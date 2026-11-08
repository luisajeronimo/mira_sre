# Spec Delta

## ADDED Requirements

### Requirement: Reaberto integra fila, filtros e atribuição como status não terminal
O status `Reaberto` DEVE (MUST) ser tratado como status canônico não terminal em todos os contratos de consulta e atribuição: fila global, lista do Gerente, filtros de Status com normalização de maiúsculas e minúsculas, preferências persistidas de filtros e atribuição, reatribuição e liberação de responsável. O legado `Solução Rejeitada` DEVE (MUST) continuar aceito nesses mesmos pontos enquanto existirem registros com esse valor. Esta capacidade NÃO DEVE (MUST NOT) alterar o status ao atribuir, reatribuir ou liberar.

#### Scenario: Filtro por Reaberto
- **WHEN** Técnico, Diretoria, Administrador ou Gerente filtra a lista por `Reaberto` ou por variação de caixa como `reaberto`
- **THEN** o Xano normaliza o valor e retorna somente chamados com esse status no escopo do perfil

#### Scenario: Preferência com Reaberto
- **WHEN** o usuário salva preferência de filtro com Status `Reaberto`
- **THEN** o Xano aceita e restaura o valor como critério válido

#### Scenario: Atribuição em chamado reaberto
- **WHEN** um perfil operacional atribui, reatribui ou libera responsável de chamado `Reaberto`
- **THEN** o Xano aplica a operação como em qualquer chamado não terminal, sem alterar o status

#### Scenario: Reabertura preserva responsável
- **WHEN** um chamado com Técnico responsável é reaberto por rejeição
- **THEN** o chamado continua com o mesmo responsável e aparece na fila com status `Reaberto`

#### Scenario: Filtro por legado
- **WHEN** o usuário filtra por `Solução Rejeitada`
- **THEN** o Xano aceita o filtro e retorna os registros legados com esse valor, sem convertê-los
