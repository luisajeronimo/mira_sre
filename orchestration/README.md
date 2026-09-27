# Orquestração de agentes

## Objetivo

`orchestrator.py` executa o ciclo Reviewer → Implementer → Reviewer. Ele só
transporta objetivos, handoffs e resultados: não contém regras de negócio do
MIRA, não faz push, archive nem operações remotas.

## Arquitetura e pré-requisitos

O processo exige Python 3, a CLI `herdr` e os agentes Herdr `reviewer` e
`implementer` configurados. Antes de cada execução, o orquestrador confirma os
dois agentes, gera um `MIRA_RUN_ID` exclusivo e interpreta somente marcadores
associados a ele. O Reviewer decide e revisa independentemente; o Implementer
executa apenas o handoff recebido.

## Execução

Forneça exatamente uma fonte de objetivo:

```bash
python3 orchestration/orchestrator.py "objetivo"
python3 orchestration/orchestrator.py --file caminho/do/objetivo.txt
```

O máximo padrão é cinco rodadas; altere-o com `--max-rounds`:

```bash
python3 orchestration/orchestrator.py --max-rounds 3 "objetivo"
```

`CONTINUE` e `FIX_REQUIRED` levam o handoff ao Implementer. `DONE` encerra o
fluxo. `HUMAN_DECISION_REQUIRED`, `READY_FOR_PUSH` e `READY_FOR_ARCHIVE` são
gates humanos e encerram sem executar a operação correspondente.

## Logs

Cada execução grava `objective.txt`, logs do Reviewer e Implementer por rodada
e `final-result.txt` em `orchestration/logs/<run-id>/`. Esses logs são locais e
ignorados pelo Git.
