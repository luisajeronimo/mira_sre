# Tasks

## 1. Navegação compartilhada e identidade visual

- [x] 1.1 Copiar `docs/design/references/logo.svg` para `assets/mira-logo.svg` sem alteração visual e adicionar teste que verifique a correspondência do asset com a referência oficial.
- [x] 1.2 Ajustar a configuração central para a matriz desktop aprovada sem `Chamados`, e verificar em teste unitário a visibilidade por perfil e a ausência de rotas de chamados na sidebar.
- [x] 1.3 Evoluir a casca autenticada para uma única sidebar Web desktop acessível, reutilizando a configuração central e removendo drawer, controles, breakpoints, estado e testes específicos de mobile.
- [x] 1.4 Tornar `/inicio` a lista canônica e `/chamados` um redirecionamento protegido compatível, preservando filtros em memória, sem alterar login, primeiro acesso, revalidação, `/chamados/novo` ou `/chamados/[chamado_id]`.

## 2. Proteção de monitoramento

- [x] 2.1 Ajustar o guard Reflex e o cliente de monitoramento para usar a matriz aprovada e o contrato dedicado, e verificar que Gerente é redirecionado para `/inicio` sem iniciar consulta de monitoramento.
- [x] 2.2 Criar a função e a API Xano `GET /monitoramento/ativos` no MIRA Service Desk, autorizando somente Técnico, Diretoria e Administrador, e verificar XanoScript/MCP e os cenários HTTP 200, 401 e 403 sem alterar `GET /ativos_referencia`.
  - Validação HTTP por perfil aprovada por decisão humana em 19/10/2026.

## 3. Verificação integrada

- [x] 3.1 Executar os testes Python focados de sessão, rotas, layout e monitoramento e a suíte completa, verificando a matriz desktop, rota canônica e compatibilidade, logout, revalidação, logo e autorização.
- [x] 3.2 Compilar o Reflex e verificar manualmente a sidebar desktop após sessão confirmada, incluindo item ativo, ausência da sidebar em fluxos públicos/revalidação e logout.
  - Validação visual no Reflex aprovada por decisão humana em 19/10/2026.
- [x] 3.3 Executar validação XanoScript, `openspec validate sidebar-global-por-perfil --strict --no-interactive` e `git diff --check`; não publicar alterações Xano sem autorização humana explícita.
