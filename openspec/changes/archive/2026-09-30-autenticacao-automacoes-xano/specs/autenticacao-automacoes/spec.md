## Purpose

Proteger as automações Fiscal e Simulator por credenciais técnicas distintas, preservando os contratos funcionais já consolidados após autenticação válida.

## ADDED Requirements

### Requirement: Fiscal exige credencial técnica de finalidade antes do heartbeat

O sistema DEVE (MUST) exigir o header `X-MIRA-Fiscal-Key` em `GET /verificar-falhas` e compará-lo exclusivamente ao segredo lógico Xano `MIRA_FISCAL_AUTOMATION_KEY` antes de qualquer leitura operacional ou lógica de heartbeat. O Fiscal DEVE (MUST) obter o valor da variável Python `MIRA_FISCAL_AUTOMATION_KEY` e NÃO DEVE (MUST NOT) enviar requisição anônima quando ela estiver ausente.

#### Scenario: Chave Fiscal ausente ou inválida
- **WHEN** `GET /verificar-falhas` não contém `X-MIRA-Fiscal-Key` ou contém valor inválido
- **THEN** o Xano responde HTTP 401 com o corpo público exato `{"error":"Não autenticado."}`, sem outros campos, segredo esperado, configuração, existência parcial ou dados operacionais
- **AND** não executa leitura, persistência, cálculo de heartbeat, alteração de disponibilidade ou incidente antes da rejeição

#### Scenario: Segredo Fiscal Xano ausente
- **WHEN** `MIRA_FISCAL_AUTOMATION_KEY` não está configurado no Xano
- **THEN** o Xano responde HTTP 401 com o mesmo corpo público exato `{"error":"Não autenticado."}` da credencial ausente ou inválida, sem outros campos
- **AND** falha fechado sem comparar permissivamente com valor vazio ou nulo

#### Scenario: Chave Fiscal válida
- **WHEN** o Fiscal envia `X-MIRA-Fiscal-Key` com o valor configurado para sua finalidade
- **THEN** o endpoint executa o contrato funcional atual sem mudança de URL ou método

#### Scenario: Variável do Fiscal ausente
- **WHEN** o processo Fiscal não possui sua variável de ambiente de credencial
- **THEN** ele falha explicitamente antes de enviar chamada anônima

### Requirement: Simulator exige credencial técnica de finalidade antes de telemetria

O sistema DEVE (MUST) exigir o header `X-MIRA-Simulator-Key` em `POST /telemetria_equipamentos` e compará-lo exclusivamente ao segredo lógico Xano `MIRA_SIMULATOR_AUTOMATION_KEY` antes de qualquer persistência ou lógica operacional. O Simulator DEVE (MUST) obter o valor da variável Python `MIRA_SIMULATOR_AUTOMATION_KEY` e NÃO DEVE (MUST NOT) enviar requisição anônima quando ela estiver ausente.

#### Scenario: Chave Simulator ausente ou inválida
- **WHEN** `POST /telemetria_equipamentos` não contém `X-MIRA-Simulator-Key` ou contém valor inválido
- **THEN** o Xano responde HTTP 401 com o corpo público exato `{"error":"Não autenticado."}`, sem outros campos, segredo esperado, configuração, existência parcial ou dados operacionais
- **AND** não executa leitura, persistência, cálculo de heartbeat, alteração de disponibilidade ou incidente antes da rejeição

#### Scenario: Segredo Simulator Xano ausente
- **WHEN** `MIRA_SIMULATOR_AUTOMATION_KEY` não está configurado no Xano
- **THEN** o Xano responde HTTP 401 com o mesmo corpo público exato `{"error":"Não autenticado."}` da credencial ausente ou inválida, sem outros campos
- **AND** falha fechado sem comparar permissivamente com valor vazio ou nulo

#### Scenario: Chave Simulator válida
- **WHEN** o Simulator envia `X-MIRA-Simulator-Key` com o valor configurado para sua finalidade
- **THEN** o endpoint preserva URL, método e payload funcional bem-sucedido atuais

