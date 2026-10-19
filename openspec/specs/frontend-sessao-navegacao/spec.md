# frontend-sessao-navegacao Specification

## Purpose

Definir o comportamento observável da casca autenticada do MIRA no Reflex, incluindo login, sessão, identidade atual, proteção de páginas e navegação pelos perfis oficiais.

## Requirements

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
O sistema DEVE (MUST) considerar uma sessão autenticada somente após `GET /me` confirmar o token e retornar uma identidade com perfil oficial, mantendo no estado apresentável apenas `id`, `nome`, `email`, `role`, `lojas_id` quando aplicável e o estado de troca obrigatória de senha.

#### Scenario: Identidade confirmada
- **WHEN** `GET /me` retorna uma identidade humana oficial válida
- **THEN** o Reflex publica seus dados permitidos e o estado de troca obrigatória na sessão

#### Scenario: Identidade fora do contrato
- **WHEN** `GET /me` retorna perfil ou estado de troca inválido
- **THEN** o Reflex falha de forma fechada sem publicar sessão autenticada

#### Scenario: Identidade válida de perfil oficial
- **WHEN** `GET /me` retorna uma identidade com perfil `gerente`, `tecnico`, `diretoria` ou `administrador`
- **THEN** o Reflex registra os dados públicos retornados, incluindo o estado de troca, e disponibiliza a casca autenticada correspondente

#### Scenario: Resposta sem perfil oficial
- **WHEN** a resposta de identidade não contém um dos quatro perfis oficiais ou não possui o formato mínimo esperado
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
O sistema DEVE (MUST) proteger todas as rotas funcionais e verificar a sessão no carregamento, mantendo `/login` como pública. Enquanto a troca obrigatória estiver pendente, qualquer rota funcional canônica ou alias legado DEVE redirecionar para `/primeiro-acesso` sem renderizar conteúdo funcional. Sem sessão válida, a rota protegida DEVE redirecionar para `/login`. Depois da troca, `/primeiro-acesso` DEVE redirecionar para `/inicio`.

#### Scenario: Acesso direto sem sessão
- **WHEN** um visitante acessa `/inicio`, `/chamados`, `/chamados/novo`, `/chamados/[chamado_id]`, `/administracao/usuarios`, `/monitoramento` ou alias legado
- **THEN** o Reflex não renderiza conteúdo protegido e redireciona para `/login`

#### Scenario: Rota funcional com troca pendente
- **WHEN** usuário autenticado com troca pendente acessa rota funcional canônica ou alias legado
- **THEN** o Reflex revalida a identidade e redireciona para `/primeiro-acesso`

#### Scenario: Rota de primeiro acesso pendente
- **WHEN** usuário autenticado com troca pendente acessa `/primeiro-acesso`
- **THEN** o Reflex revalida `/me`, permanece nessa rota e não emite redirecionamento para ela própria

#### Scenario: Rota de primeiro acesso concluído
- **WHEN** usuário autenticado sem troca pendente acessa `/primeiro-acesso`
- **THEN** o Reflex o redireciona para `/inicio`

#### Scenario: Visitante acessa página autenticada
- **WHEN** um visitante sem token de sessão acessa uma rota funcional canônica ou um alias legado
- **THEN** o Reflex não apresenta conteúdo autenticado e redireciona para `/login`

#### Scenario: Usuário autenticado acessa login
- **WHEN** um usuário com sessão confirmada acessa `/login`
- **THEN** o Reflex redireciona para `/primeiro-acesso` se houver pendência ou para `/inicio` se a identidade for válida

#### Scenario: Sessão em revalidação
- **WHEN** uma página protegida aguarda a resposta de `GET /me`
- **THEN** o Reflex apresenta estado neutro de carregamento e não renderiza antecipadamente conteúdo autenticado

#### Scenario: Sessão expirada durante revalidação
- **WHEN** a revalidação de uma rota protegida recebe rejeição de autenticação
- **THEN** o Reflex limpa a sessão local e redireciona para `/login`, sem renovar token

### Requirement: Navegação e destino inicial seguem o perfil oficial
O sistema DEVE (MUST) direcionar todos os perfis oficiais sem troca pendente para `/inicio` após login, acesso à raiz, acesso autenticado ao login ou conclusão do primeiro acesso. `/inicio` e `/chamados` DEVEM reutilizar a jornada local para Gerente e a jornada global para Técnico, Diretoria e Administrador, somente após `GET /me` confirmar a identidade. A casca DEVE apontar o botão `Início` para `/inicio`.

