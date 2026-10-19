# Delta: frontend-sessao-navegacao

## MODIFIED Requirements

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
