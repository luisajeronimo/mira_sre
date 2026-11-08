# Spec Delta

## ADDED Requirements

### Requirement: Indicadores derivam somente de fatos persistidos
Os indicadores de disponibilidade, MTTD, MTTR, SLA e recorrência DEVEM (MUST) ser calculados exclusivamente a partir de fatos persistidos no Xano: eventos de `historico_disponibilidade_totens`, `evento_timestamp` da telemetria referenciada, `chamados`, Categoria e transições de status registradas em `alteracao_chamado`. O sistema NÃO DEVE (MUST NOT) inventar, estimar ou completar timestamps ausentes, nem persistir durações, percentuais, médias ou agregados sem change aprovada.

#### Scenario: Marco ausente
- **WHEN** um evento necessário ao cálculo não possui o timestamp exigido pela fórmula
- **THEN** o registro é excluído do cálculo e contado como inconsistência no resultado, sem valor substituto

#### Scenario: Período sem dados
- **WHEN** não há eventos elegíveis no período para um indicador de média
- **THEN** o indicador é apresentado como indisponível, e não como zero

### Requirement: MTTR mede a recuperação do Totem
O MTTR DEVE (MUST) medir o tempo médio entre o início e o fim de indisponibilidades encerradas do Totem, conforme os marcos aprovados para disponibilidade, e NÃO DEVE (MUST NOT) usar abertura, resolução ou encerramento de chamado. Indisponibilidades ainda abertas NÃO DEVEM (MUST NOT) entrar na média.

#### Scenario: Chamado aberto após recuperação
- **WHEN** o Totem volta a Online e o chamado correspondente continua aberto
- **THEN** a indisponibilidade entra no MTTR e o status do chamado não altera o valor

#### Scenario: Indisponibilidade aberta
- **WHEN** o Totem continua Offline no fim do período
- **THEN** a indisponibilidade não entra na média e é informada em contagem própria

### Requirement: Categoria é a referência de causa e recorrência
A análise de causas e de recorrência DEVE (MUST) agrupar chamados pela Categoria. Título, descrição ou outro campo NÃO DEVEM (MUST NOT) substituir a Categoria sem decisão aprovada.

#### Scenario: Mesma descrição em Categorias diferentes
- **WHEN** dois chamados do mesmo Totem possuem descrições iguais e Categorias diferentes
- **THEN** eles não são considerados recorrência entre si

### Requirement: Faixas do termômetro de SLA
O consumo percentual de SLA DEVE (MUST) ser classificado como normal abaixo de 70%, risco de 70% a 90% inclusive, crítico acima de 90% até 100% inclusive, e violado acima de 100%.

#### Scenario: Limites exatos
- **WHEN** o consumo é exatamente 70%, 90% ou 100%
- **THEN** a classificação é, respectivamente, risco, risco e crítico

### Requirement: Indicadores distintos não são combinados
Disponibilidade, MTTD, MTTR, SLA e recorrência DEVEM (MUST) ser calculados e apresentados separadamente. Nenhum indicador DEVE (MUST NOT) combinar tempo de disponibilidade do Totem com tempo de SLA do chamado na mesma fórmula.

#### Scenario: Chamado e indisponibilidade simultâneos
- **WHEN** um chamado de heartbeat está aberto durante a indisponibilidade do Totem
- **THEN** a disponibilidade usa somente os eventos de disponibilidade e o SLA usa somente a linha do tempo do chamado
