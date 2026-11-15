## MODIFIED Requirements

### Requirement: Periodicidades preservam a regra de heartbeat do Xano

O Fiscal DEVE (MUST) usar periodicidade operacional padrão de cinco minutos. O Simulator DEVE (MUST) iniciar um ciclo operacional de telemetria a cada cinco minutos; os cinco minutos NÃO DEVEM (MUST NOT) ser intervalo entre Totens. A cada ciclo, DEVE (MUST) consultar uma vez o controle agrupado de seus participantes e enviar somente os autorizados, sequencialmente com espaçamento padrão de três segundos entre POSTs. Com os 15 Totens atuais ativos, são até 15 POSTs, um GET de controle e um GET do Fiscal por ciclo; o lote fictício não acrescenta participantes. O espaçamento DEVE (MUST) preservar no máximo sete POSTs por janela de vinte segundos, ou nove requisições incluindo ambos os GETs. Isso NÃO DEVE (MUST NOT) reservar capacidade contra tráfego externo nem introduzir fila, scheduler externo, rate limiter ou infraestrutura nova. O ciclo e o espaçamento DEVEM (MUST) poder ser sobrescritos por configuração sem alterar a regra de domínio do heartbeat. O Xano DEVE (MUST) continuar como autoridade exclusiva para decidir Offline pela última telemetria superior a quinze minutos; o Python NÃO DEVE (MUST NOT) calcular esse timeout, e o Fiscal apenas DEVE (MUST) disparar a verificação e NÃO DEVE (MUST NOT) conhecer nem decidir essa regra.

#### Scenario: Execução operacional padrão
- **WHEN** Fiscal e Simulator executam com configuração operacional padrão e controles inicializados
- **THEN** Fiscal usa cinco minutos e Simulator inicia ciclos a cada cinco minutos, faz uma leitura agrupada e envia os participantes ativos sequencialmente a cada três segundos, sem alterar a regra de Offline pela última telemetria superior a quinze minutos

#### Scenario: Sobrescrita de tempos por configuração
- **WHEN** ciclo e/ou espaçamento são sobrescritos por configuração
- **THEN** Fiscal e Simulator preservam os defaults operacionais de cinco minutos quando não há sobrescrita, e a configuração não altera a regra de heartbeat

#### Scenario: Totens existentes recebem histórico fictício
- **WHEN** a preparação usa dois dos 15 participantes atuais
- **THEN** a consulta continua agrupada e os envios mantêm o espaçamento, sem acrescentar consulta de controle por Totem ou fiscalização paralela

## ADDED Requirements

### Requirement: Consulta de controle exige a chave exclusiva do Simulator
`GET /simulator/controle-telemetria` DEVE (MUST) validar `X-MIRA-Simulator-Key` contra a credencial exclusiva do Simulator antes de qualquer leitura. Chave ausente, vazia, inválida ou de outra finalidade DEVE (MUST) receber HTTP 401 com `{"error":"Não autenticado."}`, sem dados operacionais, segredo ou efeitos parciais.

#### Scenario: Chave correta consulta controles
- **WHEN** o Simulator apresenta sua chave válida e os IDs participantes válidos
- **THEN** recebe somente os IDs solicitados existentes e seus controles, sem mutação de dados

#### Scenario: Chave ausente ou cruzada
- **WHEN** a requisição não apresenta a chave correta do Simulator
- **THEN** recebe o mesmo 401 público antes de qualquer leitura operacional

#### Scenario: Credencial configurada está indisponível
- **WHEN** a credencial técnica do Simulator não está configurada no Xano
- **THEN** a consulta falha fechada com o mesmo 401, sem aceitar valor vazio ou usar a chave do Fiscal
