## Why

O Xano já fornece autenticação, identidade atual e autorização consolidadas, mas o MIRA ainda não possui uma aplicação Reflex capaz de consumir esses contratos e manter uma sessão de usuário. Esta change cria a casca autenticada necessária para que as próximas jornadas web sejam construídas sem duplicar regras de segurança ou de negócio no frontend.

## What Changes

- Criar a aplicação Reflex e uma tela pública de login que envie as credenciais ao `POST /login` do Xano.
- Centralizar o acesso HTTP ao Xano, incluindo uma URL base específica de autenticação, independente das URLs dos grupos operacionais, timeout, cabeçalho de autenticação e tratamento uniforme de respostas.
- Manter o token do Xano somente no estado backend da sessão Reflex, sem persistência duradoura, exposição em componentes, logs ou mensagens e sem `LocalStorage`, `SessionStorage`, cookie próprio ou mecanismo equivalente.
- Consumir `GET /me` para estabelecer e revalidar a identidade autenticada apresentada pela aplicação.
- Representar no estado do Reflex somente os dados públicos da identidade atual: `id`, `nome`, `email`, `role` e `lojas_id` quando aplicável.
- Tratar token ausente, inválido ou expirado encerrando a sessão local e redirecionando para o login, sem refresh token ou renovação automática; as oito horas são apenas a validade máxima do token no Xano e não garantem a sobrevivência do State Reflex.
- Disponibilizar logout que descarte o token e a identidade local e retorne ao login.
- Proteger as páginas autenticadas por carregamento de rota e redirecionar usuários anônimos ao login.
- Criar uma navegação mínima e páginas iniciais neutras para `gerente`, `tecnico` e `diretoria`, sem antecipar Service Desk, dashboards ou indicadores.
- Redirecionar o usuário autenticado para a página inicial correspondente ao perfil oficial retornado por `/me`.
- Preservar integralmente os contratos e as regras consolidadas de autenticação e autorização no Xano.

## Capabilities

### New Capabilities

- `frontend-sessao-navegacao`: login no Reflex, sessão autenticada, cliente Xano, identidade atual, expiração, logout, proteção de rotas, navegação e redirecionamento por perfil.

### Modified Capabilities

Nenhuma. As capacidades `autenticacao-usuarios` e `autorizacao-perfis` serão apenas consumidas, sem alteração de requisitos.

## Impact

- Nova estrutura da aplicação Reflex em `app/`, incluindo páginas, componentes, serviços e estado.
- Configuração local de `XANO_AUTH_BASE_URL` para o grupo de autenticação, preservando `XANO_BASE_URL` para os componentes operacionais existentes, além das dependências Python necessárias ao cliente HTTP e aos testes do frontend.
- Consumo dos contratos existentes `POST /login` e `GET /me`; nenhum endpoint, tabela, função ou regra do Xano será alterado.
- Criação das rotas `/`, `/login`, `/gerente`, `/tecnico` e `/diretoria` como fundação de navegação para funcionalidades futuras.
- Simulator, Fiscal, telemetria, heartbeat, chamados, dashboards e indicadores permanecem inalterados.
