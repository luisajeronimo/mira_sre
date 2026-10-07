# Spec Delta

## ADDED Requirements

### Requirement: Criação de chamado inicializa a última atualização observável
Todo chamado criado pelos fluxos manual e automático DEVE (MUST) persistir `ultima_atualizacao_em` com o mesmo valor funcional de `criado_em`. O valor NÃO DEVE (MUST NOT) ser recebido de consumidores nem substituído por `created_at` técnico.

#### Scenario: Abertura manual inicializa a data
- **WHEN** um Gerente abre chamado manual válido
- **THEN** o registro persiste `criado_em` e `ultima_atualizacao_em` com o mesmo instante definido pelo Xano

#### Scenario: Resposta da abertura preserva a data funcional
- **WHEN** a abertura manual é concluída com sucesso
- **THEN** o DTO funcional retorna `ultima_atualizacao_em` igual a `criado_em`, sem expor `created_at`

