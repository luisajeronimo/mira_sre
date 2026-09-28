# Handoff Reviewer → Implementer

Todo handoff automático deve iniciar dentro do seguinte envelope. O
`MIRA_RUN_ID` interno identifica a delegação ao Implementer e deve ser o da
execução atual; após `MIRA_HANDOFF_END`, o Reviewer emite novamente esse mesmo
identificador junto da decisão `CONTINUE` ou `FIX_REQUIRED`.

```text
MIRA_HANDOFF_BEGIN
MIRA_RUN_ID: <id recebido>

<conteúdo abaixo>
MIRA_HANDOFF_END

MIRA_RUN_ID: <id recebido>
MIRA_DECISION: CONTINUE | FIX_REQUIRED
```

## Change

Informar a change OpenSpec real quando existir:
`<nome-da-change>`

Para tarefas de governança, auditoria ou infraestrutura fora de uma change:

`N/A — tarefa operacional`

Nunca inventar uma change para preencher este campo.

## Fase
Explore | Propose | Apply | Pre-Push | Post-Push | Pre-Archive

Usar uma fase OpenSpec apenas quando houver uma change real.

Caso contrário:

`N/A — tarefa operacional`

## Objetivo desta rodada

Descrever apenas o objetivo imediato.

## Evidências já confirmadas

Informações que não precisam ser investigadas novamente.

## Trabalho necessário

Instruções para esta rodada.

## Restrições

Regras que não podem ser alteradas.

## Validações esperadas

Testes, diffs ou evidências necessários.

## Regra de parada

Dizer exatamente em qual condição o Implementer deve parar e devolver
o trabalho ao Reviewer.
