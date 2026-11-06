# Spec Delta

## MODIFIED Requirements

### Requirement: Última atualização representa alteração observável pelo Gerente
Todo chamado válido DEVE (MUST) possuir `criado_em` e `ultima_atualizacao_em`. Na criação manual ou automática, o Xano DEVE (MUST) definir ambos com o mesmo instante funcional, calculado uma única vez; `criado_em` permanece imutável. Atribuição efetiva, mudança de status e comentário Público ou Interno autorizado DEVEM (MUST) atualizar somente `ultima_atualizacao_em`; leitura e eventos internos sem comentário ou consequência funcional NÃO DEVEM (MUST NOT) atualizá-lo.

#### Scenario: Criação inicializa os timestamps funcionais
- **WHEN** um fluxo funcional cria chamado válido
- **THEN** `criado_em` e `ultima_atualizacao_em` recebem o mesmo instante funcional definido pelo Xano

#### Scenario: Criação inicializa a última atualização
- **WHEN** um fluxo funcional cria novo chamado válido
- **THEN** `ultima_atualizacao_em` recebe o mesmo instante funcional de `criado_em`

#### Scenario: Evento observável posterior
- **WHEN** atribuição efetiva, mudança de status ou comentário Público autorizado ocorre
- **THEN** `criado_em` permanece imutável e o Xano atualiza `ultima_atualizacao_em` no mesmo ato

#### Scenario: Atribuição efetiva atualiza a data
- **WHEN** uma atribuição altera o Técnico responsável de um chamado
- **THEN** o Xano atualiza somente `ultima_atualizacao_em` no mesmo ato da alteração

#### Scenario: Mudança de status futura atualiza a data
- **WHEN** um fluxo funcional autorizado altera o status de um chamado
- **THEN** o Xano atualiza somente `ultima_atualizacao_em` no mesmo ato da alteração de status

#### Scenario: Comentário interno operacional
- **WHEN** um perfil operacional publica comentário Interno autorizado
- **THEN** o Xano atualiza `ultima_atualizacao_em` sem tornar o conteúdo do comentário visível ao Gerente

#### Scenario: Evento interno não visível
- **WHEN** ocorre diagnóstico ou outra operação interna sem comentário nem consequência funcional
- **THEN** o evento não altera `ultima_atualizacao_em`
