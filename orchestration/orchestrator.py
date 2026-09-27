#!/usr/bin/env python3
"""Orquestra ciclos Reviewer → Implementer sem regras de negócio do MIRA."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS_ROOT = ROOT / "orchestration" / "logs"
REVIEWER, IMPLEMENTER = "reviewer", "implementer"
DEFAULT_MAX_ROUNDS, TIMEOUT_MS = 5, 300_000
AUTOMATIC = frozenset({"CONTINUE", "FIX_REQUIRED"})
HUMAN_GATES = frozenset({"HUMAN_DECISION_REQUIRED", "READY_FOR_PUSH", "READY_FOR_ARCHIVE"})
TERMINAL = frozenset({"DONE"})
VALID_DECISIONS = AUTOMATIC | HUMAN_GATES | TERMINAL


class OrchestrationError(RuntimeError):
    """Falha de protocolo, dependência ou execução."""


@dataclass(frozen=True)
class ReviewerResponse:
    decision: str
    handoff: str | None


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    except FileNotFoundError as error:
        raise OrchestrationError(f"Comando indisponível: {args[0]}.") from error


def command_error(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout or "sem detalhes").strip()


def preflight() -> None:
    """Exige que os dois agentes configurados estejam disponíveis."""
    failures = []
    for agent in (REVIEWER, IMPLEMENTER):
        result = run_command(["herdr", "agent", "get", agent])
        if result.returncode:
            failures.append(f"{agent}: {command_error(result)}")
            continue
        try:
            status = json.loads(result.stdout)["result"]["agent"]["agent_status"]
        except (KeyError, TypeError, ValueError):
            failures.append(f"{agent}: resposta do Herdr sem status válido")
            continue
        if status == "blocked":
            failures.append(f"{agent}: está bloqueado")
    if failures:
        raise OrchestrationError(
            "Preflight falhou: agente(s) Herdr indisponível(is).\n"
            + "\n".join(f"- {failure}" for failure in failures)
        )


def prompt_agent(agent: str, prompt: str) -> None:
    result = run_command([
        "herdr", "agent", "prompt", agent, prompt, "--wait", "--until", "idle",
        "--until", "done", "--timeout", str(TIMEOUT_MS),
    ])
    if result.returncode:
        raise OrchestrationError(f"Erro ao executar {agent}: {command_error(result)}")


def read_agent(agent: str) -> str:
    result = run_command([
        "herdr", "agent", "read", agent, "--source", "recent-unwrapped", "--lines", "400",
    ])
    if result.returncode:
        raise OrchestrationError(f"Erro ao ler {agent}: {command_error(result)}")
    return result.stdout.strip()


def run_agent_turn(agent: str, prompt: str) -> str:
    """Executa uma rodada; o RUN_ID separa a resposta do histórico residual."""
    prompt_agent(agent, prompt)
    return read_agent(agent)


def current_run_section(text: str, run_id: str) -> str:
    pattern = re.compile(rf"(?m)^\s*MIRA_RUN_ID:\s*{re.escape(run_id)}\s*$")
    matches = list(pattern.finditer(text))
    if not matches:
        raise OrchestrationError("Resposta sem MIRA_RUN_ID correspondente à execução atual.")
    return text[matches[-1].end():]


def marker_value(text: str, marker: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(marker)}:\s*(\S.*?)\s*$", text)
    return match.group(1).strip() if match else None


def extract_handoff(section: str) -> str | None:
    begin = re.search(r"(?m)^\s*MIRA_HANDOFF_BEGIN\s*$", section)
    if not begin:
        return None
    end = re.search(r"(?m)^\s*MIRA_HANDOFF_END\s*$", section[begin.end():])
    if not end:
        raise OrchestrationError("MIRA_HANDOFF_BEGIN sem MIRA_HANDOFF_END.")
    handoff = section[begin.end():begin.end() + end.start()].strip()
    if not handoff:
        raise OrchestrationError("Handoff do Reviewer vazio.")
    return handoff


def parse_reviewer_response(text: str, run_id: str) -> ReviewerResponse:
    section = current_run_section(text, run_id)
    decision = marker_value(section, "MIRA_DECISION")
    if decision not in VALID_DECISIONS:
        raise OrchestrationError(
            "MIRA_DECISION inválida ou ausente; válidas: " + ", ".join(sorted(VALID_DECISIONS))
        )
    handoff = extract_handoff(section)
    if decision in AUTOMATIC and handoff is None:
        raise OrchestrationError("Decisão automática sem handoff do RUN_ID atual.")
    if decision not in AUTOMATIC and handoff is not None:
        raise OrchestrationError("Handoff só é permitido em CONTINUE ou FIX_REQUIRED.")
    return ReviewerResponse(decision, handoff)


def save_log(run_dir: Path, name: str, content: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / name).write_text(content.rstrip() + "\n", encoding="utf-8")


def reviewer_prompt(objective: str, run_id: str, implementation: str | None) -> str:
    result_context = ""
    if implementation is not None:
        result_context = f"""
