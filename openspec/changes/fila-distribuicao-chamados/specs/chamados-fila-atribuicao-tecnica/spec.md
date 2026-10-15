# Delta: chamados-fila-atribuicao-tecnica

## MODIFIED Requirements

### Requirement: Fila técnica oferece somente as visões aprovadas
O sistema DEVE (MUST) oferecer uma única tabela global de chamados para Técnico, Diretoria e Administrador, aplicando no Xano os mesmos filtros explícitos da listagem do Gerente: número, status, Totem e período de abertura. Sem filtros aplicados, `Todos` DEVE significar todos os chamados dentro do escopo global, sem restrição implícita por status, responsável, origem, solicitante, data ou Loja. O Técnico também possui a visão rápida `Atribuídos a mim`, fora do painel de filtros operacionais, que aplica `tecnico_id == usuário autenticado` e se combina aos filtros explícitos. Diretoria e Administrador não recebem essa visão. O Gerente NÃO DEVE acessar esta fila.

#### Scenario: Visão de chamados não atribuídos
- **WHEN** um Técnico consulta a fila global
- **THEN** a interface não apresenta uma visão rápida de chamados não atribuídos

#### Scenario: Visão de chamados atribuídos a mim
- **WHEN** um Técnico seleciona `Atribuídos a mim`
- **THEN** o Xano retorna somente chamados cujo responsável atual é o próprio Técnico autenticado

#### Scenario: Escopo rápido combina com filtros operacionais
- **WHEN** um Técnico seleciona `Atribuídos a mim` e informa número, status, Totem ou período
- **THEN** o Xano retorna a interseção entre o responsável atual e os filtros explícitos

#### Scenario: Limpeza preserva escopo rápido
- **WHEN** um Técnico limpa os filtros operacionais dentro de `Atribuídos a mim`
- **THEN** a consulta remove número, status, Totem e período, mas mantém o escopo de responsável atual

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** um chamado possui responsável diferente do usuário autenticado
- **THEN** ele continua na tabela global sem criar uma visão ou filtro específico

#### Scenario: Visão inválida
- **WHEN** uma requisição informa situação de atribuição
- **THEN** o Xano responde HTTP 422 sem retornar dados de um filtro implícito

#### Scenario: Todos sem filtro
- **WHEN** um perfil autorizado consulta a fila sem filtros
- **THEN** o Xano retorna todos os chamados globais permitidos, inclusive atribuídos, não atribuídos, terminais e não terminais

#### Scenario: Status nulo ou inelegível
- **WHEN** um chamado possui status nulo ou qualquer status persistido
- **THEN** o Xano não infere nem altera o status e a fila não o exclui apenas por ser diferente de `Novo`

#### Scenario: Ordenação e ausência de paginação
- **WHEN** a consulta válida retorna chamados
- **THEN** os itens são ordenados por `id` decrescente e a resposta não introduz paginação ou busca avançada nesta capacidade

#### Scenario: Consulta global por Diretoria ou Administrador
- **WHEN** um usuário autenticado de Diretoria ou Administrador consulta a fila
- **THEN** o Xano retorna a mesma visão global de chamados permitida ao Técnico

#### Scenario: Interseção de filtros explícitos
- **WHEN** um perfil autorizado pesquisa por número ou combina status, Totem e período de abertura
- **THEN** o Xano retorna somente os chamados que correspondem à interseção dos filtros enviados

#### Scenario: Responsável de outro Técnico não cria visão de navegação
- **WHEN** um chamado possui ou não possui Técnico responsável
- **THEN** ele permanece na tabela global e a interface não apresenta `Atribuídos a outros Técnicos` ou `Não atribuídos` como visão de atribuição

#### Scenario: Falha de consulta não confirma filtro no Reflex
- **WHEN** uma pesquisa ou filtro solicitado falha antes de o Xano retornar a lista
- **THEN** o Reflex mantém o último filtro aplicado e seu resultado coerentes e informa a falha sem indicar o novo filtro como aplicado

#### Scenario: Gerente tenta consultar a fila global
- **WHEN** um Gerente tenta consultar a fila global
- **THEN** o Xano responde HTTP 403 sem expor chamados fora dos contratos próprios do Gerente

### Requirement: Técnico pode consultar detalhe global somente leitura
O sistema DEVE (MUST) fornecer detalhe global de chamado para Técnico, Diretoria e Administrador em um DTO canônico, incluindo número, título, descrição, status, prioridade, origem, solicitante, Loja, Totem, categoria, SLA, responsável atual, `atribuido_em` e timeline. A leitura NÃO DEVE (MUST NOT) alterar o chamado. Estados terminais continuam consultáveis, mas impedem operações de atribuição incompatíveis.

