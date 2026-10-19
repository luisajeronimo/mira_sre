# Proposal: Sidebar global por perfil

## Why

A casca autenticada atual repete a composição de navegação entre páginas e
oferece somente uma topbar. A navegação lateral compartilhada torna os destinos
autorizados descobríveis por perfil sem transformar a interface em autoridade
de autorização.

Também é necessário separar a consulta de monitoramento do endpoint genérico
de ativos: ele mantém acesso do Gerente à própria Loja, enquanto a jornada de
monitoramento aprovada é exclusiva de Técnico, Diretoria e Administrador.

## What Changes

- Adicionar uma única sidebar desktop reutilizável à casca autenticada, com
  itens de navegação configurados centralmente por perfil. O MIRA é uma
  aplicação Web desktop e não oferece drawer ou controles mobile.
- Exibir somente `/inicio` para Gerente; `/inicio` e `/monitoramento` para
  Técnico e Diretoria; e `/inicio`, `/monitoramento` e
  `/administracao/usuarios` para Administrador.
- Tratar `/inicio` como a listagem canônica de chamados. Manter `/chamados`
  como redirecionamento protegido de compatibilidade para `/inicio`, sem
  descartar filtros em memória; preservar `/chamados/novo` e
  `/chamados/[chamado_id]` sem itens na sidebar.
- Manter sidebar ausente em `/login`, `/primeiro-acesso` e enquanto a sessão
  estiver sendo revalidada.
- Disponibilizar o logotipo oficial como asset da aplicação a partir de
  `docs/design/references/logo.svg`, sem redesenho ou substituição visual.
- Criar contrato Xano dedicado para a consulta de monitoramento, autorizado
  somente para Técnico, Diretoria e Administrador, preservando
  `GET /ativos_referencia` e seus consumidores atuais.
- Aplicar guards Reflex coerentes com a navegação, sem substituir a autorização
  efetiva no Xano.

## Capabilities

### New Capabilities

- `navegacao-lateral-perfis`: casca autenticada reutilizável para Web desktop e
  orientada pelo perfil confirmado da sessão.

### Modified Capabilities

- `frontend-sessao-navegacao`: proteção e jornada de `/monitoramento` passam a
  refletir o escopo aprovado e a casca autenticada passa a ter navegação lateral.
- `autorizacao-perfis`: consulta dedicada de monitoramento recebe autorização
  explícita no Xano para os três perfis globais permitidos.

## Impact

- Reflex: componentes de layout, State de sessão, páginas autenticadas,
  monitoramento, cliente Service Desk, asset público do logo e testes de rotas
  e sessão.
- Xano: nova API e função de listagem de monitoramento, com validação
  XanoScript e publicação seletiva futura.
- Não altera dados operacionais, contratos de chamados ou o endpoint genérico
  `GET /ativos_referencia`. A URL legada `/chamados` continua disponível como
  redirecionamento de compatibilidade.

## Decisões humanas pendentes

Nenhuma. A matriz de itens, a estratégia exclusivamente desktop, a rota
canônica da listagem, a integração do logo e a separação do contrato de
monitoramento foram aprovadas para esta change.