#### Scenario: Variável do Simulator ausente
- **WHEN** o processo Simulator não possui sua variável de ambiente de credencial
- **THEN** ele falha explicitamente antes de enviar chamada anônima

### Requirement: Credenciais técnicas são isoladas e não autenticam humanos

O sistema DEVE (MUST) manter as duas credenciais técnicas separadas por finalidade. A credencial do Fiscal NÃO DEVE (MUST NOT) autorizar telemetria, a credencial do Simulator NÃO DEVE (MUST NOT) autorizar heartbeat e todas as credenciais técnicas NÃO DEVEM (MUST NOT) autorizar endpoints humanos.

#### Scenario: Uso cruzado de credencial
- **WHEN** uma automação apresenta a credencial técnica da outra finalidade
- **THEN** o endpoint rejeita a requisição sem executar efeito parcial

#### Scenario: Chave técnica em endpoint humano
- **WHEN** um cliente apresenta qualquer chave técnica a um endpoint humano
- **THEN** a chave não concede sessão, perfil ou autorização humana

### Requirement: Fiscal remove diagnóstico de telemetria

O Fiscal NÃO DEVE (MUST NOT) oferecer o modo `--telemetria`.

#### Scenario: Invocação do diagnóstico removido
- **WHEN** o Fiscal é iniciado com `--telemetria`
- **THEN** o modo não é aceito e nenhuma substituição de diagnóstico é iniciada por esta capacidade

#### Scenario: Consumidores do diagnóstico removido
- **WHEN** a remoção de `--telemetria` é aplicada
- **THEN** código, documentação, testes, Makefile e scripts consumidores são inventariados e cada consumidor é ajustado ou tem sua ausência confirmada
- **AND** nenhuma ferramenta substituta é criada por esta capacidade

### Requirement: Periodicidades preservam a regra de heartbeat do Xano

O Fiscal DEVE (MUST) usar periodicidade operacional padrão de cinco minutos. O Simulator DEVE (MUST) iniciar um ciclo operacional de telemetria a cada cinco minutos; os cinco minutos NÃO DEVEM (MUST NOT) ser intervalo entre Totens. Dentro de cada ciclo, o Simulator DEVE (MUST) enviar os 15 Totens sequencialmente com espaçamento padrão de três segundos entre POSTs, de modo que o ciclo leve alguns segundos. O ciclo e o espaçamento DEVEM (MUST) poder ser sobrescritos por configuração de ambiente, sem alterar a regra de domínio do heartbeat. Considerando os 15 Totens documentados em `.env.example`, para a carga das automações há no máximo sete POSTs do Simulator por janela de vinte segundos, ou oito incluindo eventual disparo do Fiscal, e cadência média de 15 POSTs mais um GET por cinco minutos. Isso NÃO DEVE (MUST NOT) reservar capacidade contra tráfego externo nem introduzir fila, scheduler externo, rate limiter ou infraestrutura nova. O Xano DEVE (MUST) continuar decidindo Offline exclusivamente pela última telemetria superior a quinze minutos; o Python NÃO DEVE (MUST NOT) calcular esse timeout. Um ciclo de telemetria de quinze minutos junto desse timeout opera no limite e pode gerar falso Offline por atraso; os ciclos de cinco minutos fornecem aproximadamente três períodos esperados de telemetria antes do timeout. O Fiscal apenas DEVE (MUST) disparar a verificação e NÃO DEVE (MUST NOT) conhecer nem decidir a regra de quinze minutos.

#### Scenario: Execução operacional padrão
- **WHEN** Fiscal e Simulator executam com configuração operacional padrão
- **THEN** Fiscal usa cinco minutos e Simulator inicia ciclos a cada cinco minutos, enviando os 15 Totens sequencialmente a cada três segundos, sem alterar a regra Xano de Offline pela última telemetria superior a quinze minutos

#### Scenario: Sobrescrita de tempos por ambiente
- **WHEN** ciclo e/ou espaçamento são sobrescritos por configuração de ambiente
- **THEN** Fiscal e Simulator preservam os defaults operacionais de cinco minutos quando não há sobrescrita, e a configuração não altera a regra de heartbeat do Xano
