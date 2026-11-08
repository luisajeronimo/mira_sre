# Spec Delta

## MODIFIED Requirements

### Requirement: Deduplicação usa somente status vigentes não terminais

O sistema DEVE (MUST) considerar equivalente incidente do mesmo Totem e categoria cujo status seja `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido`, `Reaberto` ou o legado `Solução Rejeitada`. `Encerrado` e `Cancelado` DEVEM (MUST) ser terminais e não bloquear nova transição elegível; `Aguardando Terceiro` NÃO DEVE (MUST NOT) integrar a regra. Origem e autoria do Bot NÃO DEVEM (MUST NOT) integrar a chave e esta capacidade NÃO DEVE (MUST NOT) criar constraint física em `chamados`.

#### Scenario: Cada status não terminal bloqueia duplicação

- **WHEN** existe incidente equivalente em qualquer status vigente não terminal
- **THEN** transição Offline não cria outro incidente automático

#### Scenario: Incidente reaberto bloqueia duplicação

- **WHEN** o incidente equivalente do Totem foi reaberto por rejeição e está `Reaberto`
- **THEN** transição Offline não cria outro incidente automático

#### Scenario: Incidente equivalente terminal

- **WHEN** os únicos incidentes equivalentes do Totem estão Encerrados ou Cancelados e ocorre nova transição elegível Online → Offline
- **THEN** Xano pode criar novo incidente automático

#### Scenario: Status legado não governa deduplicação

- **WHEN** existe chamado equivalente somente com status legado `Aguardando Terceiro`
- **THEN** esse status não é usado para decidir deduplicação do heartbeat
