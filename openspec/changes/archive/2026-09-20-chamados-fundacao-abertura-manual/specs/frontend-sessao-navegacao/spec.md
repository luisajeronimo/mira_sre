## MODIFIED Requirements

### Requirement: Navegação e destino inicial seguem o perfil oficial
O sistema DEVE (MUST) fornecer uma casca de navegação compatível com o perfil confirmado por `/me`. Para o Gerente, a casca DEVE (MUST) incluir os destinos funcionais de listagem e abertura de chamados introduzidos pela capacidade `frontend-chamados-gerente`; para Técnico e Diretoria, as páginas iniciais permanecem neutras. A casca NÃO DEVE (MUST NOT) apresentar fila técnica, tratamento, dashboards ou indicadores nesta change.

#### Scenario: Entrada de Gerente
- **WHEN** `/me` confirma o perfil `gerente`
- **THEN** o Reflex direciona o usuário para `/gerente`, apresenta a listagem básica dos chamados da Loja e disponibiliza a navegação para abrir chamado

#### Scenario: Entrada de Técnico
- **WHEN** `/me` confirma o perfil `tecnico`
- **THEN** o Reflex direciona o usuário para `/tecnico` e apresenta uma página inicial neutra identificada para esse perfil

#### Scenario: Entrada de Diretoria
- **WHEN** `/me` confirma o perfil `diretoria`
- **THEN** o Reflex direciona o usuário para `/diretoria` e apresenta uma página inicial neutra identificada para esse perfil

#### Scenario: Acesso à raiz
- **WHEN** um usuário acessa `/`
- **THEN** o Reflex direciona para `/login` se não houver sessão confirmada ou para a página inicial de seu perfil se a sessão for válida

#### Scenario: Gerente navega pela jornada de chamados
- **WHEN** um Gerente com sessão confirmada usa a casca autenticada
- **THEN** ele pode acessar a listagem, a abertura e o detalhe de chamados sem receber destinos de fila técnica, tratamento, dashboards ou indicadores

#### Scenario: Usuário acessa página inicial de outro perfil
- **WHEN** um usuário autenticado tenta acessar diretamente a página inicial ou uma rota funcional reservada a outro perfil
- **THEN** o Reflex não apresenta o conteúdo dessa página e o redireciona para a página inicial do seu próprio perfil
