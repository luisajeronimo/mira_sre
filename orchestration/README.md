# Orquestração de agentes

## Objetivo

`orchestrator.py` executa o ciclo Reviewer → Implementer → Reviewer. Ele só
transporta objetivos, handoffs e resultados: não contém regras de negócio do
MIRA, não faz push, archive nem operações remotas. O Reviewer é a única
autoridade de decisão da máquina de estados.

## Arquitetura e pré-requisitos

O processo exige Python 3, a CLI `herdr` e os agentes Herdr `reviewer` e
`implementer` configurados. Antes de cada execução, o orquestrador confirma os
dois agentes, gera um `MIRA_RUN_ID` exclusivo e interpreta somente marcadores
do Reviewer associados a ele. O Reviewer decide e revisa independentemente; o
Implementer executa apenas o handoff recebido.

Antes e depois de cada rodada do Reviewer, o orquestrador calcula um
fingerprint do status, índice e conteúdo dos arquivos rastreados e não
rastreados. Se houver qualquer diferença, encerra com
`PROTOCOL_VIOLATION`, não interpreta `MIRA_DECISION` e não envia handoff ao
Implementer. Alterações que já existiam antes da rodada compõem apenas o
fingerprint inicial e não são tratadas como violação.

## Execução

Forneça exatamente uma fonte de objetivo:

```bash
python3 orchestration/orchestrator.py "objetivo"
python3 orchestration/orchestrator.py --file caminho/do/objetivo.txt
```

O máximo padrão é dez rodadas do Reviewer; altere-o com `--max-rounds`:

```bash
python3 orchestration/orchestrator.py --max-rounds 3 "objetivo"
```

Uma rodada corresponde a uma revisão do Reviewer e, em `CONTINUE` ou
`FIX_REQUIRED`, à execução subsequente do Implementer. Portanto, o limite 10
permite até dez ciclos de revisão e execução sem loop infinito.

O limite de rodadas é independente do timeout de uma execução individual de
agente. O timeout padrão é de 900 segundos (15 minutos) e pode ser alterado
somente para a execução corrente com `--agent-timeout-seconds`:

```bash
python3 orchestration/orchestrator.py --agent-timeout-seconds 1200 "objetivo"
```

Para cada handoff, o orquestrador inicia uma única execução do agente. Enquanto
ela estiver ativa e dentro desse limite, consulta periodicamente o estado e
emite progresso; não reenvia prompt, handoff nem inicia outro Implementer. Ao
atingir o limite, consulta novamente o estado e a saída recente. Se já houver
uma resposta com o `MIRA_RUN_ID` atual, ela é aproveitada normalmente. Caso
contrário, o orquestrador falha explicitamente sem matar o agente: a mensagem
identifica agente, RUN_ID, tempo e estado observado, e orienta revisar o agente
e o workspace antes de reenviar a tarefa, pois o trabalho pode continuar vivo.

`CONTINUE` e `FIX_REQUIRED` levam o handoff ao Implementer e a saída dele volta
somente como evidência para a próxima revisão. Implementer terminou não
significa objetivo terminado: seus marcadores `MIRA_DECISION`, inclusive
`DONE`, nunca abrem gates, encerram o fluxo ou controlam a máquina de estados.
Somente `DONE` emitido pelo Reviewer encerra o fluxo.
`HUMAN_DECISION_REQUIRED`, `READY_FOR_PUSH` e `READY_FOR_ARCHIVE` emitidos pelo
Reviewer são gates humanos e encerram sem executar a operação correspondente.

Em `CONTINUE` ou `FIX_REQUIRED`, o handoff deve conter o `MIRA_RUN_ID` atual
entre `MIRA_HANDOFF_BEGIN` e `MIRA_HANDOFF_END`; após o bloco, o Reviewer
repete o identificador ao emitir a decisão. O orquestrador recusa handoffs sem
esse identificador interno.

## Logs

Cada execução grava `objective.txt`, logs do Reviewer e Implementer por rodada
e `final-result.txt` em `orchestration/logs/<run-id>/`. Esses logs são locais e
ignorados pelo Git.
