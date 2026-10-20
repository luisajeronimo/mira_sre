# Tasks

## 1. Contratos Xano de leitura

- [x] 1.1 Evoluir a função e `GET /monitoramento/ativos` com Loja, última telemetria e última transição, preservando `items`, o estado persistido e a autorização existente; verificar cenários Xano de resumo completo e de timestamps ausentes.
- [x] 1.2 Criar a função e `GET /monitoramento/ativos/{ativos_referencia_id}` para o detalhe limitado e ordenado de telemetrias, transições e incidentes automáticos de heartbeat; verificar no Xano detalhe completo, coleções vazias e Totem inexistente.
- [x] 1.3 Executar os testes unitários Xano dos novos contratos, confirmando que usam somente leituras e estruturas disponíveis no plano Free.
- [x] 1.4 Caso uma sincronização Xano seja autorizada no Apply, validar os XanoScripts pelo Xano Developer MCP, executar `xano workspace push --dry-run` e revisar o diff completo antes do push; após o push autorizado, executar novo dry-run e confirmar que não restaram alterações não aprovadas.

## 2. Cliente e estado Reflex

- [x] 2.1 Evoluir os DTOs e o cliente de Service Desk para os dois contratos de monitoramento, incluindo Loja, timestamps opcionais e coleções do detalhe; adicionar testes `httpx.MockTransport` para o mapeamento completo, limites recebidos e ausências reais.
- [x] 2.2 Implementar no `MonitoramentoState` a seleção e a carga sob demanda do detalhe, reutilizando o tratamento de erro existente; adicionar testes focados para seleção, ausência de telemetria/transição/incidente e falha de consulta sem dados fabricados.

## 3. Interface operacional desktop

- [x] 3.1 Evoluir `/monitoramento` para master-detail desktop com os três indicadores atuais, resumo de cada Totem e painel na mesma rota; verificar visualmente que a seleção mantém `/monitoramento` e que os incidentes apontam para `/chamados/{id}`.
- [x] 3.2 Apresentar no painel os valores numéricos recebidos de CPU, memória e temperatura com os sufixos de apresentação aprovados (`%` para CPU/memória e `°C` para temperatura), `status_rede`, telemetrias, eventos de disponibilidade com `heartbeat_limite_minutos` como `X minutos` e incidentes em seções independentes; verificar estados vazios e de erro, sem conversão, arredondamento, indicador derivado ou informação sobre execução do Fiscal.

## 4. Verificação integrada

- [x] 4.1 Executar os testes Python focados de cliente e estado de monitoramento e a suíte definida pelo projeto; registrar separadamente qualquer validação bloqueada por ambiente.
- [x] 4.2 Executar `.venv/bin/reflex compile --dry`, `openspec validate visibilidade-operacional-monitoramento-totens --strict --no-interactive` e `git diff --check`; confirmar que não há alteração em Fiscal, Simulator, schemas, dados ou regras de heartbeat.
