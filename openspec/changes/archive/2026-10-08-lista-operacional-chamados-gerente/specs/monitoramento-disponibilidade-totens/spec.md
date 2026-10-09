# Spec Delta

## MODIFIED Requirements

### Requirement: Incidente automático é avaliado na transição Offline
O Xano DEVE (MUST) avaliar criação de incidente somente na transição elegível Online → Offline. Novo incidente elegível DEVE (MUST) usar Totem e categoria corretos, status inicial `Novo`, prioridade `Urgente`, origem `automatico`, solicitante humano ausente, `criador_sistema = bot_fiscalizacao`, snapshot do SLA vigente da categoria e os timestamps funcionais `criado_em` e `ultima_atualizacao_em`. Os dois timestamps DEVEM (MUST) receber o mesmo instante funcional calculado uma única vez pelo backend.

#### Scenario: Transição Offline sem equivalente não terminal
- **WHEN** ocorre transição Online → Offline e não existe incidente equivalente não terminal
- **THEN** Xano cria incidente automático com os campos aprovados e inicializa `criado_em` e `ultima_atualizacao_em` no mesmo instante funcional

#### Scenario: Categoria de heartbeat indisponível
- **WHEN** transição Online → Offline precisa avaliar incidente e a categoria `Totem Offline / Sem Heartbeat` não está disponível ou não possui contrato válido
- **THEN** transição e incidente não são persistidos parcialmente e a verificação reporta falha interna sem criar chamado incompleto