Resultado do Implementer na rodada anterior:
--- INÍCIO DO RESULTADO ---
{implementation}
--- FIM DO RESULTADO ---
Revise independentemente arquivos, diff, testes e evidências. Não implemente correções.
"""
    return f"""
Atue como MIRA Reviewer. Leia AGENTS.md, agents/mira-reviewer.md,
agents/handoff-template.md e openspec/config.yaml. Você é coordenado por um
orquestrador externo: não opere Herdr e não tente chamar o Implementer.

MIRA_RUN_ID atual: {run_id}
Objetivo:
--- INÍCIO DO OBJETIVO ---
{objective}
--- FIM DO OBJETIVO ---
{result_context}
Após o relatório, emita exatamente:
MIRA_RUN_ID: {run_id}
MIRA_DECISION: <CONTINUE | FIX_REQUIRED | HUMAN_DECISION_REQUIRED | READY_FOR_PUSH | READY_FOR_ARCHIVE | DONE>

Somente para CONTINUE ou FIX_REQUIRED, acrescente um handoff autocontido:
MIRA_HANDOFF_BEGIN
<handoff>
MIRA_HANDOFF_END
Não emita handoff para DONE ou gates humanos.
""".strip()


def implementer_prompt(handoff: str, run_id: str) -> str:
    return f"""
Atue como MIRA Implementer. Leia AGENTS.md, agents/mira-implementer.md,
agents/handoff-template.md e openspec/config.yaml. Você é coordenado por um
orquestrador externo: não opere Herdr nem coordene agentes. Execute exclusivamente
o handoff, sem ampliar escopo.

MIRA_RUN_ID atual: {run_id}
--- INÍCIO DO HANDOFF ---
{handoff}
--- FIM DO HANDOFF ---

Relate arquivos/recursos afetados, trabalho e resultado, validações executadas
com resultados, tasks com evidência e limitações. Termine com:
MIRA_RUN_ID: {run_id}
""".strip()


def parse_args() -> tuple[argparse.Namespace, str]:
    parser = argparse.ArgumentParser(description="Orquestra ciclos Reviewer → Implementer.")
    parser.add_argument("objective", nargs="?", help="objetivo da execução")
    parser.add_argument("--file", type=Path, help="arquivo UTF-8 com objetivo")
    parser.add_argument("--max-rounds", type=int, default=DEFAULT_MAX_ROUNDS,
                        help="máximo de rodadas (padrão: 5)")
    args = parser.parse_args()
    if int(args.objective is not None) + int(args.file is not None) != 1:
        parser.error("informe exatamente uma fonte: objetivo posicional ou --file.")
    if args.max_rounds < 1:
        parser.error("--max-rounds deve ser maior ou igual a 1.")
    if args.file is not None:
        try:
            objective = args.file.read_text(encoding="utf-8")
        except OSError as error:
            parser.error(f"não foi possível ler --file: {error}")
    else:
        objective = args.objective
    if not objective.strip():
        parser.error("o objetivo não pode estar vazio.")
    return args, objective.strip()


def main() -> int:
    args, objective = parse_args()
    run_id = f"mira-{uuid.uuid4()}"
    run_dir = LOGS_ROOT / run_id
    save_log(run_dir, "objective.txt", objective)
    print(f"MIRA_RUN_ID: {run_id}")
    print(f"Logs: {run_dir.relative_to(ROOT)}")
    try:
        preflight()
        implementation = None
        for round_number in range(1, args.max_rounds + 1):
            print(f"Rodada {round_number}/{args.max_rounds}: Reviewer")
            reviewer_output = run_agent_turn(
                REVIEWER, reviewer_prompt(objective, run_id, implementation)
            )
            save_log(run_dir, f"reviewer-round-{round_number:02d}.log", reviewer_output)
            response = parse_reviewer_response(reviewer_output, run_id)
            print(f"Decisão do Reviewer: {response.decision}")
            if response.decision in TERMINAL:
                final = f"Resultado final: DONE\nRodadas: {round_number}"
                save_log(run_dir, "final-result.txt", final)
                print(final)
                return 0
            if response.decision in HUMAN_GATES:
                final = f"Gate humano: {response.decision}\nRodadas: {round_number}"
                save_log(run_dir, "final-result.txt", final)
                print(final)
                return 0
            print(f"Rodada {round_number}/{args.max_rounds}: Implementer")
            implementation = run_agent_turn(
                IMPLEMENTER, implementer_prompt(response.handoff or "", run_id)
            )
            save_log(run_dir, f"implementer-round-{round_number:02d}.log", implementation)
            current_run_section(implementation, run_id)
        final = f"Limite de rodadas atingido: {args.max_rounds}\nRevisão humana necessária."
        save_log(run_dir, "final-result.txt", final)
        print(final)
        return 2
    except KeyboardInterrupt:
        final = "Execução interrompida por Ctrl+C. Nenhuma ação adicional foi enviada."
        save_log(run_dir, "final-result.txt", final)
        print(final)
        return 130
    except OrchestrationError as error:
        final = f"Falha do orquestrador: {error}"
        save_log(run_dir, "final-result.txt", final)
        print(final, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
