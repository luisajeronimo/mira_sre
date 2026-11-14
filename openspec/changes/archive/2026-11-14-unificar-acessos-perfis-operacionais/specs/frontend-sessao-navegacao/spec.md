## ADDED Requirements

### Requirement: Jornadas operacionais usam a mesma matriz de acesso
O Reflex DEVE (MUST) aplicar a mesma matriz operacional a Técnico, Diretoria e Administrador em `/inicio`, `/chamados/novo`, detalhe, monitoramento, indicadores e aliases operacionais. Gestão e aliases administrativos DEVEM (MUST) continuar exclusivos do Administrador. A sessão DEVE (MUST) ser confirmada antes de carregar dados.

#### Scenario: Abertura e indicadores por perfil operacional
- **WHEN** Técnico, Diretoria ou Administrador acessa uma dessas rotas com sessão concluída
- **THEN** a mesma jornada operacional é carregada, preservando identidade e perfil reais

#### Scenario: Alias operacional
- **WHEN** um perfil operacional acessa `/tecnico` ou `/diretoria`
- **THEN** é direcionado à jornada operacional canônica sem restrição adicional pelo nome legado

#### Scenario: Gestão e primeiro acesso
- **WHEN** outro perfil acessa Gestão ou uma sessão possui troca pendente
- **THEN** os gates administrativos e de primeiro acesso continuam negando o conteúdo indevido

## MODIFIED Requirements

### Requirement: Login público usa identidade visual sem alterar autenticação
A página `/login` DEVE (MUST) apresentar canvas claro, superfície desktop em
duas colunas, contexto visual do produto e formulário alinhado à linguagem rose
do MIRA. O formulário DEVE (MUST) destacar o logotipo oficial reutilizado de
`assets/mira-logo.svg` e manter os mesmos campos de e-mail e senha,
mensagens, carregamento e envio existentes. A mudança NÃO DEVE (MUST NOT)
alterar State, contrato Xano, autenticação, rota ou redirecionamento, nem criar
ações ilustrativas sem comportamento aprovado.

A página pública de login NÃO DEVE (MUST NOT) apresentar breadcrumbs.

#### Scenario: Visitante abre o login
- **WHEN** um visitante acessa `/login`
- **THEN** visualiza o painel dividido e o logotipo oficial destacado acima do
  mesmo formulário funcional de e-mail e senha

#### Scenario: Login apresenta erro ou carregamento
- **WHEN** a autenticação existente está carregando ou retorna uma mensagem
- **THEN** o botão e a mensagem preservam o mesmo estado funcional em
  apresentação coerente com o padrão visual compartilhado

#### Scenario: Login sem trilha de navegação
- **WHEN** visitante acessa `/login`
- **THEN** o formulário é apresentado sem breadcrumbs, mantendo os mesmos campos e eventos de autenticação
