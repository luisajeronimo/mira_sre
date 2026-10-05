# administracao-usuarios Specification

## Purpose

Definir o provisionamento administrativo mínimo e seguro de usuários humanos do MIRA, com perfil, Loja e senha temporária sujeitos a regras verificáveis.

## Requirements

### Requirement: Administrador cria usuários por contrato funcional específico
O sistema MUST permitir a criação de usuário somente por `POST /administracao/usuarios` e somente a um Administrador autenticado. O contrato MUST receber nome, e-mail, perfil, `lojas_id` quando aplicável e senha temporária, e NÃO DEVE reutilizar ou desbloquear CRUD genérico de `usuarios`.

#### Scenario: Administrador cria usuário
- **WHEN** um Administrador autenticado envia uma criação válida
- **THEN** o sistema cria o usuário e retorna somente sua identidade pública necessária

#### Scenario: Perfil não administrativo tenta criar usuário
- **WHEN** Gerente, Técnico ou Diretoria chama o contrato de criação
- **THEN** o sistema rejeita a operação sem criar usuário

### Requirement: Bootstrap da primeira conta Administrador exige gate humano
O sistema MUST tratar `POST /administracao/usuarios` como operação posterior à existência de Administrador autenticado. O bootstrap da primeira conta `administrador` DEVE exigir identificação e autorização humana explícitas para procedimento administrativo nativo no Xano, sem conversão automática de `admin` e sem expor senha, hash ou token.

#### Scenario: API sem Administrador prévio
- **WHEN** não existe Administrador autenticado para chamar o contrato administrativo
- **THEN** o sistema não usa o contrato para provisionar a primeira conta

#### Scenario: Bootstrap autorizado
- **WHEN** houver autorização humana explícita que identifique a primeira conta e aprove o procedimento nativo Xano
- **THEN** a execução segue o mecanismo nativo de senha e registra evidência segura sem material de credencial

#### Scenario: Credencial de automação tenta criar usuário
- **WHEN** Bot, Fiscal ou Simulator tenta chamar o contrato de criação
- **THEN** o sistema rejeita a operação sem criar usuário

### Requirement: Criação aceita somente perfis humanos canônicos
O sistema MUST aceitar somente `gerente`, `tecnico`, `diretoria` e `administrador` como perfil de usuário criado. O valor `admin`, `bot_fiscalizacao` e quaisquer valores fora dessa lista DEVEM ser rejeitados.

#### Scenario: Perfil canônico Administrador
- **WHEN** o Administrador solicita a criação com perfil `administrador`
- **THEN** o sistema cria um usuário humano autenticável com esse perfil

#### Scenario: Perfil inválido
- **WHEN** a criação informa um perfil fora dos valores canônicos
- **THEN** o sistema rejeita a requisição sem persistir usuário

### Requirement: E-mail identifica unicamente o usuário criado
O sistema MUST validar o e-mail informado e DEVE rejeitar a criação quando ele já identificar um usuário existente.

#### Scenario: E-mail disponível
- **WHEN** a criação informa e-mail válido ainda não cadastrado
- **THEN** o sistema permite que a criação prossiga conforme as demais validações

#### Scenario: E-mail duplicado
- **WHEN** a criação informa e-mail já cadastrado
- **THEN** o sistema rejeita a criação sem expor dados do usuário existente

### Requirement: Associação de Loja segue o perfil criado
O sistema MUST exigir `lojas_id` de Loja existente para Gerente. Para Técnico, Diretoria e Administrador, `lojas_id` DEVE ser nulo e a requisição que o informar DEVE ser rejeitada.

#### Scenario: Gerente com Loja existente
- **WHEN** um Administrador cria Gerente com `lojas_id` de uma Loja existente
- **THEN** o sistema cria o Gerente associado àquela Loja

#### Scenario: Gerente sem Loja ou com Loja inexistente
- **WHEN** a criação de Gerente omite `lojas_id` ou informa uma Loja inexistente
- **THEN** o sistema rejeita a criação sem persistir usuário

#### Scenario: Perfil global com Loja informada
- **WHEN** a criação de Técnico, Diretoria ou Administrador informa `lojas_id`
- **THEN** o sistema rejeita a criação sem ignorar silenciosamente o campo

### Requirement: Administração consulta opções mínimas de Loja para criar Gerente
O sistema MUST oferecer `GET /administracao/lojas` exclusivamente a Administrador autenticado e aprovado pelo gate central de primeiro acesso. A resposta MUST conter somente a lista de opções, cada uma com `id` e `nome`, para preencher o seletor da criação de Gerente. Administrador pendente, Gerente, Técnico, Diretoria e pessoa não autenticada MUST ser rejeitados. Esta capability NÃO DEVE ampliar as permissões de `GET /lojas`, `GET /lojas/{id}` ou de gestão de Lojas.

#### Scenario: Administrador concluído consulta opções para criação
- **WHEN** um Administrador autenticado e sem pendência consulta `GET /administracao/lojas`
- **THEN** o sistema retorna as Lojas existentes em uma lista mínima de `{id, nome}`

#### Scenario: Sessão pendente ou perfil não administrativo consulta opções
- **WHEN** Administrador pendente, Gerente, Técnico, Diretoria ou pessoa não autenticada chama `GET /administracao/lojas`
- **THEN** o sistema rejeita a consulta sem ampliar a autorização geral de Lojas

### Requirement: Senha temporária é sensível e inicia troca obrigatória
O sistema MUST aceitar senha temporária somente como input sensível, com no mínimo oito caracteres, e persistir seu valor pelo mecanismo nativo de senha. Um usuário criado por este contrato DEVE iniciar com troca obrigatória pendente; senha, hash, token e histórico de senha NÃO DEVEM constar da resposta.

#### Scenario: Criação com senha temporária válida
- **WHEN** um Administrador envia senha temporária com oito ou mais caracteres
- **THEN** o usuário criado nasce com troca obrigatória pendente e a resposta não contém material de credencial

#### Scenario: Senha temporária curta
- **WHEN** a criação informa senha temporária com menos de oito caracteres
- **THEN** o sistema rejeita a criação sem persistir usuário
