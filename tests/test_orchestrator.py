"""Testes locais da proteção contra mutação pelo Reviewer."""

import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "orchestration" / "orchestrator.py"
SPEC = importlib.util.spec_from_file_location("orchestrator", MODULE_PATH)
orchestrator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = orchestrator
SPEC.loader.exec_module(orchestrator)


class WorkspaceFingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "tracked.txt").write_text("inicial\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        self.previous_root = orchestrator.ROOT
        orchestrator.ROOT = self.root

    def tearDown(self) -> None:
        orchestrator.ROOT = self.previous_root
        self.temporary_directory.cleanup()

    def test_detecta_conteudo_untracked_e_estados_tracked_e_staged(self) -> None:
        original = orchestrator.workspace_fingerprint()

        untracked = self.root / "temporario.txt"
        untracked.write_text("primeira versão\n", encoding="utf-8")
        with_untracked = orchestrator.workspace_fingerprint()
        self.assertNotEqual(original, with_untracked)

        untracked.write_text("segunda versão\n", encoding="utf-8")
        self.assertNotEqual(with_untracked, orchestrator.workspace_fingerprint())

        (self.root / "tracked.txt").write_text("alterado sem stage\n", encoding="utf-8")
        with_worktree_change = orchestrator.workspace_fingerprint()
        self.assertNotEqual(original, with_worktree_change)

        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        self.assertNotEqual(with_worktree_change, orchestrator.workspace_fingerprint())


def resposta_reviewer_automatica(
    decisao: str,
    handoff: str = "Trabalho da rodada.",
    run_id: str = "mira-teste",
) -> str:
    return f"""MIRA_HANDOFF_BEGIN
MIRA_RUN_ID: {run_id}

{handoff}
MIRA_HANDOFF_END
MIRA_RUN_ID: {run_id}
MIRA_DECISION: {decisao}"""


def resposta_reviewer_final(run_id: str = "mira-teste") -> str:
    return f"MIRA_RUN_ID: {run_id}\nMIRA_DECISION: DONE"


def evidencia_implementer(run_id: str = "mira-teste", decisao: str | None = None) -> str:
    marcador = f"\nMIRA_DECISION: {decisao}" if decisao is not None else ""
    return f"Resultado do Implementer.\nMIRA_RUN_ID: {run_id}{marcador}"


class ReviewerLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.previous_root = orchestrator.ROOT
        self.previous_logs_root = orchestrator.LOGS_ROOT
        orchestrator.ROOT = Path(self.temporary_directory.name)
        orchestrator.LOGS_ROOT = orchestrator.ROOT / "orchestration" / "logs"

    def tearDown(self) -> None:
        orchestrator.ROOT = self.previous_root
        orchestrator.LOGS_ROOT = self.previous_logs_root
        self.temporary_directory.cleanup()

    def executar(self, turn, *argumentos: str) -> int:
        self.prompts: list[tuple[str, str]] = []

        def registrar_turn(agent: str, prompt: str) -> str:
            self.prompts.append((agent, prompt))
            return turn(agent, prompt)

        with (
            patch.object(orchestrator, "preflight"),
            patch.object(orchestrator, "workspace_fingerprint", return_value="imutável"),
            patch.object(orchestrator, "run_agent_turn", side_effect=registrar_turn),
            patch.object(orchestrator.uuid, "uuid4", return_value="teste"),
            patch.object(sys, "argv", ["orchestrator.py", *argumentos]),
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            return orchestrator.main()

    def resultado_final(self) -> str:
        return (orchestrator.LOGS_ROOT / "mira-teste" / "final-result.txt").read_text(
            encoding="utf-8"
        )

    def test_reviewer_implementer_reviewer_done(self) -> None:
        chamadas: list[str] = []
        resultado_implementer = evidencia_implementer()
        respostas = iter(
            [
                resposta_reviewer_automatica("CONTINUE"),
                resultado_implementer,
                resposta_reviewer_final(),
            ]
        )

        def turn(agent: str, _prompt: str) -> str:
            chamadas.append(agent)
            return next(respostas)

        self.assertEqual(self.executar(turn, "objetivo"), 0)
        self.assertEqual(chamadas, ["reviewer", "implementer", "reviewer"])
        agente, prompt_revisao_seguinte = self.prompts[2]
        self.assertEqual(agente, orchestrator.REVIEWER)
        self.assertIn(
            f"--- INÍCIO DO RESULTADO ---\n{resultado_implementer}\n"
            "--- FIM DO RESULTADO ---",
            prompt_revisao_seguinte,
        )
        self.assertIn("Resultado final: DONE", self.resultado_final())

    def test_fix_required_retorna_ao_reviewer_antes_de_done(self) -> None:
        chamadas: list[str] = []
        primeiro_handoff = "Corrigir a primeira evidência."
        segundo_handoff = "Corrigir a regressão restante."
        respostas = iter(
            [
                resposta_reviewer_automatica("CONTINUE", primeiro_handoff),
                evidencia_implementer(),
                resposta_reviewer_automatica("FIX_REQUIRED", segundo_handoff),
                evidencia_implementer(),
                resposta_reviewer_final(),
            ]
        )

        def turn(agent: str, _prompt: str) -> str:
            chamadas.append(agent)
            return next(respostas)

        self.assertEqual(self.executar(turn, "objetivo"), 0)
        self.assertEqual(
            chamadas,
            ["reviewer", "implementer", "reviewer", "implementer", "reviewer"],
        )
        self.assertEqual(
            self.prompts[1],
            (
                orchestrator.IMPLEMENTER,
                orchestrator.implementer_prompt(
                    f"MIRA_RUN_ID: mira-teste\n\n{primeiro_handoff}",
                    "mira-teste",
                ),
            ),
        )
        self.assertEqual(
            self.prompts[3],
            (
                orchestrator.IMPLEMENTER,
                orchestrator.implementer_prompt(
                    f"MIRA_RUN_ID: mira-teste\n\n{segundo_handoff}",
                    "mira-teste",
                ),
            ),
        )

    def test_decisao_done_do_implementer_e_ignorada(self) -> None:
        chamadas: list[str] = []
        respostas = iter(
            [
                resposta_reviewer_automatica("CONTINUE"),
                evidencia_implementer(decisao="DONE"),
                resposta_reviewer_final(),
            ]
        )

        def turn(agent: str, _prompt: str) -> str:
            chamadas.append(agent)
            return next(respostas)

        self.assertEqual(self.executar(turn, "objetivo"), 0)
        self.assertEqual(chamadas, ["reviewer", "implementer", "reviewer"])

    def test_limite_padrao_dez_interrompe_fluxo_nao_convergente(self) -> None:
        chamadas: list[str] = []

        def turn(agent: str, _prompt: str) -> str:
            chamadas.append(agent)
            if agent == orchestrator.REVIEWER:
                return resposta_reviewer_automatica("CONTINUE")
            return evidencia_implementer()

        self.assertEqual(orchestrator.DEFAULT_MAX_ROUNDS, 10)
        self.assertEqual(self.executar(turn, "objetivo"), 2)
        self.assertEqual(chamadas.count(orchestrator.REVIEWER), 10)
        self.assertEqual(chamadas.count(orchestrator.IMPLEMENTER), 10)
        self.assertIn("Limite de rodadas atingido: 10", self.resultado_final())
        self.assertIn("Revisão humana necessária.", self.resultado_final())


if __name__ == "__main__":
    unittest.main()
