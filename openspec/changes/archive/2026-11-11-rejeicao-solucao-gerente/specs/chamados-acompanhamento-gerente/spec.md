# Spec Delta

## ADDED Requirements

### Requirement: Gerente rejeita solução de chamado Resolvido da própria Loja
O Xano DEVE (MUST) oferecer uma operação autenticada específica de rejeição de solução, separada do Save operacional. A operação DEVE (MUST) validar, antes de qualquer escrita, a autorização definida em `autorizacao-perfis`, a justificativa não vazia após trim, o status persistido `Resolvido` e o `ultima_atualizacao_em` informado. Ao confirmar, o Xano DEVE (MUST) registrar a justificativa como comentário público com o Gerente autenticado como autor, alterar o status para `Solução Rejeitada`, atualizar `ultima_atualizacao_em` e registrar `alteracao_chamado` com o par `Resolvido` → `Solução Rejeitada`, o autor e a referência ao comentário, sem visibilidade. A operação NÃO DEVE (MUST NOT) alterar responsável, prioridade, Categoria, SLA aplicado ou outros dados funcionais, nem criar status diferente dos canônicos vigentes. Autor, status, visibilidade e timestamps DEVEM (MUST) ser definidos pelo Xano.

#### Scenario: Rejeição válida
- **WHEN** o Gerente da Loja rejeita, com justificativa não vazia e `ultima_atualizacao_em` atual, chamado `Resolvido`
- **THEN** o chamado passa a `Solução Rejeitada`, a justificativa aparece como comentário público do Gerente e a transição aparece no histórico público de status

#### Scenario: Chamado automático da própria Loja
- **WHEN** o chamado `Resolvido` foi criado pelo Bot de Fiscalização para Totem da Loja do Gerente
- **THEN** a rejeição é aceita nas mesmas condições

#### Scenario: Justificativa ausente ou vazia
- **WHEN** a justificativa está ausente, vazia ou contém somente espaços
- **THEN** o Xano rejeita a operação como entrada inválida sem alterar status, criar interação ou atualizar `ultima_atualizacao_em`

#### Scenario: Status diferente de Resolvido
- **WHEN** o status persistido é diferente de `Resolvido`, inclusive `Encerrado` ou `Cancelado`
- **THEN** o Xano rejeita a operação como conflito sem nenhuma escrita

#### Scenario: Detalhe desatualizado
- **WHEN** o `ultima_atualizacao_em` informado difere do persistido
- **THEN** o Xano rejeita a operação como conflito sem nenhuma escrita

#### Scenario: Dados funcionais preservados
- **WHEN** a rejeição é concluída
- **THEN** responsável, prioridade, Categoria e SLA aplicado permanecem inalterados

#### Scenario: Cliente informa campos sob autoridade do Xano
- **WHEN** o cliente envia autor, Loja, status, visibilidade ou timestamp funcional
- **THEN** o Xano ignora ou rejeita esses valores e usa somente os definidos pelo backend
