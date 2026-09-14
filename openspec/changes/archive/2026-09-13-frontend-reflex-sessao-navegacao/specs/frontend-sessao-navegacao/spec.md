## Purpose

Definir o comportamento observável da casca autenticada do MIRA no Reflex, incluindo login, sessão, identidade atual, proteção de páginas e navegação pelos três perfis oficiais.

## ADDED Requirements

### Requirement: Login do Reflex delega autenticação ao Xano
O sistema DEVE (MUST) oferecer uma tela pública de login que envie o e-mail e a senha informados ao contrato consolidado `POST /login` do Xano, sem validar credenciais por conta própria nem oferecer cadastro, recuperação de senha ou renovação de sessão.

#### Scenario: Login com credenciais válidas
- **WHEN** um usuário informa credenciais válidas na tela de login
- **THEN** o Reflex envia as credenciais ao Xano, recebe o token de autenticação e consulta `GET /me` antes de considerar a sessão autenticada

#### Scenario: Login com credenciais inválidas
- **WHEN** o Xano rejeita as credenciais informadas
- **THEN** o Reflex permanece na tela de login, não cria sessão autenticada e apresenta uma mensagem genérica que não distingue e-mail inexistente de senha incorreta

#### Scenario: Envio repetido durante autenticação
- **WHEN** uma tentativa de login ainda está em processamento
- **THEN** a interface indica o processamento e impede novos envios concorrentes do mesmo formulário

### Requirement: Cliente do Reflex centraliza o acesso ao Xano
O sistema DEVE (MUST) realizar as chamadas de autenticação do Reflex ao Xano por um contrato HTTP centralizado, utilizando uma URL base específica de autenticação configurada fora do código, independente das bases de grupos operacionais, timeout definido e o token da sessão nas operações autenticadas.

#### Scenario: Requisição autenticada
- **WHEN** o Reflex chama `GET /me` para uma sessão que possui token
- **THEN** a requisição usa `XANO_AUTH_BASE_URL` e envia o token no formato exigido pelo contrato do Xano

#### Scenario: Base operacional configurada para outro grupo
- **WHEN** `XANO_BASE_URL` aponta para um grupo operacional que não contém autenticação
- **THEN** `POST /login` e `GET /me` continuam usando exclusivamente `XANO_AUTH_BASE_URL`, sem alterar a configuração dos componentes operacionais

#### Scenario: Configuração ausente
- **WHEN** `XANO_AUTH_BASE_URL` não está configurada para a aplicação
- **THEN** o Reflex falha de forma explícita sem tentar acessar um endpoint específico de outro ambiente

#### Scenario: Xano temporariamente indisponível
- **WHEN** uma chamada ao Xano falha por timeout, conexão ou erro temporário de servidor
- **THEN** o Reflex informa que o serviço está indisponível e não trata essa falha como credencial inválida ou sessão expirada

### Requirement: Token permanece restrito à sessão autenticada sem persistência duradoura
O sistema DEVE (MUST) manter o token retornado pelo Xano somente enquanto o State backend da sessão Reflex correspondente estiver disponível e NÃO DEVE (MUST NOT) expô-lo em componentes visuais, mensagens, URLs ou logs da aplicação. O sistema NÃO DEVE (MUST NOT) persistir ou recuperar o token por `LocalStorage`, `SessionStorage`, cookie próprio, refresh token, armazenamento durável do State backend ou qualquer outro mecanismo de persistência não aprovado.

#### Scenario: Token recebido após login
- **WHEN** o Xano retorna um token válido
- **THEN** o Reflex o associa somente à sessão atual e o utiliza apenas nas chamadas autenticadas ao Xano

#### Scenario: Renderização da interface autenticada
- **WHEN** a aplicação apresenta a identidade ou a navegação do usuário
- **THEN** nenhum valor do token é enviado como conteúdo renderizado, parâmetro de URL ou mensagem de interface

#### Scenario: Nova sessão de navegador
- **WHEN** o usuário inicia uma nova sessão do navegador após encerrar a anterior
- **THEN** o Reflex não restaura automaticamente o token da sessão encerrada e exige nova autenticação

#### Scenario: State backend perdido ou reiniciado
- **WHEN** o State backend da sessão for perdido ou reiniciado e o token não estiver mais disponível
- **THEN** o Reflex não tenta recuperar o token por outro armazenamento e exige que o usuário se autentique novamente

#### Scenario: Processo Reflex reiniciado
- **WHEN** o processo backend do Reflex é encerrado e iniciado novamente
- **THEN** o token da sessão anterior não é restaurado de arquivo ou outro armazenamento durável

### Requirement: Oito horas são a validade máxima do token, não da sessão Reflex
O sistema DEVE (MUST) tratar as oito horas consolidadas como o prazo máximo durante o qual o Xano pode aceitar o token, sem garantir que o State Reflex ou a sessão da aplicação sobreviva por todo esse período.

#### Scenario: State perdido antes de oito horas
- **WHEN** o State Reflex deixar de estar disponível antes do limite de oito horas do token Xano
- **THEN** a sessão da aplicação termina e o usuário deve se autenticar novamente, mesmo que o token pudesse continuar válido no Xano

#### Scenario: State preservado após expiração do token
- **WHEN** o State Reflex ainda contém o token depois que o Xano encerra sua validade máxima de oito horas
- **THEN** a próxima validação por `/me` encerra a sessão local sem refresh ou renovação automática

### Requirement: Identidade autenticada é obtida por `/me`
O sistema DEVE (MUST) considerar uma sessão autenticada somente após `GET /me` confirmar o token e retornar uma identidade com perfil oficial, mantendo no estado apresentável apenas `id`, `nome`, `email`, `role` e `lojas_id` quando aplicável.