#### Scenario: Detalhe antes da assunção
- **WHEN** um perfil autorizado consulta chamado ainda sem responsável
- **THEN** o Xano retorna responsável e `atribuido_em` nulos, quando aplicável

#### Scenario: Detalhe depois da assunção
- **WHEN** um perfil autorizado consulta chamado atribuído
- **THEN** o Xano retorna o Técnico responsável e o `atribuido_em` persistido

#### Scenario: Chamado inexistente
- **WHEN** um perfil autorizado consulta identificador inexistente
- **THEN** o Xano responde HTTP 404

#### Scenario: Dados protegidos por rota indevida
- **WHEN** um Gerente tenta usar o detalhe da fila global
- **THEN** o Xano responde HTTP 403 sem expor o chamado

#### Scenario: Contrato de detalhe incompatível
- **WHEN** o backend omite campo obrigatório do DTO canônico
- **THEN** o service recusa a resposta e a interface informa erro de carregamento sem renderizar valores `undefined`

### Requirement: Schema registra a atribuição sem backfill
O sistema DEVE (MUST) manter `atribuido_em` como timestamp opcional em `chamados`, representando o início da atribuição atual. O Xano define o timestamp ao atribuir ou reatribuir, limpa-o ao liberar e preserva registros históricos sem preenchimento retroativo.

#### Scenario: Assunção grava timestamp do backend
- **WHEN** uma operação autorizada altera o Técnico responsável
- **THEN** o Xano grava `atribuido_em` com o instante da nova atribuição, sem aceitar timestamp enviado pelo cliente

#### Scenario: Cliente tenta informar timestamp
- **WHEN** o cliente envia `atribuido_em` na requisição
- **THEN** o Xano ignora ou rejeita esse valor e define o instante pelo backend

#### Scenario: Liberação encerra atribuição atual
- **WHEN** uma operação autorizada libera o Técnico responsável
- **THEN** `tecnico_id` e `atribuido_em` ficam ausentes e o status do chamado permanece inalterado

#### Scenario: Registro legado
- **WHEN** a evolução do schema encontra um chamado existente
- **THEN** o registro é preservado e `atribuido_em` permanece nulo quando não houver valor persistido

### Requirement: Assunção é autoatribuição idempotente com consistência best-effort no plano Free
O Xano DEVE (MUST) permitir assumir, atribuir, reatribuir e liberar chamados não terminais conforme o perfil autenticado. Somente Técnico pode ser responsável. Alterações de responsável NÃO DEVEM alterar o status e DEVEM persistir a mutação e o evento estruturado na mesma operação.

#### Scenario: Assunção válida
- **WHEN** um Técnico autenticado assume um chamado sem responsável e não terminal
- **THEN** o Xano atribui o Técnico autenticado, registra `atribuido_em` e o evento, mantendo o status existente

#### Scenario: Repetição pelo mesmo Técnico
- **WHEN** o Técnico responsável repete `Assumir`
- **THEN** o Xano retorna o estado atual sem alterar `tecnico_id`, `atribuido_em` ou `ultima_atualizacao_em` e sem criar outro evento

#### Scenario: Outro Técnico já assumiu
- **WHEN** um Técnico tenta assumir chamado já atribuído a outro Técnico
- **THEN** o Xano não substitui a atribuição e responde HTTP 409

#### Scenario: Técnico, Diretoria ou Administrador atribui ou reatribui
- **WHEN** um desses perfis envia um Técnico válido para um chamado não terminal
- **THEN** o Xano grava o Técnico escolhido, define `atribuido_em` e registra se a operação foi atribuição ou reatribuição, sem alterar o status

#### Scenario: Usuário escolhido não é Técnico
- **WHEN** uma operação informa como responsável um usuário que não possui perfil Técnico
- **THEN** o Xano rejeita a operação sem alterar chamado ou histórico

#### Scenario: Técnico libera somente a própria atribuição
- **WHEN** um Técnico libera chamado atribuído a ele
- **THEN** o Xano remove responsável e `atribuido_em`, registra o evento e mantém o status atual

#### Scenario: Técnico tenta liberar atribuição de outro Técnico
- **WHEN** um Técnico tenta liberar chamado atribuído a outra pessoa
- **THEN** o Xano responde HTTP 403 sem alterar chamado ou histórico

