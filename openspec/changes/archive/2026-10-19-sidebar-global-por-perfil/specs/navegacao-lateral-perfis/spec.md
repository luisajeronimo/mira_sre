# Spec Delta

## Purpose

Definir a casca de navegação lateral do MIRA para tornar destinos autorizados
descobríveis por perfil, sem substituir a autorização aplicada pelo Xano.

## ADDED Requirements

### Requirement: Casca autenticada apresenta navegação lateral configurada por perfil
O Reflex DEVE (MUST) apresentar uma única navegação lateral desktop reutilizável
após confirmar sessão e perfil oficial. A configuração central DEVE (MUST)
exibir somente `/inicio` para Gerente; `/inicio` e `/monitoramento` para
Técnico e Diretoria; e `/inicio`, `/monitoramento` e
`/administracao/usuarios` para Administrador.

#### Scenario: Matriz de navegação autenticada
- **WHEN** cada perfil oficial conclui a confirmação de identidade
- **THEN** a sidebar mostra somente os destinos permitidos pela matriz aprovada

#### Scenario: Perfil inválido ou sessão não confirmada
- **WHEN** a sessão não está confirmada ou não possui perfil oficial
- **THEN** a interface não renderiza a sidebar nem destinos autenticados

#### Scenario: Inclusão futura de destino
- **WHEN** uma mudança futura adiciona destino à configuração central
- **THEN** a visibilidade por perfil é definida no mesmo registro sem duplicar
  listas de navegação nas páginas

### Requirement: Sidebar não representa a jornada de chamados como destino
A sidebar NÃO DEVE (MUST NOT) apresentar `/chamados`, `/chamados/novo` ou
`/chamados/[chamado_id]` como itens próprios. A listagem é representada pelo
item `/inicio`; a sidebar NÃO DEVE (MUST NOT) criar rotas, ações ou
funcionalidades novas.

#### Scenario: Abertura manual de chamado
- **WHEN** Gerente autenticado acessa `/chamados/novo`
- **THEN** a sidebar não cria item de abertura

#### Scenario: Detalhe de chamado
- **WHEN** perfil autorizado acessa `/chamados/[chamado_id]`
- **THEN** a sidebar não cria item de detalhe

### Requirement: Casca exclui fluxos públicos e de revalidação
A sidebar NÃO DEVE (MUST NOT) aparecer em `/login`, `/primeiro-acesso` ou
enquanto a sessão protegida aguarda revalidação. Login, primeiro acesso,
expiração, indisponibilidade e redirecionamentos DEVEM (MUST) preservar os
estados seguros já aprovados.

#### Scenario: Login e primeiro acesso
- **WHEN** visitante acessa `/login` ou usuário pendente acessa `/primeiro-acesso`
- **THEN** a página não renderiza sidebar

#### Scenario: Sessão em revalidação
- **WHEN** rota protegida aguarda a confirmação de `/me`
- **THEN** a interface apresenta somente o estado neutro de carregamento

#### Scenario: Logout
- **WHEN** usuário autenticado aciona logout pela casca
- **THEN** a sessão é descartada e a sidebar deixa de ser apresentada antes da
  próxima rota protegida exigir nova autenticação

### Requirement: Identidade visual e navegação desktop preservadas
A casca DEVE (MUST) reutilizar o logotipo oficial MIRA preservando proporções,
cores e integridade visual. O MIRA DEVE (MUST) oferecer somente a sidebar Web
desktop; drawer, controles e lógica específica de mobile NÃO DEVEM (MUST NOT)
ser renderizados. Foco, item ativo e navegação por teclado DEVEM (MUST) ser
distinguíveis sem depender apenas de cor.

#### Scenario: Logotipo oficial na casca
- **WHEN** a sidebar autenticada é renderizada
- **THEN** ela usa o asset oficial do logotipo sem redesenhá-lo ou substituí-lo
  por texto ou ícone genérico

#### Scenario: Casca Web desktop
- **WHEN** usuário autenticado acessa uma rota protegida
- **THEN** a interface apresenta a única sidebar desktop ao lado do conteúdo,
  sem drawer ou controle de navegação mobile

#### Scenario: Item ativo acessível
- **WHEN** uma rota configurada na navegação é a rota atual
- **THEN** o item correspondente possui indicação visual e semântica de ativo

#### Scenario: Início ativo na jornada canônica de chamados
- **WHEN** a rota canônica Reflex atual é `/inicio`, `/chamados`,
  `/chamados/novo` ou `/chamados/[chamado_id]`
- **THEN** somente o item `Início` possui indicação visual e semântica de ativo,
  embora nenhuma rota de chamados seja exibida como item próprio

#### Scenario: Destinos globais ativos exclusivamente na própria rota
- **WHEN** a rota canônica Reflex atual é `/monitoramento` ou
  `/administracao/usuarios`
- **THEN** somente o respectivo item configurado possui indicação visual e
  semântica de ativo
