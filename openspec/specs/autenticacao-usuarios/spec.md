# autenticação de usuários Specification

## Purpose

Definir a autenticação dos usuários do MIRA no Xano e o contrato seguro pelo qual o Reflex obtém e apresenta a identidade autenticada.

## Requirements

### Requirement: Autenticação pertence ao Xano
O sistema DEVE (MUST) autenticar usuários exclusivamente pelo mecanismo de autenticação do Xano. O Reflex DEVE apenas enviar as credenciais ao contrato de autenticação e consumir o resultado, sem implementar validação própria de credenciais.

#### Scenario: Credenciais válidas
- **WHEN** um usuário cadastrado informa credenciais válidas
- **THEN** o Xano autentica o usuário e retorna um token válido por 8 horas para as requisições subsequentes

#### Scenario: Credenciais inválidas
- **WHEN** uma tentativa de autenticação contém credenciais inválidas
- **THEN** o Xano rejeita a tentativa sem emitir credencial de sessão e sem revelar qual parte das credenciais está incorreta

### Requirement: Token possui expiração definida
O sistema DEVE (MUST) emitir o token de autenticação com expiração de 8 horas. O sistema NÃO DEVE (MUST NOT) introduzir refresh token ou renovação automática nesta change.

#### Scenario: Expiração do token
- **WHEN** o Xano emite um token após uma autenticação válida
- **THEN** o token expira 8 horas após sua emissão

#### Scenario: Token expirado
- **WHEN** uma API destinada a usuários recebe um token após sua expiração
- **THEN** o Xano rejeita a requisição como não autenticada sem renovar o token automaticamente

### Requirement: Sessão identifica o usuário autenticado
O sistema DEVE (MUST) permitir que um consumidor autenticado consulte sua identidade atual e receba somente os dados necessários para identificação e direcionamento da interface, incluindo identificação, nome, e-mail e perfil oficial.

#### Scenario: Consulta da própria identidade
- **WHEN** uma requisição com credencial de sessão válida consulta a identidade atual
- **THEN** o Xano retorna os dados do usuário associado à sessão e seu perfil oficial

#### Scenario: Consulta sem sessão válida
- **WHEN** uma requisição sem credencial de sessão válida consulta a identidade atual
- **THEN** o Xano rejeita a requisição como não autenticada

### Requirement: Credenciais não são dados de negócio
O sistema NÃO DEVE (MUST NOT) retornar senha, representação reversível da senha ou material interno de autenticação nas respostas das APIs destinadas ao Reflex.

#### Scenario: Resposta de autenticação
- **WHEN** o Xano responde a uma autenticação bem-sucedida ou à consulta da identidade atual
- **THEN** a resposta não contém senha nem representação interna reutilizável da credencial armazenada

### Requirement: Somente perfis oficiais obtêm acesso ao MIRA
O sistema DEVE (MUST) conceder uma sessão utilizável no MIRA somente a usuários associados a um dos perfis oficiais Gerente, Técnico ou Diretoria.

#### Scenario: Usuário com perfil oficial
- **WHEN** um usuário com credenciais válidas possui o perfil Gerente, Técnico ou Diretoria
- **THEN** o Xano permite a autenticação e identifica o perfil oficial na sessão

#### Scenario: Usuário com valor de perfil não oficial após a migração
- **WHEN** um usuário possui credenciais válidas, mas seu valor de perfil não corresponde a Gerente, Técnico ou Diretoria depois da aplicação do mapeamento de migração aprovado
- **THEN** o Xano não concede acesso utilizável às APIs do MIRA e não converte esse valor sem nova decisão humana explícita

### Requirement: APIs destinadas a usuários exigem autenticação
O sistema DEVE (MUST) exigir uma credencial de sessão válida nas APIs destinadas ao uso por Gerente, Técnico ou Diretoria.

#### Scenario: Acesso autenticado
- **WHEN** uma API destinada a usuários recebe uma credencial de sessão válida
- **THEN** o Xano identifica o usuário antes de avaliar sua autorização

#### Scenario: Acesso anônimo
- **WHEN** uma API destinada a usuários é chamada sem credencial de sessão válida
- **THEN** o Xano rejeita a requisição sem retornar dados protegidos nem executar alterações
