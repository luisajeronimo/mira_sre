## MODIFIED Requirements

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
