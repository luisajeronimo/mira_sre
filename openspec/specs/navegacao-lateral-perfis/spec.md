# navegacao-lateral-perfis Specification

## Purpose

Definir a casca de navegação lateral do MIRA para tornar destinos autorizados
descobríveis por perfil, sem substituir a autorização aplicada pelo Xano.

## Requirements

### Requirement: Casca autenticada apresenta navegação lateral configurada por perfil
O Reflex DEVE (MUST) apresentar uma única navegação lateral desktop reutilizável
após confirmar sessão e perfil oficial. A configuração central DEVE (MUST)
exibir somente `/inicio` para Gerente; `/inicio`, `/monitoramento` e
`/indicadores/disponibilidade` para Técnico e Diretoria; e esses três destinos
mais `/administracao/gestao` para Administrador. O destino Administração DEVE (MUST)
abrir diretamente a gestão consolidada. A sidebar NÃO DEVE (MUST NOT)
apresentar "Chamados solicitados" como destino separado; a listagem canônica
permanece em `/inicio`.

#### Scenario: Matriz de navegação autenticada
- **WHEN** cada perfil oficial conclui a confirmação de identidade
- **THEN** a sidebar mostra somente os destinos permitidos pela matriz aprovada e o Administrador chega diretamente a `/administracao/gestao`

#### Scenario: Navegação sem listagem duplicada
- **WHEN** um perfil oficial conclui a confirmação de identidade
- **THEN** a sidebar oferece a listagem de chamados somente por "Início"

#### Scenario: Perfil inválido ou sessão não confirmada
- **WHEN** a sessão não está confirmada ou não possui perfil oficial
- **THEN** a interface não renderiza a sidebar nem destinos autenticados

#### Scenario: Inclusão futura de destino
- **WHEN** uma mudança futura adiciona destino à configuração central
- **THEN** a visibilidade por perfil é definida no mesmo registro sem duplicar
  listas de navegação nas páginas

#### Scenario: Diretoria encontra Indicadores
- **WHEN** um perfil operacional autenticado consulta a sidebar
- **THEN** Técnico, Diretoria e Administrador encontram Indicadores; Gerente não o recebe

### Requirement: Sidebar não representa a jornada de chamados como destino
A sidebar NÃO DEVE (MUST NOT) apresentar `/chamados`, `/chamados/novo` ou
`/chamados/[chamado_id]` como itens próprios. A listagem é representada pelo
item `/inicio`. A sidebar
NÃO DEVE (MUST NOT) criar rotas, ações ou funcionalidades além das aprovadas.

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
- **WHEN** a rota canônica Reflex atual é `/monitoramento`,
  `/indicadores/disponibilidade` ou `/administracao/gestao`
- **THEN** somente o respectivo item configurado possui indicação visual e
  semântica de ativo

### Requirement: Casca autenticada usa linguagem visual desktop compartilhada
Após a confirmação da sessão, a casca autenticada DEVE (MUST) apresentar
sidebar e topbar em superfícies claras, com identidade da sessão na topbar. O
contexto da página DEVE (MUST) permanecer reconhecível pela navegação e pelo
conteúdo; a topbar NÃO DEVE (MUST NOT) exibir título da rota em nenhum perfil.
A composição DEVE (MUST) usar a identidade visual definida e preservar os
destinos, a matriz de perfis e as rotas já aprovadas.

#### Scenario: Perfil autenticado abre rota protegida
- **WHEN** um perfil oficial confirmado abre uma rota protegida
- **THEN** a interface apresenta a única sidebar desktop existente, uma topbar
  com identidade e saída e o conteúdo em canvas claro, sem criar destino, ação
  ou permissão adicional

#### Scenario: Título da rota fora da topbar
- **WHEN** qualquer perfil oficial navega entre rotas protegidas
- **THEN** a topbar não exibe títulos como Início, Novo chamado, Detalhe do
  chamado, Monitoramento ou Administração de usuários

#### Scenario: Navegação acessível permanece configurada por perfil
- **WHEN** a casca renderiza a navegação para um perfil autenticado
- **THEN** o destino ativo, o foco visível e os rótulos continuam distinguíveis
  sem depender exclusivamente de cor, e somente os itens previstos para o perfil
  são exibidos

#### Scenario: Fluxo público ou revalidação
- **WHEN** a sessão ainda não foi confirmada ou a rota é pública
- **THEN** a interface não apresenta a casca autenticada nem conteúdo protegido

### Requirement: Identificação e saída ficam concentradas na topbar
A casca autenticada DEVE (MUST) apresentar nome, cargo em maiúsculas e a ação
existente de saída uma única vez na topbar. A sidebar NÃO DEVE (MUST NOT)
duplicar identificação ou logout, e a mudança NÃO DEVE (MUST NOT) alterar a
sessão, matriz de navegação ou destinos configurados. A ação de saída DEVE
(MUST) usar o rose primário com contraste adequado.

#### Scenario: Sessão confirmada renderiza a casca
- **WHEN** um perfil oficial confirmado abre uma rota protegida
- **THEN** a topbar apresenta identificação e saída, e a sidebar mantém apenas
  marca e os itens de navegação autorizados
