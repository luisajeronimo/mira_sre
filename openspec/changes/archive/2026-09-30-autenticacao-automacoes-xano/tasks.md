## 1. Confirmação e configuração segura

- [x] 1.1 Confirmar por documentação oficial e/ou Xano Developer MCP que o mecanismo selecionado para armazenar e obter no servidor `MIRA_FISCAL_AUTOMATION_KEY` e `MIRA_SIMULATOR_AUTOMATION_KEY` está disponível no plano Free, e que endpoints/XanoScript acessam os headers `X-MIRA-Fiscal-Key` e `X-MIRA-Simulator-Key` conforme o design; parar com `HUMAN_DECISION_REQUIRED` se qualquer capacidade exigir recurso pago ou não puder ser confirmada, sem alternativa automática ou sugestão de upgrade.
- [x] 1.2 Documentar `MIRA_FISCAL_AUTOMATION_KEY` e `MIRA_SIMULATOR_AUTOMATION_KEY` em `.env.example` com valores vazios, preparar valores reais exclusivamente no ambiente apropriado e verificar que nenhuma saída, log ou resposta registra headers ou segredos.
- [x] 1.3 Avaliar os limites Free para Fiscal a cada cinco minutos e para cada ciclo do Simulator iniciado a cada cinco minutos, considerando os 15 Totens documentados em `.env.example`; validar envio sequencial a cada três segundos entre POSTs, duração do ciclo de alguns segundos, no máximo sete POSTs do Simulator por vinte segundos, ou oito com eventual disparo do Fiscal, e cadência média de 15 POSTs mais um GET por cinco minutos, sem reserva contra tráfego externo, fila, scheduler externo, rate limiter ou infraestrutura nova. Validar que ciclo e espaçamento podem ser sobrescritos por configuração de ambiente sem alterar a regra Xano de Offline pela última telemetria superior a quinze minutos, timeout que o Python não calcula.

## 2. Proteção do Fiscal

- [x] 2.1 Implementar no Xano o guard de `GET /verificar-falhas`, que compara `X-MIRA-Fiscal-Key` a `MIRA_FISCAL_AUTOMATION_KEY` antes de qualquer lógica de heartbeat ou leitura operacional.
- [x] 2.2 Validar credencial Fiscal ausente, inválida, segredo Xano ausente e válida: HTTP 401 uniforme com o corpo público exato `{"error":"Não autenticado."}` e sem outros campos, falha fechada sem comparação permissiva com vazio/nulo, ausência de leitura, heartbeat, disponibilidade ou incidente antes da rejeição e preservação do contrato bem-sucedido.
- [x] 2.3 Atualizar o Fiscal para exigir `MIRA_FISCAL_AUTOMATION_KEY`, enviar somente `X-MIRA-Fiscal-Key`, usar default de cinco minutos e falhar explicitamente antes de qualquer chamada anônima.

## 3. Proteção do Simulator

- [x] 3.1 Implementar no Xano o guard de `POST /telemetria_equipamentos`, que compara `X-MIRA-Simulator-Key` a `MIRA_SIMULATOR_AUTOMATION_KEY` antes de persistência ou lógica operacional.
- [x] 3.2 Validar credencial Simulator ausente, inválida, segredo Xano ausente e válida: HTTP 401 uniforme com o corpo público exato `{"error":"Não autenticado."}` e sem outros campos, falha fechada sem comparação permissiva com vazio/nulo, ausência de persistência, heartbeat, disponibilidade ou incidente antes da rejeição e preservação de URL, método e payload bem-sucedidos.
- [x] 3.3 Atualizar o Simulator para exigir `MIRA_SIMULATOR_AUTOMATION_KEY`, enviar somente `X-MIRA-Simulator-Key`, iniciar ciclos operacionais a cada cinco minutos, enviar os 15 Totens sequencialmente com três segundos entre POSTs e permitir sobrescrita de ciclo e espaçamento por configuração de ambiente, sem alterar o timeout de heartbeat no Xano.

## 4. Limites de finalidade e remoção de diagnóstico

- [x] 4.1 Testar que a chave do Fiscal não autoriza telemetria, a chave do Simulator não autoriza heartbeat e nenhuma chave autoriza endpoints humanos.
- [x] 4.2 Inventariar código, documentação, testes, Makefile e scripts consumidores de `Fiscal --telemetria`; ajustar ou confirmar ausência de cada consumidor, remover o modo sem substituto e cobrir sua ausência no contrato de linha de comando.
- [x] 4.3 Validar ausência de `MIRA_FISCAL_AUTOMATION_KEY` e `MIRA_SIMULATOR_AUTOMATION_KEY` em ambos os scripts, falha explícita antes de chamada anônima e ausência de segredo em logs, exceções e respostas.

## 5. Regressão e validação final

- [x] 5.1 Executar testes Python para headers, variáveis ausentes, credenciais ausentes/inválidas/válidas, privilégios cruzados, periodicidades e ausência de vazamento.
- [x] 5.2 Executar regressões de URL, método e payload, heartbeat/Offline exclusivamente por última telemetria acima de quinze minutos, disponibilidade, deduplicação e incidentes automáticos; comprovar que três ciclos esperados de cinco minutos antecedem aproximadamente o timeout e que o Fiscal apenas dispara a verificação, sem calcular ou decidir a regra.
- [x] 5.3 Validar todo XanoScript alterado com Xano Developer MCP e executar `xano workspace push --dry-run` somente no futuro Apply autorizado, revisando o diff completo antes de qualquer push.
- [x] 5.4 Executar `openspec validate autenticacao-automacoes-xano --strict`, `git diff --check` e registrar resultados, bloqueios e limitações reais.
