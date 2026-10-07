# Spec Delta

## ADDED Requirements

### Requirement: Assunção efetiva atualiza a última atualização observável
Uma assunção que efetivamente altera o Técnico responsável DEVE (MUST) atualizar `ultima_atualizacao_em` pelo Xano junto com `tecnico_id` e `atribuido_em`. A repetição idempotente pelo mesmo Técnico NÃO DEVE (MUST NOT) alterar novamente esse timestamp.

#### Scenario: Assunção válida atualiza a data
- **WHEN** um Técnico efetiva assunção válida de chamado sem responsável
- **THEN** o Xano persiste `tecnico_id`, `atribuido_em` e `ultima_atualizacao_em` definidos pelo backend

#### Scenario: Repetição idempotente não atualiza a data
- **WHEN** o mesmo Técnico repete a assunção de chamado já atribuído a ele
- **THEN** `ultima_atualizacao_em` permanece inalterada

