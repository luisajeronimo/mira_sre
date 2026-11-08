# Spec Delta

## MODIFIED Requirements

### Requirement: Casca autenticada apresenta navegação lateral configurada por perfil
O Reflex DEVE (MUST) apresentar uma única navegação lateral desktop reutilizável
após confirmar sessão e perfil oficial. A configuração central DEVE (MUST)
exibir somente `/inicio` e `/chamados/solicitados` para Gerente; `/inicio`,
`/chamados/solicitados` e `/monitoramento` para Técnico e Diretoria; e
`/inicio`, `/chamados/solicitados`, `/monitoramento` e
`/administracao/usuarios` para Administrador. O item `/chamados/solicitados`
DEVE (MUST) ter o rótulo "Chamados solicitados", e sua visibilidade NÃO DEVE
(MUST NOT) ser tratada como autorização, que permanece no Xano pelo vínculo com
cada chamado.

#### Scenario: Matriz de navegação autenticada
- **WHEN** cada perfil oficial conclui a confirmação de identidade
- **THEN** a sidebar mostra somente os destinos permitidos pela matriz aprovada

#### Scenario: Chamados solicitados para todos os perfis oficiais
- **WHEN** Gerente, Técnico, Diretoria ou Administrador conclui a confirmação de
  identidade
- **THEN** a sidebar apresenta "Chamados solicitados", que leva a
  `/chamados/solicitados`, inclusive para usuário sem chamados associados

#### Scenario: Chamados solicitados ativo nas próprias rotas
- **WHEN** a rota canônica Reflex atual é `/chamados/solicitados` ou
  `/chamados/solicitados/[chamado_id]`
- **THEN** somente o item "Chamados solicitados" possui indicação visual e
  semântica de ativo

#### Scenario: Perfil inválido ou sessão não confirmada
- **WHEN** a sessão não está confirmada ou não possui perfil oficial
- **THEN** a interface não renderiza a sidebar nem destinos autenticados

#### Scenario: Inclusão futura de destino
- **WHEN** uma mudança futura adiciona destino à configuração central
- **THEN** a visibilidade por perfil é definida no mesmo registro sem duplicar
  listas de navegação nas páginas

### Requirement: Sidebar não representa a jornada de chamados como destino
A sidebar NÃO DEVE (MUST NOT) apresentar `/chamados`, `/chamados/novo`,
`/chamados/[chamado_id]` ou `/chamados/solicitados/[chamado_id]` como itens
próprios. A listagem é representada pelo item `/inicio`; `/chamados/solicitados`
é o único destino da jornada de chamados aprovado como item próprio. A sidebar
NÃO DEVE (MUST NOT) criar rotas, ações ou funcionalidades além das aprovadas.

#### Scenario: Abertura manual de chamado
- **WHEN** Gerente autenticado acessa `/chamados/novo`
- **THEN** a sidebar não cria item de abertura

#### Scenario: Detalhe de chamado
- **WHEN** perfil autorizado acessa `/chamados/[chamado_id]`
- **THEN** a sidebar não cria item de detalhe

#### Scenario: Detalhe de chamado solicitado
- **WHEN** usuário autenticado acessa `/chamados/solicitados/[chamado_id]`
- **THEN** a sidebar não cria item de detalhe
