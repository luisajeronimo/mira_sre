# Spec Delta

## MODIFIED Requirements

### Requirement: Contratos funcionais preservam autenticação e negação por padrão
Todas as operações de `mira-service-desk` DEVEM (MUST) exigir autenticação da tabela `usuarios`, autorizar somente o perfil Gerente nesta capacidade e aplicar o escopo persistido de Loja no Xano. Em `POST /gerente/chamados`, a autorização do perfil Gerente DEVE (MUST) ocorrer no próprio contrato, antes de executar a abertura manual. Os contratos funcionais NÃO DEVEM (MUST NOT) reabrir os endpoints genéricos de POST, PATCH ou DELETE nem atribuir autorização ao Reflex.

#### Scenario: Token ausente ou inválido
- **WHEN** uma operação funcional recebe uma requisição sem token válido
- **THEN** o Xano responde como não autenticado sem consultar ou modificar dados protegidos

#### Scenario: Perfil autenticado sem permissão
- **WHEN** um Técnico ou usuário da Diretoria chama uma operação funcional reservada ao Gerente
- **THEN** o Xano responde como não autorizado sem executar a operação

#### Scenario: Administrador no contrato funcional do Gerente
- **WHEN** um Administrador autenticado chama `POST /gerente/chamados`
- **THEN** o Xano responde como não autorizado antes de executar a abertura manual, sem criar chamado

#### Scenario: Mutação genérica direta
- **WHEN** um usuário tenta usar os CRUDs genéricos existentes para criar, editar ou excluir chamado
- **THEN** a negação consolidada permanece aplicada e nenhum registro é modificado
