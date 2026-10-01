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
        self.prompts: list[tuple[str, str, str]] = []

        def registrar_turn(agent: str, prompt: str, run_id: str, **_kwargs: int) -> str:
            self.prompts.append((agent, prompt, run_id))
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
        agente, prompt_revisao_seguinte, run_id = self.prompts[2]
        self.assertEqual(agente, orchestrator.REVIEWER)
        self.assertEqual(run_id, "mira-teste")
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
            self.prompts[1][:2],
            (
                orchestrator.IMPLEMENTER,
                orchestrator.implementer_prompt(
                    f"MIRA_RUN_ID: mira-teste\n\n{primeiro_handoff}",
                    "mira-teste",
                ),
            ),
        )
        self.assertEqual(
            self.prompts[3][:2],
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
        self.assertEqual(orchestrator.DEFAULT_AGENT_TIMEOUT_SECONDS, 900)
        self.assertEqual(self.executar(turn, "objetivo"), 2)
        self.assertEqual(chamadas.count(orchestrator.REVIEWER), 10)
        self.assertEqual(chamadas.count(orchestrator.IMPLEMENTER), 10)
        self.assertIn("Limite de rodadas atingido: 10", self.resultado_final())
        self.assertIn("Revisão humana necessária.", self.resultado_final())


class AgentTurnTimeoutTests(unittest.TestCase):
    class Process:
        def __init__(self, polls_before_completion: int | None) -> None:
            self.polls_before_completion = polls_before_completion
            self.poll_count = 0
            self.returncode = 0

        def poll(self) -> int | None:
            self.poll_count += 1
            if self.polls_before_completion is None or self.poll_count <= self.polls_before_completion:
                return None
            return self.returncode

        def communicate(self) -> tuple[str, str]:
            return ("", "")

    def test_polls_uma_execucao_ativa_e_retorna_ao_reviewer(self) -> None:
        process = self.Process(polls_before_completion=2)
        output = evidencia_implementer()
        with (
            patch.object(orchestrator, "start_agent_prompt", return_value=process) as start,
            patch.object(orchestrator, "agent_status", return_value="working") as status,
            patch.object(orchestrator, "read_agent", return_value=output),
            patch.object(orchestrator.time, "monotonic", side_effect=[0, 0, 15, 30]),
            patch.object(orchestrator.time, "sleep") as sleep,
        ):
            result = orchestrator.run_agent_turn(
                orchestrator.IMPLEMENTER, "handoff", "mira-teste", timeout_seconds=900
            )

        self.assertEqual(result, output)
        start.assert_called_once_with(orchestrator.IMPLEMENTER, "handoff", 900)
        self.assertEqual(status.call_count, 2)
        self.assertEqual(sleep.call_count, 2)

    def test_timeout_nao_reenvia_execucao(self) -> None:
        process = self.Process(polls_before_completion=None)
        with (
            patch.object(orchestrator, "start_agent_prompt", return_value=process) as start,
            patch.object(orchestrator, "agent_status", return_value="working"),
            patch.object(orchestrator, "read_agent", return_value="saída sem run"),
            patch.object(orchestrator.time, "monotonic", side_effect=[0, 0, 900]),
            patch.object(orchestrator.time, "sleep"),
        ):
            with self.assertRaisesRegex(
                orchestrator.OrchestrationError,
                r"Tempo limite de 900s.*implementer.*mira-teste.*working.*pode continuar",
            ):
                orchestrator.run_agent_turn(
                    orchestrator.IMPLEMENTER, "handoff", "mira-teste", timeout_seconds=900
                )

        start.assert_called_once_with(orchestrator.IMPLEMENTER, "handoff", 900)

    def test_resultado_no_limite_e_recuperado(self) -> None:
        process = self.Process(polls_before_completion=None)
        output = evidencia_implementer()
        with (
            patch.object(orchestrator, "start_agent_prompt", return_value=process) as start,
            patch.object(orchestrator, "agent_status", return_value="working") as status,
            patch.object(orchestrator, "read_agent", return_value=output),
            patch.object(orchestrator.time, "monotonic", side_effect=[0, 0, 900]),
            patch.object(orchestrator.time, "sleep"),
        ):
            result = orchestrator.run_agent_turn(
                orchestrator.IMPLEMENTER, "handoff", "mira-teste", timeout_seconds=900
            )

        self.assertEqual(result, output)
        start.assert_called_once_with(orchestrator.IMPLEMENTER, "handoff", 900)
        self.assertEqual(status.call_count, 2)

    def test_timeout_preserva_decisao_do_implementer_como_evidencia(self) -> None:
        output = evidencia_implementer(decisao="DONE")
        process = self.Process(polls_before_completion=None)
        with (
            patch.object(orchestrator, "start_agent_prompt", return_value=process),
            patch.object(orchestrator, "agent_status", return_value="working"),
            patch.object(orchestrator, "read_agent", return_value=output),
            patch.object(orchestrator.time, "monotonic", side_effect=[0, 0, 900]),
            patch.object(orchestrator.time, "sleep"),
        ):
            self.assertEqual(
                orchestrator.run_agent_turn(
                    orchestrator.IMPLEMENTER, "handoff", "mira-teste", timeout_seconds=900
                ),
                output,
            )


class IntegratedAgentTimeoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.previous_root = orchestrator.ROOT
        self.previous_logs_root = orchestrator.LOGS_ROOT
        orchestrator.ROOT = Path(self.temporary_directory.name)
        orchestrator.LOGS_ROOT = orchestrator.ROOT / "orchestration" / "logs"
        self.prompts: list[tuple[str, str, str]] = []
        self.calls: list[str] = []

    def tearDown(self) -> None:
        orchestrator.ROOT = self.previous_root
        orchestrator.LOGS_ROOT = self.previous_logs_root
        self.temporary_directory.cleanup()

    def executar_main_com_implementer_real(
        self,
        reviewer_outputs: list[str],
        process: AgentTurnTimeoutTests.Process,
        implementation_output: str,
        monotonic_values: list[int],
    ) -> tuple[int, object]:
        original_run_agent_turn = orchestrator.run_agent_turn
        responses = iter(reviewer_outputs)

        def executar_turn(agent: str, prompt: str, run_id: str, **kwargs: int) -> str:
            self.calls.append(agent)
            self.prompts.append((agent, prompt, run_id))
            if agent == orchestrator.REVIEWER:
                return next(responses)
            return original_run_agent_turn(agent, prompt, run_id, **kwargs)

        with (
            patch.object(orchestrator, "preflight"),
            patch.object(orchestrator, "workspace_fingerprint", return_value="imutável"),
            patch.object(orchestrator, "run_agent_turn", side_effect=executar_turn),
            patch.object(orchestrator, "start_agent_prompt", return_value=process) as start,
            patch.object(orchestrator, "agent_status", return_value="working"),
            patch.object(orchestrator, "read_agent", return_value=implementation_output),
            patch.object(orchestrator.time, "monotonic", side_effect=monotonic_values),
            patch.object(orchestrator.time, "sleep"),
            patch.object(orchestrator.uuid, "uuid4", return_value="teste"),
            patch.object(sys, "argv", ["orchestrator.py", "objetivo"]),
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            return orchestrator.main(), start

    def test_main_retorna_ao_reviewer_apos_polls_do_implementer(self) -> None:
        report = evidencia_implementer()
        returncode, start = self.executar_main_com_implementer_real(
            [resposta_reviewer_automatica("CONTINUE"), resposta_reviewer_final()],
            AgentTurnTimeoutTests.Process(polls_before_completion=2),
            report,
            [0, 0, 15],
        )

        self.assertEqual(returncode, 0)
        self.assertEqual(
            self.calls,
            [orchestrator.REVIEWER, orchestrator.IMPLEMENTER, orchestrator.REVIEWER],
        )
        start.assert_called_once()
        self.assertIn(report, self.prompts[2][1])
        self.assertIn("Resultado final: DONE", self._resultado_final())

    def test_main_recupera_resultado_no_limite_como_evidencia(self) -> None:
        report = evidencia_implementer(decisao="DONE")
        returncode, start = self.executar_main_com_implementer_real(
            [resposta_reviewer_automatica("CONTINUE"), resposta_reviewer_final()],
            AgentTurnTimeoutTests.Process(polls_before_completion=None),
            report,
            [0, 0, 900],
        )

        self.assertEqual(returncode, 0)
        self.assertEqual(
            self.calls,
            [orchestrator.REVIEWER, orchestrator.IMPLEMENTER, orchestrator.REVIEWER],
        )
        start.assert_called_once()
        self.assertIn(report, self.prompts[2][1])
        self.assertIn("Resultado final: DONE", self._resultado_final())

    def test_main_timeout_real_para_sem_reenviar_handoff(self) -> None:
        returncode, start = self.executar_main_com_implementer_real(
            [resposta_reviewer_automatica("CONTINUE")],
            AgentTurnTimeoutTests.Process(polls_before_completion=None),
            "saída sem o RUN_ID atual",
            [0, 0, 900],
        )

        self.assertEqual(returncode, 1)
        self.assertEqual(self.calls, [orchestrator.REVIEWER, orchestrator.IMPLEMENTER])
        start.assert_called_once()
        final = self._resultado_final()
        self.assertIn("implementer", final)
        self.assertIn("MIRA_RUN_ID: mira-teste", final)
        self.assertIn("estado observado: working", final)
        self.assertIn("pode continuar em execução", final)
        self.assertIn("Não reenvie a tarefa", final)
        self.assertNotIn("DONE", final)

    def _resultado_final(self) -> str:
        return (orchestrator.LOGS_ROOT / "mira-teste" / "final-result.txt").read_text(
            encoding="utf-8"
        )


if __name__ == "__main__":
    unittest.main()
