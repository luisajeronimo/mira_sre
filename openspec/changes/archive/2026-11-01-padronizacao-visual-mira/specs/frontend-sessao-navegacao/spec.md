# Spec Delta

## ADDED Requirements

### Requirement: Página inicial global aplica o padrão visual compartilhado
A jornada global em `/inicio` para Técnico, Diretoria e Administrador DEVE
(MUST) apresentar cabeçalho, controles, filtros e listagem existentes com a
linguagem visual compartilhada de tipografia, superfícies, espaçamento, bordas
e ações. A alteração DEVE (MUST) preservar os dados, filtros, ordenação,
escopos rápidos e ações funcionais existentes.

#### Scenario: Perfil global abre a página inicial
- **WHEN** Técnico, Diretoria ou Administrador autenticado acessa `/inicio`
- **THEN** a página apresenta a mesma fila global autorizada em canvas claro,
  com cabeçalho de página, filtros organizados e tabela legível em superfície
  separada

#### Scenario: Controle existente recebe estilo compartilhado
- **WHEN** um controle existente da fila está disponível, ativo, desabilitado,
  em foco ou em carregamento
- **THEN** sua apresentação torna o estado distinguível e mantém o mesmo evento,
  valor, rótulo e disponibilidade funcional anteriores

#### Scenario: Perfil sem jornada global
- **WHEN** Gerente autenticado acessa `/inicio`
- **THEN** a jornada local existente continua sendo apresentada sem receber a
  fila global ou seus controles

### Requirement: Status preservam valor e recebem apresentação semântica
Status e visibilidades já retornados pelo sistema DEVERÃO (MUST) ser exibidos
em maiúsculas com badge semântico consistente, inclusive estados operacionais
online e offline. A apresentação NÃO DEVE (MUST NOT) alterar valor, contrato,
autorização ou persistência.

#### Scenario: Estado existente é apresentado
- **WHEN** a interface renderiza um status ou visibilidade já recebido
- **THEN** o texto aparece em maiúsculas e a cor semântica é acompanhada pelo
  próprio rótulo, sem modificação do valor de origem

### Requirement: Login público usa identidade visual sem alterar autenticação
A página `/login` DEVE (MUST) apresentar canvas claro, superfície desktop em
duas colunas, contexto visual do produto e formulário alinhado à linguagem rose
do MIRA. O formulário DEVE (MUST) destacar o logotipo oficial reutilizado de
`docs/design/references/logo.svg` e manter os mesmos campos de e-mail e senha,
mensagens, carregamento e envio existentes. A mudança NÃO DEVE (MUST NOT)
alterar State, contrato Xano, autenticação, rota ou redirecionamento, nem criar
ações ilustrativas sem comportamento aprovado.

#### Scenario: Visitante abre o login
- **WHEN** um visitante acessa `/login`
- **THEN** visualiza o painel dividido e o logotipo oficial destacado acima do
  mesmo formulário funcional de e-mail e senha

#### Scenario: Login apresenta erro ou carregamento
- **WHEN** a autenticação existente está carregando ou retorna uma mensagem
- **THEN** o botão e a mensagem preservam o mesmo estado funcional em
  apresentação coerente com o padrão visual compartilhado
