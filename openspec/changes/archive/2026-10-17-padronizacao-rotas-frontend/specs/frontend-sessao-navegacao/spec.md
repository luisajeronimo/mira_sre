# Delta: frontend-sessao-navegacao

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: URLs canônicas representam funcionalidades
O Reflex DEVE (MUST) registrar `/inicio`, `/chamados`, `/chamados/novo`, `/chamados/[chamado_id]` e `/administracao/usuarios` como URLs canônicas. `/chamados/novo` DEVE ser resolvida como rota estática antes de `/chamados/[chamado_id]`. `/`, `/login`, `/primeiro-acesso` e `/monitoramento` mantêm suas responsabilidades atuais.

#### Scenario: Rota estática de abertura
- **WHEN** Gerente autenticado acessa `/chamados/novo`
- **THEN** o Reflex carrega o formulário de abertura, e não interpreta `novo` como `chamado_id`

#### Scenario: Monitoramento preservado
- **WHEN** sessão autenticada acessa `/monitoramento`
- **THEN** o Reflex mantém o comportamento e o guard existentes, sem ampliar nem restringir permissões nesta change
