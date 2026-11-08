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
O sistema MUST exigir `lojas_id` de Loja existente e `Ativa` para Gerente. Para Técnico, Diretoria e Administrador, `lojas_id` DEVE ser nulo e a requisição que o informar DEVE ser rejeitada.

#### Scenario: Gerente com Loja existente
- **WHEN** um Administrador cria Gerente com `lojas_id` de uma Loja `Ativa` existente
- **THEN** o sistema cria o Gerente associado àquela Loja

#### Scenario: Gerente sem Loja ou com Loja inexistente
- **WHEN** a criação de Gerente omite `lojas_id` ou informa uma Loja inexistente
- **THEN** o sistema rejeita a criação sem persistir usuário

#### Scenario: Gerente com Loja Inativa
- **WHEN** a criação de Gerente informa uma Loja `Inativa`
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

### Requirement: Interface administrativa usa rota funcional de usuários
O Reflex DEVE (MUST) disponibilizar a criação e a manutenção de usuários na gestão consolidada `/administracao/gestao`, exclusivamente para Administrador autenticado e sem troca pendente. `/administracao` e `/administracao/usuarios` DEVEM (MUST) atuar somente como aliases protegidos para a gestão, sem segunda interface ou formulário duplicado. O contrato `POST /administracao/usuarios` continua sendo a operação de criação.

#### Scenario: Administrador acessa rota canônica
- **WHEN** Administrador autenticado e sem pendência acessa `/administracao/gestao`
- **THEN** o Reflex apresenta a gestão de usuários junto às gestões de Lojas e Totens, com criação em modal

#### Scenario: Link antigo
- **WHEN** Administrador autenticado acessa `/administracao` ou `/administracao/usuarios`
- **THEN** o Reflex redireciona para `/administracao/gestao` sem renderizar outra gestão

#### Scenario: Perfil não administrativo acessa rota administrativa
- **WHEN** Gerente, Técnico ou Diretoria acessa a rota canônica ou alias administrativo
- **THEN** o Reflex não apresenta dados ou formulários administrativos e o Xano continua negando contratos indevidos

#### Scenario: Primeiro acesso pendente
- **WHEN** Administrador com troca obrigatória pendente acessa rota canônica ou alias administrativo
- **THEN** o Reflex redireciona para `/primeiro-acesso` antes de carregar catálogo ou formulário

### Requirement: Campos administrativos possuem rótulos persistentes
Os campos existentes dos formulários de criação de usuário e de troca obrigatória de senha DEVEM (MUST) apresentar rótulos persistentes associados aos controles, legíveis antes e depois de digitar, conforme `DESIGN.md`.

#### Scenario: Criação de usuário
- **WHEN** Administrador abre o formulário de criação
- **THEN** Nome, E-mail, Perfil, Loja quando aplicável, Senha temporária e Confirmação possuem rótulos persistentes sem alterar campos ou validações

#### Scenario: Troca obrigatória de senha
- **WHEN** usuário abre o formulário de primeiro acesso
- **THEN** Nova senha e Confirmação possuem rótulos persistentes sem alterar o envio ou a política de senha

### Requirement: Administração lista e consulta usuários sem credenciais
O Xano DEVE (MUST) fornecer listagem e detalhe de usuários somente a Administrador autenticado e sem pendência. As respostas DEVEM (MUST) conter somente ID, nome, e-mail, perfil e Loja quando aplicável; senha, hash, token e material de credencial NÃO DEVEM (MUST NOT) aparecer.

#### Scenario: Consulta autorizada
- **WHEN** Administrador consulta usuários ou o detalhe de um usuário
- **THEN** recebe somente dados cadastrais públicos necessários à gestão

#### Scenario: Consulta indevida
- **WHEN** outro perfil, sessão pendente ou pessoa não autenticada consulta contratos administrativos
- **THEN** o Xano rejeita sem expor usuários

### Requirement: Administrador edita cadastro e perfil canônico
O Xano DEVE (MUST) permitir a Administrador alterar nome, e-mail único e perfil entre `gerente`, `tecnico`, `diretoria` e `administrador`, preservando ID e referências históricas. Gerente DEVE (MUST) manter Loja existente; novo vínculo ou transferência exige Loja `Ativa`. Os demais perfis DEVEM (MUST) ficar sem vínculo de Loja.

