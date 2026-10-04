# monitoramento-disponibilidade-totens Specification

## Purpose

Definir o monitoramento de disponibilidade dos Totens a partir da telemetria e preservar transições temporais confiáveis para incidentes e indicadores futuros.

## Requirements

### Requirement: Fiscal único aciona a decisão do Xano

O Fiscal DEVE (MUST) continuar sendo a única automação de fiscalização prevista nesta capacidade: chama sequencialmente `GET /verificar-falhas`, aguarda a resposta e só então aguarda o ciclo operacional padrão de 300 segundos antes da próxima chamada. O Xano DEVE (MUST) ser a única autoridade para avaliar a última telemetria de cada Totem por `evento_timestamp` e pelo limite estrito de mais de 15 minutos. Fiscal e Simulator NÃO DEVEM (MUST NOT) decidir disponibilidade, calcular timeout, criar chamado ou alterar estado. Múltiplas instâncias, workers e fiscalizações concorrentes NÃO DEVEM (MUST NOT) ser introduzidos por esta capacidade.

#### Scenario: Totem nunca recebeu telemetria

- **WHEN** a verificação encontra um Totem sem telemetria persistida
- **THEN** não altera disponibilidade, não registra transição e não cria incidente automático

#### Scenario: Telemetria no limite ou mais recente

- **WHEN** a última telemetria é igual ou posterior ao limite de 15 minutos
- **THEN** o Xano não considera o Totem sem heartbeat por essa verificação

### Requirement: Histórico específico de disponibilidade preserva transições

O sistema DEVE (MUST) persistir em `historico_disponibilidade_totens` somente transições decididas pelo Xano. Cada evento DEVE (MUST) conter identificador técnico, relação obrigatória `ativos_referencia_id`, relação técnica `telemetria_referencia_id`, status canônico `online` ou `offline`, `detectado_em`, `heartbeat_limite_minutos` e `created_at` técnico. A telemetria identifica a última telemetria que fundamentou a decisão, e o limite registra o snapshot da regra aplicada, atualmente `15`.

O histórico NÃO DEVE (MUST NOT) registrar polling sem transição, receber backfill, conter `chamado_id`, transformar telemetria em ator, servir de auditoria genérica ou persistir métricas derivadas.

#### Scenario: Detecção Offline é preservada

- **WHEN** ocorre uma transição elegível Online → Offline
- **THEN** o histórico recebe um evento `offline` ligado ao Totem e à última telemetria, com `detectado_em` da decisão e `heartbeat_limite_minutos = 15`

#### Scenario: Recuperação Online é preservada

- **WHEN** ocorre uma transição elegível Offline → Online
- **THEN** o histórico recebe um evento `online` ligado ao Totem e à telemetria recente que fundamentou a recuperação

#### Scenario: Verificação sem transição

- **WHEN** uma verificação encontra o mesmo estado de disponibilidade já persistido
- **THEN** não cria registro histórico adicional

### Requirement: Transição elegível para Offline é previamente Online

O Xano DEVE (MUST) produzir transição Offline somente quando o Totem possui telemetria anterior, sua última `evento_timestamp` excede estritamente 15 minutos e seu estado persistido imediatamente anterior é Online. A continuidade de Totem já Offline NÃO DEVE (MUST NOT) produzir outra transição, sobrescrever evento anterior ou criar incidente pela mesma ausência.

#### Scenario: Online passa para Offline por heartbeat expirado

- **WHEN** Totem previamente Online possui última telemetria superior a 15 minutos
- **THEN** disponibilidade passa para Offline, um único evento `offline` é persistido e a criação de incidente é avaliada

#### Scenario: Fiscal repete verificação sem nova telemetria

- **WHEN** o Fiscal chama a verificação novamente para Totem que permanece Offline e sem telemetria recente
- **THEN** o Xano não registra transição Offline adicional nem cria incidente adicional por essa continuidade

### Requirement: Transição Offline e criação crítica são atômicas

Para uma transição Online → Offline, o Xano DEVE (MUST) executar na mesma `db.transaction` a revalidação da última telemetria e elegibilidade, confirmação do estado anterior Online, validação da categoria de heartbeat, consulta de incidente equivalente, criação do histórico Offline, atualização do Totem e, quando elegível, criação do incidente.

Se operação obrigatória da unidade falhar, suas escritas NÃO DEVEM (MUST NOT) permanecer parcialmente aplicadas. Após rollback, fiscalização posterior DEVE (MUST) poder reavaliar normalmente o Totem ainda elegível. A capacidade NÃO DEVE (MUST NOT) introduzir serialização, locks, CAS, `FOR UPDATE`, claim de concorrência, índice UNIQUE para concorrência ou garantia para múltiplos Fiscais.

#### Scenario: Falha ao criar histórico ou incidente durante transição

