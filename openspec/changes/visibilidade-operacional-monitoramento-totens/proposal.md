# Proposal: Visibilidade operacional do monitoramento de Totens

## Why

A página `/monitoramento` mostra apenas totais e o estado atual de cada Totem, sem tornar visíveis a telemetria, as transições de disponibilidade e os incidentes já persistidos pelo Xano. Para a demonstração acadêmica, é necessário tornar a evolução individual observável sem antecipar os indicadores consolidados da Diretoria.

## What Changes

- Evoluir a consulta dedicada `GET /monitoramento/ativos` para retornar, por Totem, Loja, estado persistido, data/hora da última telemetria e data/hora da última transição de disponibilidade.
- Adicionar uma única consulta dedicada de detalhe do Totem selecionado, limitada a até 10 telemetrias, 10 transições e 10 incidentes automáticos de heartbeat, sempre do mais recente para o mais antigo.
- Evoluir `/monitoramento` para uma composição desktop master-detail: listagem com resumo operacional e painel do Totem selecionado na própria rota.
- Exibir os valores reais da última telemetria e o histórico recente disponível, distinguindo eventos de disponibilidade de incidentes automáticos e permitindo abrir o detalhe de chamado já existente.
- Manter os totais atuais como contagem do estado persistido pelo Xano e apresentar vazios reais quando não houver telemetria, transições ou incidentes.
- Preservar as regras consolidadas: o Xano decide Online/Offline; o Fiscal apenas dispara a verificação quando em execução; não haverá cálculo de disponibilidade no frontend, dados inventados, polling, métricas derivadas, mudanças no Fiscal, Simulator, tabelas ou regras de heartbeat.
- Manter a autorização global de monitoramento já consolidada para Técnico, Diretoria e Administrador; esta change não altera permissões nem o contrato genérico de telemetria.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `monitoramento-disponibilidade-totens`: acrescentar a leitura operacional dos fatos de telemetria, disponibilidade e incidentes já persistidos, além da apresentação por Totem em `/monitoramento`.

## Impact

- **Frontend Reflex:** estado, cliente e página de `/monitoramento`, reutilizando a casca, cards, tabela/listagem, badges, callouts e navegação já existentes em desktop.
- **Xano:** função e endpoint dedicados de listagem de monitoramento e um único contrato de detalhe somente de leitura, consultando `ativos_referencia`, `telemetria_equipamentos`, `historico_disponibilidade_totens` e `chamados` com queries simples compatíveis com o plano Free.
- **Chamados:** o painel apenas lista incidentes automáticos de heartbeat realmente registrados e encaminha ao detalhe existente; não cria relação causal entre um evento de disponibilidade e um chamado.
- **Fora do escopo:** dashboards executivos, gráficos, percentuais de disponibilidade, MTTD, MTTR, duração calculada, SLA, tendências, filtros avançados, paginação, persistência nova, backfill, logs ou saúde do Fiscal.

## Decisões humanas pendentes

Nenhuma para iniciar o Apply: os limites de 10 itens e o escopo funcional estão aprovados. A apresentação conserva os valores numéricos de telemetria recebidos e acrescenta somente sufixos de apresentação: `%` para CPU e memória, `°C` para temperatura e `minutos` para o limite de heartbeat. Esses sufixos não aplicam conversão, arredondamento, cálculo, regra de precisão ou indicador de saúde adicional.
