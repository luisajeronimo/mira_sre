# Spec Delta

## MODIFIED Requirements

### Requirement: Páginas autenticadas possuem proteção de rota
O sistema DEVE (MUST) proteger todas as rotas funcionais e verificar a sessão no carregamento, mantendo `/login` como pública. Enquanto a troca obrigatória estiver pendente, qualquer rota funcional canônica ou alias legado DEVE redirecionar para `/primeiro-acesso` sem renderizar conteúdo funcional. Sem sessão válida, a rota protegida DEVE redirecionar para `/login`. Depois da troca, `/primeiro-acesso` DEVE redirecionar para `/inicio`.

#### Scenario: Acesso direto sem sessão
- **WHEN** um visitante acessa `/inicio`, `/chamados`, `/chamados/novo`, `/chamados/[chamado_id]`, `/administracao/usuarios`, `/monitoramento` ou alias legado
- **THEN** o Reflex não renderiza conteúdo protegido e redireciona para `/login`

#### Scenario: Rota funcional com troca pendente
- **WHEN** usuário autenticado com troca pendente acessa rota funcional canônica ou alias legado
- **THEN** o Reflex revalida a identidade e redireciona para `/primeiro-acesso`

#### Scenario: Rota de primeiro acesso pendente
- **WHEN** usuário autenticado com troca pendente acessa `/primeiro-acesso`
- **THEN** o Reflex revalida `/me`, permanece nessa rota e não emite redirecionamento para ela própria

#### Scenario: Rota de primeiro acesso concluído
- **WHEN** usuário autenticado sem troca pendente acessa `/primeiro-acesso`
- **THEN** o Reflex o redireciona para `/inicio`

#### Scenario: Visitante acessa página autenticada
- **WHEN** um visitante sem token de sessão acessa uma rota funcional canônica ou um alias legado
- **THEN** o Reflex não apresenta conteúdo autenticado e redireciona para `/login`

#### Scenario: Usuário autenticado acessa login
- **WHEN** um usuário com sessão confirmada acessa `/login`
- **THEN** o Reflex redireciona para `/primeiro-acesso` se houver pendência ou para `/inicio` se a identidade for válida

#### Scenario: Sessão em revalidação
- **WHEN** uma página protegida aguarda a resposta de `GET /me`
- **THEN** o Reflex apresenta estado neutro de carregamento e não renderiza antecipadamente conteúdo autenticado

#### Scenario: Sessão expirada durante revalidação
- **WHEN** a revalidação de uma rota protegida recebe rejeição de autenticação
- **THEN** o Reflex limpa a sessão local e redireciona para `/login`, sem renovar token

### Requirement: URLs canônicas representam funcionalidades
O Reflex DEVE (MUST) registrar `/inicio` como a URL canônica da listagem de
chamados por perfil e manter `/chamados` como redirecionamento protegido de
compatibilidade para `/inicio`. O redirecionamento NÃO DEVE (MUST NOT) limpar
filtros em memória da sessão. `/chamados/novo`, `/chamados/[chamado_id]` e
`/administracao/usuarios` permanecem rotas funcionais; `/chamados/novo` DEVE
(MUST) ser resolvida como rota estática antes de `/chamados/[chamado_id]`.
`/`, `/login` e `/primeiro-acesso` mantêm suas responsabilidades atuais.
`/monitoramento` DEVE (MUST) permitir somente Técnico, Diretoria e
Administrador depois da revalidação; Gerente é redirecionado para `/inicio` sem
carregar dados de monitoramento.

#### Scenario: Link legado da listagem
- **WHEN** perfil autenticado acessa `/chamados`
- **THEN** o Reflex revalida a sessão e redireciona para `/inicio` sem renderizar
  uma segunda listagem ou descartar seus filtros em memória

#### Scenario: Rota estática de abertura
- **WHEN** Gerente autenticado acessa `/chamados/novo`
- **THEN** o Reflex carrega o formulário de abertura, e não interpreta `novo`
  como `chamado_id`

#### Scenario: Monitoramento preservado
- **WHEN** Técnico, Diretoria ou Administrador com sessão revalidada acessa
  `/monitoramento`
- **THEN** o Reflex preserva a jornada de monitoramento existente após aplicar
  a autorização aprovada para a rota

#### Scenario: Monitoramento por perfil permitido
- **WHEN** Técnico, Diretoria ou Administrador com sessão revalidada acessa
  `/monitoramento`
- **THEN** o Reflex carrega a jornada de monitoramento existente

#### Scenario: Gerente acessa monitoramento diretamente
- **WHEN** Gerente com sessão revalidada acessa `/monitoramento`
- **THEN** o Reflex redireciona para `/inicio` sem consultar o contrato de
  monitoramento