#### Scenario: Diretoria ou Administrador libera atribuição
- **WHEN** Diretoria ou Administrador libera chamado atribuído a um Técnico
- **THEN** o Xano remove responsável e `atribuido_em`, registra o evento e mantém o status atual

#### Scenario: Estado terminal
- **WHEN** qualquer perfil tenta assumir, atribuir, reatribuir ou liberar chamado `Encerrado` ou `Cancelado`
- **THEN** o Xano rejeita a operação sem alterar status, responsável, timestamp ou histórico

#### Scenario: Resolvido não é terminal para atribuição
- **WHEN** um perfil autorizado atribui, reatribui ou libera chamado `Resolvido`
- **THEN** o Xano aplica as regras da operação e mantém o status `Resolvido`

#### Scenario: Assunção mantém Novo
- **WHEN** um Técnico assume chamado em `Novo`
- **THEN** o status permanece `Novo` e não passa automaticamente a `Em Atendimento`

#### Scenario: Chamado inelegível para assunção
- **WHEN** uma operação de atribuição tenta alterar chamado `Encerrado`, `Cancelado` ou com status não reconhecido
- **THEN** o Xano rejeita a operação sem efeito parcial

#### Scenario: Assumir outro status não terminal
- **WHEN** um Técnico assume chamado sem responsável em status não terminal diferente de `Novo`
- **THEN** o Xano registra a atribuição e mantém o status atual

#### Scenario: Dois Técnicos concorrem
- **WHEN** dois Técnicos tentam assumir simultaneamente o mesmo chamado sem responsável
- **THEN** o Xano valida a atribuição antes e depois da escrita conforme os recursos gratuitos disponíveis, sem afirmar garantia matemática de vencedor único em simultaneidade exata

#### Scenario: Chamado não terminal em outro status
- **WHEN** um perfil autorizado atribui, reatribui ou libera chamado em status diferente de `Encerrado` e `Cancelado`
- **THEN** o Xano aplica a operação sem alterar o status, inclusive quando estiver `Resolvido`

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** um Técnico usa `Assumir` em chamado já atribuído a outra pessoa
- **THEN** o Xano responde HTTP 409 sem sobrescrever o responsável ou `atribuido_em`

#### Scenario: Campos sob autoridade do Xano
- **WHEN** o cliente envia status ou `atribuido_em`, ou envia um responsável que não é válido para a operação
- **THEN** o Xano rejeita ou ignora esses valores sem permitir que substituam as regras do backend

### Requirement: Autorização e erros da jornada técnica são estáveis
Os contratos da fila global DEVEM (MUST) exigir autenticação e aplicar no Xano os perfis autorizados e as regras da atribuição, independentemente da interface Reflex. O CRUD genérico de chamados NÃO DEVE (MUST NOT) contornar essas regras.

#### Scenario: Sessão ausente
- **WHEN** uma rota da fila global recebe requisição sem sessão válida
- **THEN** o Xano responde HTTP 401 sem consultar ou alterar chamados

#### Scenario: Gerente ou Diretoria tenta usar rota técnica
- **WHEN** um Gerente consulta a fila global ou a Diretoria solicita operação fora da gestão de atribuição prevista
- **THEN** o Xano responde HTTP 403 sem expor dados ou executar alterações

#### Scenario: CRUD genérico continua negado
- **WHEN** um usuário tenta alterar `chamados` pelo CRUD genérico
- **THEN** nenhum chamado é modificado

### Requirement: Assunção efetiva atualiza a última atualização observável
Uma alteração efetiva de responsável DEVE (MUST) atualizar `ultima_atualizacao_em` junto com `tecnico_id`, `atribuido_em` e o evento de histórico. Uma operação sem alteração efetiva, incluindo `Assumir` idempotente, NÃO DEVE (MUST NOT) atualizar esses valores nem criar evento duplicado.

#### Scenario: Assunção válida atualiza a data
- **WHEN** uma operação autorizada efetivamente altera o responsável
- **THEN** os dados do chamado, `ultima_atualizacao_em` e o evento são persistidos juntos pelo Xano

#### Scenario: Repetição idempotente não atualiza a data
- **WHEN** o Técnico responsável repete `Assumir`
- **THEN** `ultima_atualizacao_em`, `atribuido_em` e o histórico permanecem inalterados

#### Scenario: Atribuição, reatribuição ou liberação efetiva
- **WHEN** uma operação autorizada efetivamente altera o responsável
- **THEN** os timestamps funcionais e evento correspondentes são persistidos com a alteração

