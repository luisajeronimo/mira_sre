# Spec Delta

## MODIFIED Requirements

### Requirement: Sessão identifica o usuário autenticado
O sistema DEVE (MUST) permitir que um consumidor autenticado consulte sua identidade atual e receba somente os dados necessários para identificação e direcionamento da interface, incluindo identificação, nome, e-mail, perfil oficial e o estado de troca obrigatória de senha.

#### Scenario: Consulta da própria identidade
- **WHEN** uma requisição com credencial de sessão válida consulta a identidade atual
- **THEN** o Xano retorna os dados do usuário associado à sessão, seu perfil oficial e se a troca obrigatória de senha está pendente

#### Scenario: Consulta sem sessão válida
- **WHEN** uma requisição sem credencial de sessão válida consulta a identidade atual
- **THEN** o Xano rejeita a requisição como não autenticada

### Requirement: Somente perfis oficiais obtêm acesso ao MIRA
O sistema DEVE (MUST) conceder uma sessão utilizável no MIRA somente a usuários associados a Gerente, Técnico, Diretoria ou Administrador. `administrador` é um usuário humano autenticável; `admin` e atores de sistema não representam perfil oficial de sessão humana.

#### Scenario: Usuário com perfil oficial
- **WHEN** um usuário com credenciais válidas possui o perfil Gerente, Técnico, Diretoria ou Administrador
- **THEN** o Xano permite a autenticação e identifica o perfil oficial na sessão

#### Scenario: Usuário com valor de perfil não oficial após a migração
- **WHEN** um usuário possui credenciais válidas, mas seu valor de perfil não corresponde a Gerente, Técnico, Diretoria ou Administrador depois da aplicação do mapeamento de migração aprovado
- **THEN** o Xano não concede acesso utilizável às APIs do MIRA e não converte esse valor sem nova decisão humana explícita

## ADDED Requirements

### Requirement: Primeiro acesso restringe a sessão autenticada
O sistema DEVE (MUST) permitir que a autenticação válida de usuário com troca obrigatória pendente emita token, mas DEVE limitar essa sessão à consulta da própria identidade, à troca obrigatória da própria senha e ao encerramento local aplicável. APIs funcionais normais DEVEM rejeitar a sessão pendente no backend.

#### Scenario: Login com troca pendente
- **WHEN** um usuário com senha temporária válida e troca obrigatória pendente autentica
- **THEN** o sistema emite token e `/me` informa que a troca está pendente

#### Scenario: Sessão pendente chama operação funcional normal
- **WHEN** um usuário autenticado com troca obrigatória pendente chama diretamente uma API funcional normal
- **THEN** o Xano rejeita a operação sem retornar dados protegidos nem executar alteração

### Requirement: Troca obrigatória altera somente a senha do usuário autenticado
O sistema DEVE (MUST) oferecer uma operação autenticada de primeiro acesso que receba somente a nova senha, valide o mínimo de oito caracteres, altere a senha do próprio usuário pelo mecanismo nativo e encerre a pendência somente após sucesso coerente das duas alterações.

#### Scenario: Troca obrigatória bem-sucedida
- **WHEN** o usuário autenticado com troca pendente informa nova senha válida
- **THEN** o sistema altera sua senha, encerra a pendência e não retorna a senha, hash ou token adicional

#### Scenario: Troca sem pendência ou com senha curta
- **WHEN** o usuário chama a troca sem pendência ou informa senha com menos de oito caracteres
- **THEN** o sistema rejeita a operação sem limpar a pendência nem alterar a senha