- **WHEN** a criação obrigatória de histórico ou incidente falha dentro da transação elegível
- **THEN** as escritas da transição são revertidas e verificação futura pode reavaliar o Totem ainda Online

#### Scenario: Equivalente encontrado durante transição

- **WHEN** transição Online → Offline encontra incidente equivalente não terminal
- **THEN** disponibilidade e histórico Offline são persistidos sem criar outro incidente

### Requirement: Incidente automático é avaliado na transição Offline

O Xano DEVE (MUST) avaliar criação de incidente somente na transição elegível Online → Offline. Novo incidente elegível DEVE (MUST) usar Totem e categoria corretos, status inicial `Novo`, prioridade `Urgente`, origem `automatico`, solicitante humano ausente, `criador_sistema = bot_fiscalizacao` e snapshot do SLA vigente da categoria.

#### Scenario: Transição Offline sem equivalente não terminal

- **WHEN** ocorre transição Online → Offline e não existe incidente equivalente não terminal
- **THEN** Xano cria incidente automático com os campos aprovados

#### Scenario: Categoria de heartbeat indisponível

- **WHEN** transição Online → Offline precisa avaliar incidente e a categoria `Totem Offline / Sem Heartbeat` não está disponível ou não possui contrato válido
- **THEN** transição e incidente não são persistidos parcialmente e a verificação reporta falha interna sem criar chamado incompleto

### Requirement: Deduplicação usa somente status vigentes não terminais

O sistema DEVE (MUST) considerar equivalente incidente do mesmo Totem e categoria cujo status seja `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido` ou `Solução Rejeitada`. `Encerrado` e `Cancelado` DEVEM (MUST) ser terminais e não bloquear nova transição elegível; `Aguardando Terceiro` NÃO DEVE (MUST NOT) integrar a regra. Origem e autoria do Bot NÃO DEVEM (MUST NOT) integrar a chave e esta capacidade NÃO DEVE (MUST NOT) criar constraint física em `chamados`.

#### Scenario: Cada status não terminal bloqueia duplicação

- **WHEN** existe incidente equivalente em qualquer status vigente não terminal
- **THEN** transição Offline não cria outro incidente automático

#### Scenario: Incidente equivalente terminal

- **WHEN** os únicos incidentes equivalentes do Totem estão Encerrados ou Cancelados e ocorre nova transição elegível Online → Offline
- **THEN** Xano pode criar novo incidente automático

#### Scenario: Status legado não governa deduplicação

- **WHEN** existe chamado equivalente somente com status legado `Aguardando Terceiro`
- **THEN** esse status não é usado para decidir deduplicação do heartbeat

### Requirement: Telemetria recente restaura Online sem tratar chamado

O Xano DEVE (MUST) restaurar Totem Offline para Online quando a verificação encontrar telemetria no limite ou mais recente. A unidade de escrita DEVE (MUST) persistir evento histórico Online, com telemetria de referência e snapshot do limite aplicado, e atualizar o Totem. Retorno de telemetria NÃO DEVE (MUST NOT) resolver, encerrar, cancelar, alterar status ou modificar tratativa de chamado.

#### Scenario: Retorno de telemetria de Totem Offline

- **WHEN** Totem Offline possui telemetria no limite ou mais recente na verificação seguinte
- **THEN** disponibilidade passa para Online e histórico recebe uma única transição Online

#### Scenario: Fiscal repete verificação após recuperação

- **WHEN** Totem continua Online com telemetria recente em nova verificação
- **THEN** sistema não duplica transição Online nem altera chamado existente

### Requirement: Categoria de heartbeat descreve o contrato vigente

A categoria `Totem Offline / Sem Heartbeat` DEVE (MUST) continuar do tipo `Incidente`, não permitida para abertura manual e com SLA numérico aplicável ao snapshot. Sua descrição versionada DEVE (MUST) referir ausência superior a 15 minutos, sem modificar prioridade automática ou SLA.

#### Scenario: Categoria usada na criação automática

- **WHEN** Xano cria incidente elegível de heartbeat
- **THEN** utiliza categoria de heartbeat com SLA vigente como snapshot do chamado

### Requirement: Dados temporais permitem consumo futuro sem dashboard

Eventos de disponibilidade, telemetria de referência e `chamados.criado_em` DEVEM (MUST) permitir futuramente relacionar detecção, recuperação, duração, número e recorrência por Totem ou Loja, percentual histórico de disponibilidade, último heartbeat e criação de incidente. A capacidade NÃO DEVE (MUST NOT) persistir duração, percentual, MTTD, MTTR, médias ou agregados, nem implementar dashboard, endpoint específico ou UI nesta change.

#### Scenario: Dados de uma indisponibilidade completa

- **WHEN** Totem passa de Online para Offline e depois retorna Online
- **THEN** existem fatos persistidos que permitem relacionar última telemetria, detecção, recuperação e chamado criado quando aplicável