### Requirement: Reflex oferece a jornada técnica mínima
O Reflex DEVE (MUST) reutilizar a fila e o detalhe existentes para Técnico, Diretoria e Administrador, exibindo pesquisa por número, responsável, ações permitidas e timeline. A interface NÃO substitui a autorização do Xano nem oferece mudança de status nesta change.

#### Scenario: Técnico carrega a fila
- **WHEN** um Técnico autenticado acessa a fila
- **THEN** o Reflex consulta o Xano e apresenta a tabela global com estados de carregamento, vazio, sucesso e erro

#### Scenario: Ações disponíveis por perfil e estado
- **WHEN** a interface apresenta um chamado não terminal
- **THEN** ela oferece somente ações de atribuição permitidas ao perfil e ao estado do responsável

#### Scenario: Assunção bem-sucedida
- **WHEN** o Técnico confirma `Assumir` em chamado sem responsável e o Xano responde sucesso
- **THEN** o Reflex atualiza o State com a resposta e mantém o status recebido

#### Scenario: Conflito de assunção
- **WHEN** o Xano responde HTTP 409 porque outro Técnico assumiu
- **THEN** o Reflex informa o conflito e recarrega a lista ou detalhe sem substituir dados

#### Scenario: Chamado terminal
- **WHEN** a interface apresenta chamado `Encerrado` ou `Cancelado`
- **THEN** permite consulta, mas não oferece ação de assumir, atribuir, reatribuir ou liberar

#### Scenario: Status não é alterado pela fila
- **WHEN** um usuário executa uma ação de atribuição
- **THEN** o Reflex não envia nem oferece comando de mudança de status

#### Scenario: Sessão ou autorização rejeitada
- **WHEN** uma rota da fila responde HTTP 401 ou 403
- **THEN** o Reflex encerra a sessão em 401, preserva a sessão em 403 e não trata proteção visual como autorização

#### Scenario: Erro de contrato ou carregamento da fila
- **WHEN** a consulta da fila recebe resposta incompatível, falha de rede ou filtro inválido
- **THEN** o Reflex informa o erro correspondente sem encerrar a sessão nem apresentar a falha como problema de identidade

#### Scenario: Jornada permanece somente leitura além da assunção
- **WHEN** um usuário consulta fila ou detalhe nesta change
- **THEN** a interface não oferece mudança de status, diagnóstico, solução, resolução ou cancelamento

### Requirement: Detalhe técnico preserva segurança e credenciais apartadas
A autoria exposta no detalhe global DEVE (MUST) representar apenas o ator lógico canônico do domínio e NÃO DEVE (MUST NOT) revelar, aceitar ou depender de cabeçalho, segredo, chave de automação, token de usuário ou variável de ambiente. Autenticação humana e autorização dos perfis globais permanecem aplicadas no Xano.

#### Scenario: Consumidor tenta informar autoria
- **WHEN** um consumidor tenta informar ou substituir autoria de sistema por payload, parâmetro ou credencial técnica em uma rota de leitura
- **THEN** o contrato não usa esse valor como autoridade e não modifica o chamado

## ADDED Requirements

### Requirement: Timeline global combina comentários e eventos estruturados
A timeline do chamado DEVE (MUST) apresentar comentários existentes e eventos de atribuição, reatribuição e liberação em uma única ordem cronológica. Eventos de responsável NÃO DEVEM (MUST NOT) ser armazenados somente como texto de comentário e DEVEM identificar tipo, chamado, autor, instante e Técnico anterior e novo quando aplicável.

#### Scenario: Comentários e mudanças de responsável intercalados
- **WHEN** um chamado possui comentários e eventos de responsável com instantes distintos
- **THEN** Técnico, Diretoria e Administrador veem todos na mesma timeline em ordem cronológica do evento

#### Scenario: Atribuição, reatribuição e liberação na timeline
- **WHEN** o Xano registra uma dessas operações
- **THEN** a timeline mostra o tipo do evento, seu autor, instante e responsáveis anterior e resultante quando aplicáveis

#### Scenario: Interações históricas
- **WHEN** uma interação existente não possui tipo de evento estruturado
- **THEN** ela continua apresentada como comentário sem backfill ou autoria inventada

#### Scenario: Mudança de status
- **WHEN** esta change é aplicada
- **THEN** nenhuma operação ou evento de mudança de status é acrescentado à timeline por esta change
