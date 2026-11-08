# Spec Delta

## ADDED Requirements

### Requirement: Rejeição de solução é autorizada somente ao Gerente da Loja do chamado
O Xano DEVE (MUST) autorizar a rejeição de solução somente ao usuário autenticado, sem troca de senha pendente, com perfil Gerente e Loja associada igual à Loja do Totem do chamado. Técnico, Diretoria, Administrador e usuários sem perfil oficial NÃO DEVEM (MUST NOT) receber essa permissão. A permissão de rejeitar NÃO DEVE (MUST NOT) conceder ao Gerente Save operacional, mudança direta de status, atribuição, comentário interno ou acesso à fila e ao detalhe técnicos. Identificador, Loja ou perfil enviados pelo cliente e a visibilidade da ação no Reflex NÃO DEVEM (MUST NOT) conceder autorização.

#### Scenario: Gerente da Loja
- **WHEN** um Gerente rejeita chamado ligado a Totem da própria Loja
- **THEN** o Xano autoriza a operação

#### Scenario: Gerente de outra Loja
- **WHEN** um Gerente tenta rejeitar chamado de outra Loja
- **THEN** o Xano nega a operação sem retornar nem alterar dados

#### Scenario: Gerente sem Loja
- **WHEN** um Gerente sem Loja associada tenta rejeitar
- **THEN** o Xano nega a operação

#### Scenario: Perfil operacional
- **WHEN** Técnico, Diretoria ou Administrador usa a operação de rejeição
- **THEN** o Xano nega a operação

#### Scenario: Gerente tenta alterar status pelo Save
- **WHEN** um Gerente chama o Save operacional ou um endpoint genérico de alteração
- **THEN** o Xano continua negando a operação
