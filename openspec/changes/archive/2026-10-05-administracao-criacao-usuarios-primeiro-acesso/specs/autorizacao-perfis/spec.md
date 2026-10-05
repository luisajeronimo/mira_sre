# Spec Delta

## MODIFIED Requirements

### Requirement: Negação por padrão
O sistema DEVE (MUST) negar qualquer operação destinada a usuários que não esteja explicitamente autorizada para o perfil e o escopo do usuário autenticado. `administrador` somente recebe nesta capacidade a criação administrativa de usuários; `admin`, `bot_fiscalizacao` e valores não oficiais não recebem permissões humanas.

#### Scenario: Operação sem permissão definida
- **WHEN** um usuário autenticado solicita uma operação sem permissão definida para seu perfil
- **THEN** o Xano rejeita a operação sem executar alterações

#### Scenario: Perfil não oficial
- **WHEN** uma requisição está associada a `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `bot_fiscalizacao` ou qualquer outro valor que não represente Gerente, Técnico, Diretoria ou Administrador
- **THEN** o Xano não atribui permissões de um perfil oficial à requisição

## ADDED Requirements

### Requirement: Autorização central considera troca obrigatória pendente
O sistema DEVE (MUST) aplicar centralmente o estado de troca obrigatória antes da autorização de operações funcionais normais. A sessão pendente somente DEVE passar para a consulta da própria identidade e para a operação autenticada de troca de senha.

#### Scenario: Autorização de operação normal com pendência
- **WHEN** uma sessão pendente alcança a autorização de uma operação funcional normal
- **THEN** o sistema a rejeita antes de executar a regra funcional da operação

#### Scenario: Operação permitida durante pendência
- **WHEN** uma sessão pendente consulta a própria identidade ou envia sua nova senha ao contrato de primeiro acesso
- **THEN** o sistema permite a operação autenticada correspondente

## MODIFIED Requirements

### Requirement: CRUDs genéricos não ampliam permissões
O sistema NÃO DEVE (MUST NOT) permitir que endpoints CRUD genéricos contornem as regras de autorização ou concedam operações administrativas e destrutivas não previstas para os perfis oficiais. A criação de usuário administrativo DEVE permanecer no contrato funcional específico autorizado apenas a Administrador.

#### Scenario: Acesso direto a mutação genérica
- **WHEN** um usuário autenticado chama diretamente um endpoint genérico de criação, alteração ou exclusão sem permissão funcional correspondente
- **THEN** o Xano rejeita a operação sem modificar os dados

#### Scenario: Consulta genérica fora do escopo
- **WHEN** uma consulta genérica poderia retornar dados além do escopo autorizado ao usuário
- **THEN** o Xano aplica o filtro de escopo no backend ou rejeita a consulta sem expor esses dados