#### Scenario: Login de perfil oficial
- **WHEN** `/me` confirma Gerente, Técnico, Diretoria ou Administrador sem troca pendente
- **THEN** o Reflex redireciona para `/inicio`

#### Scenario: Destino de Administrador
- **WHEN** `/me` confirma uma identidade com perfil `administrador` e sem troca pendente
- **THEN** o Reflex a direciona para `/inicio`, que reutiliza a fila global existente

#### Scenario: Área administrativa mínima
- **WHEN** Administrador confirmado acessa `/administracao/usuarios`
- **THEN** a interface apresenta o formulário existente de criação com nome, e-mail, perfil, Loja condicional, senha temporária e confirmação local

#### Scenario: Entrada de Gerente
- **WHEN** `/me` confirma o perfil `gerente`
- **THEN** o Reflex direciona o usuário para `/inicio`, que apresenta a listagem de chamados da Loja e a navegação existente para abrir chamado

#### Scenario: Entrada de Técnico
- **WHEN** `/me` confirma o perfil `tecnico`
- **THEN** o Reflex direciona o usuário para `/inicio`, que apresenta a fila global e suas visões aprovadas

#### Scenario: Entrada de Diretoria
- **WHEN** `/me` confirma o perfil `diretoria`
- **THEN** o Reflex direciona o usuário para `/inicio`, que apresenta a fila global existente, sem dashboard ou página neutra adicional

#### Scenario: Conteúdo inicial por perfil
- **WHEN** perfil autenticado acessa `/inicio`
- **THEN** Gerente recebe a lista de sua Loja e Técnico, Diretoria e Administrador recebem a fila global existente, sem nova tela intermediária ou dashboard

#### Scenario: Listagem canônica
- **WHEN** perfil autenticado acessa `/chamados`
- **THEN** o Reflex apresenta a mesma jornada contextual de `/inicio` para esse perfil

#### Scenario: Acesso à raiz
- **WHEN** um usuário acessa `/`
- **THEN** o Reflex direciona para `/login` se não houver sessão confirmada, para `/primeiro-acesso` se houver pendência ou para `/inicio` se a sessão for válida

#### Scenario: Técnico navega pela jornada de atribuição
- **WHEN** um Técnico com sessão confirmada usa a casca autenticada
- **THEN** ele acessa `/chamados` e `/chamados/[chamado_id]`, mantendo a fila, o detalhe e o escopo rápido aprovados, sem destinos de Gerente

#### Scenario: Gerente navega pela jornada de chamados
- **WHEN** um Gerente com sessão confirmada usa a casca autenticada
- **THEN** ele acessa `/chamados`, `/chamados/novo` e `/chamados/[chamado_id]`, sem receber fila global ou tratativa

#### Scenario: Usuário acessa página inicial de outro perfil
- **WHEN** usuário autenticado tenta acessar rota canônica ou alias que resolveria para jornada não permitida ao seu perfil
- **THEN** o Reflex não apresenta conteúdo daquela jornada e o redireciona para `/inicio`, salvo troca pendente, que direciona para `/primeiro-acesso`

#### Scenario: URL legada de listagem
- **WHEN** sessão revalidada acessa `/gerente`, `/tecnico` ou `/diretoria`
- **THEN** o Reflex redireciona para a rota canônica apropriada sem renderizar implementação legada; se a funcionalidade não for permitida ao perfil, redireciona para `/inicio`

#### Scenario: Alias legado de detalhe
- **WHEN** sessão revalidada acessa `/gerente/chamados/[chamado_id]` ou `/tecnico/chamados/[chamado_id]`
- **THEN** o Reflex redireciona para `/chamados/[chamado_id]` e preserva o identificador, aplicando a jornada correspondente ao perfil

#### Scenario: Alias legado de abertura
- **WHEN** Gerente autenticado e sem pendência acessa `/gerente/chamados/novo`
- **THEN** o Reflex redireciona para `/chamados/novo` sem renderizar formulário legado e resolve `novo` como segmento estático, não como `chamado_id`

#### Scenario: Alias administrativo
- **WHEN** Administrador autenticado acessa `/administracao`
- **THEN** o Reflex redireciona para `/administracao/usuarios` sem duplicar a tela administrativa

### Requirement: Proteção visual não substitui autorização do Xano
O sistema NÃO DEVE (MUST NOT) usar a rota, o dispatcher, um alias, a identidade visual ou a ocultação de componentes como autorização. A escolha de jornada no Reflex DEVE manter as chamadas aos contratos Xano já consolidados.

