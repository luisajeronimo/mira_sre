# Spec Delta

## MODIFIED Requirements

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

### Requirement: Páginas autenticadas possuem proteção de rota
O sistema DEVE (MUST) proteger as páginas da casca autenticada e verificar a sessão no carregamento da rota, mantendo `/login` como página pública. Enquanto a troca obrigatória estiver pendente, qualquer rota funcional protegida DEVE redirecionar para a rota exclusiva de primeiro acesso; depois de concluída, essa rota exclusiva DEVE redirecionar ao destino do perfil.

#### Scenario: Rota funcional com troca pendente
- **WHEN** usuário autenticado com troca pendente acessa `/gerente`, `/tecnico`, `/diretoria`, `/administracao` ou outra rota funcional protegida
- **THEN** o Reflex redireciona para o fluxo exclusivo de primeiro acesso sem renderizar conteúdo funcional

#### Scenario: Rota de primeiro acesso pendente
- **WHEN** usuário autenticado com troca pendente acessa a rota exclusiva de primeiro acesso
- **THEN** o Reflex revalida `/me`, permanece na rota e não emite redirecionamento para ela própria

#### Scenario: Rota de primeiro acesso concluído
- **WHEN** usuário autenticado sem troca pendente acessa a rota exclusiva de primeiro acesso
- **THEN** o Reflex o redireciona para o destino normal de seu perfil

#### Scenario: Visitante acessa página autenticada
- **WHEN** um visitante sem token de sessão acessa `/gerente`, `/tecnico`, `/diretoria` ou `/administracao`
- **THEN** o Reflex não apresenta o conteúdo autenticado e redireciona para `/login`

#### Scenario: Usuário autenticado acessa login
- **WHEN** um usuário com sessão confirmada acessa `/login`
- **THEN** o Reflex redireciona para a rota de primeiro acesso se estiver pendente ou para a página inicial do perfil retornado por `/me`

#### Scenario: Sessão em revalidação
- **WHEN** uma página protegida está aguardando a resposta de `GET /me`
- **THEN** o Reflex apresenta um estado neutro de carregamento e não renderiza antecipadamente conteúdo autenticado

### Requirement: Navegação e destino inicial seguem o perfil oficial
O sistema DEVE (MUST) fornecer uma casca de navegação compatível com o perfil confirmado por `/me`. Para o Gerente, a casca DEVE (MUST) incluir os destinos funcionais de listagem e abertura de chamados; para o Técnico, DEVE (MUST) incluir a fila e o detalhe da atribuição técnica introduzidos pela capacidade `chamados-fila-atribuicao-tecnica`; para a Diretoria, a página inicial permanece neutra; para o Administrador, DEVE incluir somente a área mínima de criação de usuários nesta change. A casca NÃO DEVE (MUST NOT) apresentar tratativa completa, dashboards ou indicadores nesta change.

#### Scenario: Destino de Administrador
- **WHEN** `/me` confirma uma identidade com perfil `administrador` e sem troca pendente
- **THEN** o Reflex a direciona para `/administracao`

#### Scenario: Área administrativa mínima
- **WHEN** Administrador confirmado acessa `/administracao`
- **THEN** a interface apresenta o formulário de criação com nome, e-mail, perfil, Loja condicional, senha temporária e confirmação local de senha

#### Scenario: Entrada de Gerente
- **WHEN** `/me` confirma o perfil `gerente`
- **THEN** o Reflex direciona o usuário para `/gerente`, apresenta a listagem básica dos chamados da Loja e disponibiliza a navegação para abrir chamado

#### Scenario: Entrada de Técnico
- **WHEN** `/me` confirma o perfil `tecnico`
- **THEN** o Reflex direciona o usuário para `/tecnico` e apresenta a fila técnica com as visões aprovadas, sem apresentar tratativa completa, dashboards ou indicadores

#### Scenario: Entrada de Diretoria
- **WHEN** `/me` confirma o perfil `diretoria`
- **THEN** o Reflex direciona o usuário para `/diretoria` e apresenta uma página inicial neutra identificada para esse perfil

#### Scenario: Acesso à raiz
- **WHEN** um usuário acessa `/`
- **THEN** o Reflex direciona para `/login` se não houver sessão confirmada, para primeiro acesso se houver pendência ou para a página inicial de seu perfil se a sessão for válida

#### Scenario: Técnico navega pela jornada de atribuição
- **WHEN** um Técnico com sessão confirmada usa a casca autenticada
- **THEN** ele pode acessar a fila e o detalhe técnico, sem receber ações de tratativa completa ou destinos de Gerente e Diretoria

#### Scenario: Gerente navega pela jornada de chamados
- **WHEN** um Gerente com sessão confirmada usa a casca autenticada
- **THEN** ele pode acessar a listagem, a abertura e o detalhe de chamados sem receber destinos de fila técnica, tratamento, dashboards ou indicadores

#### Scenario: Usuário acessa página inicial de outro perfil
- **WHEN** um usuário autenticado tenta acessar diretamente a página inicial ou uma rota funcional reservada a outro perfil
- **THEN** o Reflex não apresenta o conteúdo dessa página e o redireciona para a página inicial do próprio perfil, salvo se houver troca pendente, caso em que vai para primeiro acesso

## ADDED Requirements

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
