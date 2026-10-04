# Spec Delta

## MODIFIED Requirements

### Requirement: Compatibilidade automática é limitada aos novos dados compartilhados

O criador automático de heartbeat DEVE (MUST) criar incidente somente em uma transição elegível Online → Offline, com título, status `Novo`, prioridade `Urgente`, categoria, ativo, origem `automatico`, solicitante humano ausente, `criador_sistema = "bot_fiscalizacao"`, `criado_em` definido pelo backend e snapshot de SLA. A consulta de incidente equivalente DEVE (MUST) usar ativo, categoria e os status vigentes não terminais. Se encontrar equivalente, NÃO DEVE (MUST NOT) criar chamado nem alterar origem, autoria, status, SLA, solicitante ou qualquer dado do registro existente.

#### Scenario: Heartbeat cria incidente compatível

- **WHEN** uma transição elegível do heartbeat não encontra incidente equivalente não terminal
- **THEN** o Xano cria o registro com os dados compartilhados aprovados e sem solicitante humano

#### Scenario: Heartbeat encontra incidente equivalente

- **WHEN** uma transição elegível encontra incidente equivalente não terminal
- **THEN** nenhum novo chamado é criado e nenhum registro existente recebe alteração de origem, autoria, status, SLA ou solicitante
