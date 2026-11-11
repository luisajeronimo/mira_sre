# Spec Delta

## MODIFIED Requirements

### Requirement: Casca autenticada apresenta navegação lateral configurada por perfil
O Reflex DEVE (MUST) apresentar uma única navegação lateral desktop reutilizável
após confirmar sessão e perfil oficial. A configuração central DEVE (MUST)
exibir somente `/inicio` para Gerente; `/inicio` e `/monitoramento` para
Técnico e Diretoria; e `/inicio`, `/monitoramento` e
`/administracao/gestao` para Administrador. O destino Administração DEVE (MUST)
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
