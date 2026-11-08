# Spec Delta

## MODIFIED Requirements

### Requirement: Casca autenticada apresenta navegação lateral configurada por perfil
O Reflex DEVE (MUST) apresentar uma única navegação lateral desktop reutilizável após confirmar sessão e perfil oficial. A configuração central DEVE (MUST) exibir somente `/inicio` para Gerente; `/inicio` e `/monitoramento` para Técnico e Diretoria; e `/inicio`, `/monitoramento` e `/administracao/gestao` para Administrador. O destino Administração DEVE (MUST) abrir diretamente a gestão consolidada.

#### Scenario: Matriz de navegação autenticada
- **WHEN** cada perfil oficial conclui a confirmação de identidade
- **THEN** a sidebar mostra somente os destinos permitidos pela matriz aprovada e o Administrador chega diretamente a `/administracao/gestao`

#### Scenario: Perfil inválido ou sessão não confirmada
- **WHEN** a sessão não está confirmada ou não possui perfil oficial
- **THEN** a interface não renderiza a sidebar nem destinos autenticados

#### Scenario: Inclusão futura de destino
- **WHEN** uma mudança futura adiciona destino à configuração central
- **THEN** a visibilidade por perfil é definida no mesmo registro sem duplicar listas de navegação nas páginas

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
  `/administracao/gestao`
- **THEN** somente o respectivo item configurado possui indicação visual e
  semântica de ativo
