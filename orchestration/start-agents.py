#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "orchestration" / "herdr.local.json"

REVIEWER = "reviewer"
IMPLEMENTER = "implementer"

TIMEOUT_MS = 120_000


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(
            "Configuração local não encontrada:\n"
            f"  {CONFIG_PATH}\n\n"
            "Crie o arquivo com:\n\n"
            '{\n'
            '  "reviewer_pane": "w1:p1",\n'
            '  "implementer_pane": "w1:p2"\n'
            '}\n'
        )
        sys.exit(1)

    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def get_agent(name: str) -> dict | None:
    result = run(["herdr", "agent", "get", name])

    if result.returncode != 0:
        return None

    try:
        payload = json.loads(result.stdout)
        return payload.get("result", {}).get("agent")
    except json.JSONDecodeError:
        return None


def start_agent(name: str, pane: str) -> None:
    print(f"Iniciando {name} em {pane}...")

    result = run(
        [
            "herdr",
            "agent",
            "start",
            name,
            "--kind",
            "codex",
            "--pane",
            pane,
        ]
    )

    if result.returncode != 0:
        print(f"Falha ao iniciar {name}:")
        print(result.stderr or result.stdout)
        sys.exit(1)


def ensure_agent(name: str, pane: str) -> None:
    agent = get_agent(name)

    if agent:
        print(f"{name}: já existe.")
        return

    start_agent(name, pane)


def prompt_agent(name: str, prompt: str) -> None:
    result = run(
        [
            "herdr",
            "agent",
            "prompt",
            name,
            prompt,
            "--wait",
            "--until",
            "idle",
            "--until",
            "done",
            "--timeout",
            str(TIMEOUT_MS),
        ]
    )

    if result.returncode != 0:
        print(f"Falha no bootstrap de {name}:")
        print(result.stderr or result.stdout)
        sys.exit(1)


def bootstrap_reviewer() -> None:
    prompt = """
Inicialização da sessão MIRA.

Atue como MIRA Reviewer.

Leia integralmente:
- AGENTS.md
- agents/README.md
- agents/mira-reviewer.md
- agents/handoff-template.md
- openspec/config.yaml

Você é coordenado exclusivamente pelo orquestrador externo em
orchestration/orchestrator.py.

Não opere Herdr diretamente.
Não coordene agentes diretamente.
Não implemente as correções que identificar.

Confirme que compreendeu o papel e aguarde objetivos enviados pelo orquestrador.
""".strip()

    print("Inicializando contexto do Reviewer...")
    prompt_agent(REVIEWER, prompt)


def bootstrap_implementer() -> None:
    prompt = """
Inicialização da sessão MIRA.

Atue como MIRA Implementer.

Leia integralmente:
- AGENTS.md
- agents/README.md
- agents/mira-implementer.md
- agents/handoff-template.md
- openspec/config.yaml

Execute somente handoffs recebidos pelo fluxo de orquestração.

Não coordene outros agentes.
Não opere Herdr diretamente.
Não amplie o escopo recebido.
Não tome decisões de negócio não especificadas.

Confirme que compreendeu o papel e aguarde trabalho.
""".strip()

    print("Inicializando contexto do Implementer...")
    prompt_agent(IMPLEMENTER, prompt)


def main() -> None:
    print("=== MIRA Agent Bootstrap ===\n")

    config = load_config()

    ensure_agent(
        REVIEWER,
        config["reviewer_pane"],
    )

    ensure_agent(
        IMPLEMENTER,
        config["implementer_pane"],
    )

    bootstrap_reviewer()
    bootstrap_implementer()

    reviewer = get_agent(REVIEWER)
    implementer = get_agent(IMPLEMENTER)

    print("\n=== Estado final ===")

    print(
        "reviewer:",
        reviewer.get("status", "desconhecido")
        if reviewer else "não encontrado",
    )

    print(
        "implementer:",
        implementer.get("status", "desconhecido")
        if implementer else "não encontrado",
    )

    print("\n✅ Agentes MIRA inicializados.")
    print(
        '\nAgora execute:\n'
        'python3 orchestration/orchestrator.py "seu objetivo"'
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBootstrap cancelado.")
        sys.exit(130)