#### Scenario: URL comum para perfis com escopos distintos
- **WHEN** Gerente e perfil global acessam a mesma rota canônica de chamados
- **THEN** cada jornada chama apenas seu contrato existente e o Xano continua decidindo autorização, escopo e dados retornados

#### Scenario: Chamada protegida iniciada pelo Reflex
- **WHEN** página ou evento Reflex acessa API destinada a usuários
- **THEN** a chamada é enviada ao Xano com a identidade de sessão para que o backend aplique a autorização consolidada

#### Scenario: Elemento indisponível para o perfil
- **WHEN** a casca omite ou redireciona um destino que não corresponde ao perfil atual
- **THEN** essa decisão é somente de navegação e não altera nem substitui a política de autorização do Xano

### Requirement: Interface de criação respeita regras de perfil e segredo
O formulário administrativo MUST mostrar e exigir Loja somente para Gerente, NÃO DEVE enviar Loja para os outros perfis e DEVE exigir confirmação local da senha temporária. Sucesso ou erro NÃO DEVE exibir senha, hash ou token; o backend permanece autoridade das validações.

#### Scenario: Criação de Gerente pela interface
- **WHEN** Administrador seleciona Gerente e preenche os dados válidos com Loja e senhas temporárias iguais
- **THEN** a interface envia a criação e apresenta sucesso sem repetir a senha

#### Scenario: Perfil sem Loja ou confirmação divergente
- **WHEN** Administrador seleciona Técnico, Diretoria ou Administrador, ou informa confirmações de senha diferentes
- **THEN** a interface não envia Loja para o perfil global e impede o envio local até a confirmação coincidir

### Requirement: Interface conclui o primeiro acesso
O Reflex MUST oferecer a rota exclusiva de primeiro acesso com nova senha e confirmação local. Após sucesso da operação autenticada, DEVE revalidar `/me` e redirecionar para o destino normal confirmado pelo perfil.

#### Scenario: Nova senha válida
- **WHEN** usuário pendente informa nova senha com confirmação local correspondente e a operação é aceita
- **THEN** o Reflex revalida `/me` e o direciona a Gerente, Técnico, Diretoria ou Administração conforme a identidade confirmada

#### Scenario: Falha na troca
- **WHEN** a operação de troca é rejeitada ou falha
- **THEN** o Reflex mantém o usuário no fluxo exclusivo, apresenta erro sanitizado e não assume que a pendência foi encerrada

### Requirement: URLs canônicas representam funcionalidades
O Reflex DEVE (MUST) registrar `/inicio` como a URL canônica da listagem de
chamados por perfil e manter `/chamados` como redirecionamento protegido de
compatibilidade para `/inicio`. O redirecionamento NÃO DEVE (MUST NOT) limpar
filtros em memória da sessão. `/chamados/novo`, `/chamados/[chamado_id]` e
`/administracao/usuarios` permanecem rotas funcionais; `/chamados/novo` DEVE
(MUST) ser resolvida como rota estática antes de `/chamados/[chamado_id]`.
`/`, `/login` e `/primeiro-acesso` mantêm suas responsabilidades atuais.
`/monitoramento` DEVE (MUST) permitir somente Técnico, Diretoria e
Administrador depois da revalidação; Gerente é redirecionado para `/inicio` sem
carregar dados de monitoramento.

#### Scenario: Link legado da listagem
- **WHEN** perfil autenticado acessa `/chamados`
- **THEN** o Reflex revalida a sessão e redireciona para `/inicio` sem renderizar
  uma segunda listagem ou descartar seus filtros em memória

#### Scenario: Rota estática de abertura
- **WHEN** Gerente autenticado acessa `/chamados/novo`
- **THEN** o Reflex carrega o formulário de abertura, e não interpreta `novo`
  como `chamado_id`

#### Scenario: Monitoramento preservado
- **WHEN** Técnico, Diretoria ou Administrador com sessão revalidada acessa
  `/monitoramento`
- **THEN** o Reflex preserva a jornada de monitoramento existente após aplicar
  a autorização aprovada para a rota

#### Scenario: Monitoramento por perfil permitido
- **WHEN** Técnico, Diretoria ou Administrador com sessão revalidada acessa
  `/monitoramento`
- **THEN** o Reflex carrega a jornada de monitoramento existente

#### Scenario: Gerente acessa monitoramento diretamente
- **WHEN** Gerente com sessão revalidada acessa `/monitoramento`
- **THEN** o Reflex redireciona para `/inicio` sem consultar o contrato de
  monitoramento
