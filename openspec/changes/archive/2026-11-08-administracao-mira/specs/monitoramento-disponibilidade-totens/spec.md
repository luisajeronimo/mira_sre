# Spec Delta

## MODIFIED Requirements

### Requirement: Listagem de monitoramento expõe resumo operacional persistido

`GET /monitoramento/ativos` DEVE (MUST) retornar, para cada Totem, identificação, Loja atual, estado `online` ou `offline` persistido no Xano ou estado ainda desconhecido quando não houve primeira telemetria válida, `evento_timestamp` da última telemetria e `detectado_em` da última transição, admitindo `null` para fatos ausentes. Os totais de `/monitoramento` DEVEM (MUST) continuar derivados somente dos estados efetivamente persistidos, sem classificar o desconhecido como Online ou Offline.

#### Scenario: Listagem com resumo de Totens

- **WHEN** um perfil já autorizado ao monitoramento consulta a listagem
- **THEN** cada Totem retornado contém sua Loja atual, estado persistido quando existir, data/hora da última telemetria e data/hora da última transição disponíveis

#### Scenario: Totem sem fatos históricos

- **WHEN** um Totem ainda não possui primeira telemetria válida nem transição registrada
- **THEN** a listagem o mantém com estado operacional desconhecido e timestamps ausentes, sem fabricar Online ou Offline

### Requirement: Estados operacionais preservam dados e usam badge consistente
A página de monitoramento DEVE (MUST) apresentar estados persistidos de Totens e incidentes em maiúsculas com o mesmo padrão semântico de badge da interface. Estado de Totem ainda desconhecido DEVE (MUST) ser distinguível de `ONLINE` e `OFFLINE`. A apresentação NÃO DEVE (MUST NOT) alterar valores, cálculos, autorização ou fatos persistidos.

#### Scenario: Totem retorna estado persistido
- **WHEN** a consulta existente retorna `online` ou `offline`
- **THEN** a interface exibe respectivamente `ONLINE` ou `OFFLINE` como apresentação visual, mantendo o valor retornado pela consulta

#### Scenario: Totem sem primeira telemetria
- **WHEN** a consulta retorna estado operacional ainda desconhecido
- **THEN** a interface não o apresenta como `ONLINE` nem `OFFLINE` e não altera o cadastro

## ADDED Requirements

### Requirement: Transferência preserva fatos anteriores do Totem
A transferência de Totem DEVE (MUST) preservar telemetrias e eventos de disponibilidade existentes, seus IDs e timestamps. Para vínculo demonstrável, a consulta histórica por Loja DEVE (MUST) usar `evento_timestamp` da telemetria e `detectado_em` do evento de disponibilidade, sem derivar Loja apenas do vínculo atual.

#### Scenario: Fatos antes e depois da transferência
- **WHEN** Totem possui eventos anteriores e posteriores à mudança de Loja
- **THEN** os fatos permanecem intactos e são atribuídos às respectivas Lojas de ocorrência

#### Scenario: Vínculo histórico não demonstrável
- **WHEN** não há evidência suficiente para atribuir um fato legado a uma Loja
- **THEN** a Loja histórica fica indeterminada, sem inferência pelo vínculo atual, backfill ou alteração do fato

#### Scenario: Loja Inativa conserva monitoramento
- **WHEN** a Loja de um Totem já monitorado se torna `Inativa`
- **THEN** a verificação de heartbeat e a criação elegível de incidente continuam, sem produzir `Offline` somente pela situação cadastral