#### Scenario: Transferência de Gerente
- **WHEN** Administrador altera a Loja de um Gerente para outra Loja `Ativa`
- **THEN** o ID e fatos históricos permanecem e o novo escopo vale para operações futuras

#### Scenario: Alteração de perfil
- **WHEN** Administrador altera perfil canônico e informa associação de Loja compatível
- **THEN** o novo perfil passa a reger operações futuras sem reescrever chamados ou interações anteriores

#### Scenario: E-mail duplicado ou perfil inválido
- **WHEN** edição informa e-mail já usado por outro usuário ou perfil não canônico
- **THEN** o Xano rejeita sem modificar o usuário

#### Scenario: Gerente sem Loja válida ou destino Inativo
- **WHEN** edição deixaria Gerente sem Loja existente ou mudaria seu vínculo para Loja `Inativa`
- **THEN** o Xano rejeita sem modificar o usuário

#### Scenario: Edição cadastral de Gerente em Loja Inativa
- **WHEN** Gerente já vinculado a Loja que se tornou `Inativa` recebe edição válida de nome ou e-mail sem mudar de Loja
- **THEN** o Xano preserva seu vínculo e permite a edição sem criar associação nova

### Requirement: Mudança de perfil preserva responsabilidades técnicas
O Xano DEVE (MUST) impedir que usuário deixe de ser `tecnico` enquanto for responsável atual por chamado. Referências históricas de solicitante, autor, Técnico anterior ou novo DEVEM (MUST) permanecer intactas em mudanças permitidas.

#### Scenario: Técnico com chamado atribuído
- **WHEN** Administrador tenta mudar para outro perfil um Técnico ainda responsável por chamado
- **THEN** o Xano bloqueia a mudança e preserva usuário e chamado

#### Scenario: Técnico sem responsabilidade atual
- **WHEN** um Técnico não é responsável atual por chamado e a edição é válida
- **THEN** a mudança de perfil é permitida sem alterar interações históricas

### Requirement: Último Administrador não perde o perfil
O Xano DEVE (MUST) rejeitar mudança de perfil que deixe o sistema sem Administrador, inclusive edição da própria conta. Se outro Administrador válido permanecer, a mudança DEVE (MUST) ser permitida conforme as demais validações. Operação bloqueada NÃO DEVE (MUST NOT) causar alteração parcial, mesmo sob chamadas concorrentes.

#### Scenario: Último Administrador muda o próprio perfil
- **WHEN** o único Administrador tenta mudar a própria conta para Gerente, Técnico ou Diretoria
- **THEN** o Xano rejeita a edição e mantém o perfil `administrador`

#### Scenario: Outro Administrador muda o último perfil
- **WHEN** um Administrador tenta mudar o perfil da única conta Administrador restante
- **THEN** o Xano rejeita a edição sem modificar a conta

#### Scenario: Outro Administrador permanece
- **WHEN** um Administrador muda de perfil e outra conta Administrador válida permanece
- **THEN** o Xano permite a mudança se todas as demais validações forem atendidas

#### Scenario: Duas mudanças simultâneas
- **WHEN** duas requisições tentam mudar simultaneamente os perfis das duas últimas contas Administrador
- **THEN** no máximo uma mudança é concluída e ao menos uma conta mantém perfil `administrador`, sem escrita parcial

### Requirement: Exclusão física de usuário respeita identidade e histórico
O Xano DEVE (MUST) excluir fisicamente usuário somente sem chamados, interações, atribuições, preferências ou outro vínculo ou histórico impeditivo. Administrador NÃO DEVE (MUST NOT) excluir a própria conta nem o último Administrador. Não há exclusão em cascata.

#### Scenario: Usuário sem dependências
- **WHEN** Administrador exclui outro usuário existente sem dependências impeditivas
- **THEN** somente esse usuário é removido

#### Scenario: Própria conta ou último Administrador
- **WHEN** Administrador tenta excluir sua própria conta ou o último Administrador
- **THEN** o Xano rejeita sem remover o usuário

#### Scenario: Usuário referenciado
- **WHEN** usuário possui chamado, interação, atribuição, preferência ou outro histórico impeditivo
- **THEN** o Xano retorna erro funcional e preserva todos os registros

#### Scenario: Exclusão concorrente dos dois últimos Administradores
- **WHEN** duas requisições tentam excluir simultaneamente as duas últimas contas Administrador, sem atingir a própria conta de quem solicita
- **THEN** no máximo uma exclusão é concluída e ao menos uma conta Administrador permanece