#### Scenario: Identidade válida de perfil oficial
- **WHEN** `GET /me` retorna uma identidade com perfil `gerente`, `tecnico` ou `diretoria`
- **THEN** o Reflex registra os dados públicos retornados como usuário atual e disponibiliza a casca autenticada correspondente

#### Scenario: Resposta sem perfil oficial
- **WHEN** a resposta de identidade não contém um dos três perfis oficiais ou não possui o formato mínimo esperado
- **THEN** o Reflex não concede uma sessão utilizável, descarta o estado de autenticação e retorna ao login

#### Scenario: Revalidação de sessão existente
- **WHEN** uma página autenticada é carregada com um token já associado à sessão Reflex
- **THEN** o Reflex consulta `GET /me` antes de apresentar o conteúdo autenticado da página

### Requirement: Expiração encerra a sessão local
O sistema DEVE (MUST) tratar a rejeição de autenticação de uma chamada protegida como sessão inválida ou expirada, descartando token e identidade locais, sem tentar renovar o token automaticamente.

#### Scenario: Token expirado durante revalidação
- **WHEN** `GET /me` rejeita o token como não autenticado
- **THEN** o Reflex limpa a sessão local, informa que a sessão expirou e redireciona o usuário para `/login`

#### Scenario: Token expirado durante operação autenticada futura
- **WHEN** o cliente centralizado receber uma rejeição de autenticação do Xano em qualquer chamada protegida
- **THEN** o mesmo encerramento de sessão é aplicado sem refresh token ou renovação automática

#### Scenario: Operação apenas não autorizada
- **WHEN** o Xano reconhece a sessão, mas rejeita uma operação por falta de autorização
- **THEN** o Reflex mantém a sessão autenticada e apresenta a negação sem reinterpretá-la como expiração

### Requirement: Logout remove o estado autenticado
O sistema DEVE (MUST) permitir que qualquer usuário autenticado encerre sua sessão local por uma ação de logout disponível na casca da aplicação.

#### Scenario: Logout de usuário autenticado
- **WHEN** o usuário aciona o logout
- **THEN** o Reflex descarta o token e a identidade local e redireciona para `/login`

#### Scenario: Retorno após logout
- **WHEN** o usuário tenta carregar uma página autenticada depois do logout
- **THEN** o Reflex exige uma nova autenticação e não reapresenta o estado anterior

### Requirement: Páginas autenticadas possuem proteção de rota
O sistema DEVE (MUST) proteger as páginas da casca autenticada e verificar a sessão no carregamento da rota, mantendo `/login` como página pública.

#### Scenario: Visitante acessa página autenticada
- **WHEN** um visitante sem token de sessão acessa `/gerente`, `/tecnico` ou `/diretoria`
- **THEN** o Reflex não apresenta o conteúdo autenticado e redireciona para `/login`

#### Scenario: Usuário autenticado acessa login
- **WHEN** um usuário com sessão confirmada acessa `/login`
- **THEN** o Reflex redireciona para a página inicial correspondente ao perfil retornado por `/me`

#### Scenario: Sessão em revalidação
- **WHEN** uma página protegida está aguardando a resposta de `GET /me`
- **THEN** o Reflex apresenta um estado neutro de carregamento e não renderiza antecipadamente conteúdo autenticado

### Requirement: Navegação e destino inicial seguem o perfil oficial
O sistema DEVE (MUST) fornecer uma casca de navegação mínima compatível com o perfil confirmado por `/me`, sem apresentar ações de Service Desk, fila técnica, tratamento, dashboards ou indicadores nesta change.

#### Scenario: Entrada de Gerente
- **WHEN** `/me` confirma o perfil `gerente`
- **THEN** o Reflex direciona o usuário para `/gerente` e apresenta uma página inicial neutra identificada para esse perfil

#### Scenario: Entrada de Técnico
- **WHEN** `/me` confirma o perfil `tecnico`
- **THEN** o Reflex direciona o usuário para `/tecnico` e apresenta uma página inicial neutra identificada para esse perfil

#### Scenario: Entrada de Diretoria
- **WHEN** `/me` confirma o perfil `diretoria`
- **THEN** o Reflex direciona o usuário para `/diretoria` e apresenta uma página inicial neutra identificada para esse perfil

#### Scenario: Acesso à raiz
- **WHEN** um usuário acessa `/`
- **THEN** o Reflex direciona para `/login` se não houver sessão confirmada ou para a página inicial de seu perfil se a sessão for válida

#### Scenario: Usuário acessa página inicial de outro perfil
- **WHEN** um usuário autenticado tenta acessar diretamente a página inicial reservada a outro perfil
- **THEN** o Reflex não apresenta o conteúdo dessa página e o redireciona para a página inicial do seu próprio perfil

### Requirement: Proteção visual não substitui autorização do Xano
O sistema NÃO DEVE (MUST NOT) tratar a navegação, a ocultação de componentes ou a proteção de rotas do Reflex como fonte de autorização para dados ou operações protegidas.

#### Scenario: Chamada protegida iniciada pelo Reflex
- **WHEN** uma página ou evento do Reflex precisar acessar uma API destinada a usuários
- **THEN** a chamada é enviada ao Xano com a identidade de sessão para que o backend aplique a autorização consolidada

#### Scenario: Elemento indisponível para o perfil
- **WHEN** a casca omite um destino que não corresponde ao perfil atual
- **THEN** essa omissão é tratada somente como comportamento de navegação e não altera nem substitui a política de autorização do Xano
