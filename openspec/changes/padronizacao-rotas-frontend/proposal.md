# Proposal: Padronização de rotas do frontend

## Why

As rotas Reflex atuais misturam a funcionalidade acessada com o perfil que a
acessa. Isso produz URLs como `/gerente` e `/tecnico` para jornadas de chamados
que já possuem escopos e permissões consolidados no Xano. A navegação deve usar
nomes funcionais sem unificar componentes, States, contratos ou autorização.

## What Changes

- Tornar `/inicio` o destino pós-login, pós-primeiro-acesso e da raiz para os
  quatro perfis humanos autenticados.
- Registrar rotas canônicas por funcionalidade: `/chamados`,
  `/chamados/novo`, `/chamados/[chamado_id]` e `/administracao/usuarios`.
- Resolver `/inicio`, listagem e detalhe de chamados pelo perfil confirmado:
  Gerente reutiliza a jornada local; Técnico, Diretoria e Administrador
  reutilizam a jornada global existente.
- Manter aliases transitórios das rotas antigas somente como redirecionamentos
  protegidos, preservando `chamado_id` quando aplicável.
- Manter `/`, `/login`, `/primeiro-acesso` e `/monitoramento`; preservar o
  acesso atual de monitoramento para sessões autenticadas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-sessao-navegacao`: destinos autenticados, proteção de rotas,
  aliases legados e navegação comum passam a usar URLs funcionais.
- `frontend-chamados-gerente`: a jornada Reflex local usa as rotas canônicas
  de chamados, sem alterar seus contratos ou capacidades.
- `chamados-fila-atribuicao-tecnica`: a jornada Reflex global usa as rotas
  canônicas de chamados, preservando a tratativa já consolidada.
- `administracao-usuarios`: a interface administrativa existente é exposta em
  `/administracao/usuarios`, sem alterar o contrato administrativo.

## Impact

- Afeta o registro Reflex, guards, destinos da sessão, links internos e testes
  de rotas/sessão/navegação.
- Não altera APIs, XanoScript, banco, automações ou permissões do Xano. Em
  particular, endpoints como `/gerente/chamados` e `/tecnico/chamados`
  continuam sendo contratos de backend e não acompanham esta mudança.
- Não cria dashboards, menu/sidebar, tela intermediária, redesign ou
  unificação dos States de Gerente e da fila global.
