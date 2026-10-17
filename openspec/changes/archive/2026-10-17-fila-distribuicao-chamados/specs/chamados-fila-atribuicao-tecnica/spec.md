# Delta: chamados-fila-atribuicao-tecnica

## MODIFIED Requirements

### Requirement: Fila técnica oferece somente as visões aprovadas
O sistema DEVE (MUST) oferecer uma única tabela global de chamados para Técnico, Diretoria e Administrador, aplicando no Xano os mesmos filtros explícitos da listagem do Gerente: número, status, Totem e período de abertura. Sem filtros aplicados, `Todos` DEVE significar todos os chamados dentro do escopo global. O Técnico possui `Atribuídos a mim` como escopo rápido, não como preferência persistente; Diretoria e Administrador não o recebem. O Gerente NÃO DEVE acessar esta fila.

#### Scenario: Visão de chamados não atribuídos
- **WHEN** um Técnico consulta a fila global
- **THEN** a interface não apresenta uma visão rápida de chamados não atribuídos

#### Scenario: Visão de chamados atribuídos a mim
- **WHEN** um Técnico seleciona `Atribuídos a mim`
- **THEN** o Xano retorna somente chamados cujo responsável atual é o próprio Técnico autenticado

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** um chamado possui responsável diferente do usuário autenticado
- **THEN** ele continua consultável em `Todos`, sem criar uma visão ou filtro específico

#### Scenario: Status nulo ou inelegível
- **WHEN** um chamado possui status nulo ou qualquer status persistido
- **THEN** o Xano não infere nem altera o status e a fila não o exclui apenas por ser diferente de `Novo`

#### Scenario: Visão inválida
- **WHEN** uma requisição informa visão diferente de `Todos` ou `Atribuídos a mim` autorizados ao perfil
- **THEN** o Xano responde HTTP 422 sem retornar dados de uma visão implícita

#### Scenario: Ordenação e ausência de paginação
- **WHEN** a consulta válida retorna chamados
- **THEN** os itens são ordenados por `id` decrescente e a resposta não introduz paginação ou busca avançada nesta capacidade

#### Scenario: Escopo rápido combina com filtros operacionais
- **WHEN** um Técnico seleciona `Atribuídos a mim` e informa número, status, Totem ou período
- **THEN** o Xano retorna a interseção entre o responsável atual e os filtros explícitos

#### Scenario: Limpeza preserva escopo rápido atual
- **WHEN** um Técnico limpa os filtros operacionais dentro de `Atribuídos a mim`
- **THEN** a consulta remove número, status, Totem e período, mas mantém o escopo atual até o usuário selecionar outra visão

#### Scenario: Todos sem filtro
- **WHEN** um perfil autorizado consulta a fila sem filtros
- **THEN** o Xano retorna todos os chamados globais permitidos, inclusive atribuídos, não atribuídos, terminais e não terminais

#### Scenario: Consulta global por Diretoria ou Administrador
- **WHEN** um usuário autenticado de Diretoria ou Administrador consulta a fila
- **THEN** o Xano retorna a mesma visão global de chamados permitida ao Técnico

#### Scenario: Interseção de filtros explícitos
- **WHEN** um perfil autorizado pesquisa por número ou combina status, Totem e período de abertura
- **THEN** o Xano retorna somente os chamados que correspondem à interseção dos filtros enviados

#### Scenario: Responsável não cria visão de navegação
- **WHEN** um chamado possui ou não possui Técnico responsável
- **THEN** ele permanece na tabela global e a interface não apresenta `Atribuídos a outros Técnicos` ou `Não atribuídos` como visão de atribuição

#### Scenario: Falha de consulta não confirma filtro no Reflex
- **WHEN** uma pesquisa ou filtro solicitado falha antes de o Xano retornar a lista
- **THEN** o Reflex mantém o último filtro aplicado e seu resultado coerentes e informa a falha sem indicar o novo filtro como aplicado

#### Scenario: Gerente tenta consultar a fila global
- **WHEN** um Gerente tenta consultar a fila global
- **THEN** o Xano responde HTTP 403 sem expor chamados fora dos contratos próprios do Gerente

### Requirement: Listagem técnica retorna DTO funcional estável
O sistema DEVE (MUST) retornar em cada item da fila o DTO canônico de consulta, incluindo `id`, `titulo`, `status`, `prioridade`, `origem`, `criado_em`, `ultima_atualizacao_em`, `sla_horas_aplicado`, `atribuido_em`, ativo, categoria, solicitante e Técnico atual quando existir. Valores históricos ausentes DEVEM (MUST) permanecer nulos, sem inferência.

#### Scenario: Chamado manual na fila
- **WHEN** um chamado manual válido é retornado
- **THEN** a resposta preserva origem manual, prioridade, timestamps funcionais, snapshot de SLA, ativo, categoria e Técnico atual

#### Scenario: Chamado automático na fila
- **WHEN** um chamado automático válido é retornado
- **THEN** a resposta preserva origem automática, timestamps funcionais e os demais dados já persistidos, sem alterar a regra do heartbeat

#### Scenario: Chamado legado na consulta
- **WHEN** um registro histórico possui origem, SLA ou atribuição ausentes
- **THEN** a resposta preserva esses campos como nulos sem inferência

### Requirement: Detalhe técnico preserva segurança e credenciais apartadas
A autoria exposta no detalhe global DEVE (MUST) representar apenas o ator lógico canônico do domínio e NÃO DEVE (MUST NOT) revelar, aceitar ou depender de cabeçalho, segredo, chave de automação, token de usuário ou variável de ambiente. Autenticação humana e autorização dos perfis globais permanecem aplicadas no Xano.

#### Scenario: Consumidor tenta informar autoria
- **WHEN** um consumidor tenta informar ou substituir autoria de sistema por payload, parâmetro ou credencial técnica em uma rota de leitura
- **THEN** o contrato não usa esse valor como autoridade e não modifica o chamado

## ADDED Requirements

### Requirement: Perfis globais consultam detalhe técnico canônico
O sistema DEVE (MUST) fornecer detalhe global de chamado para Técnico, Diretoria e Administrador em DTO canônico, incluindo número, título, descrição, status, prioridade, origem, solicitante, Loja, Totem, categoria, SLA, responsável atual, `atribuido_em` e timeline. A leitura NÃO DEVE (MUST NOT) alterar o chamado; estados terminais continuam consultáveis.

#### Scenario: Detalhe sem responsável
- **WHEN** um perfil autorizado consulta chamado ainda sem responsável
- **THEN** o Xano retorna responsável e `atribuido_em` nulos, quando aplicável

#### Scenario: Detalhe com responsável
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

### Requirement: Dados de responsável e atribuição permanecem compatíveis
O sistema DEVE (MUST) manter `tecnico_id` e `atribuido_em` como dados de leitura do responsável atual e do início da atribuição atual, preservando registros históricos sem preenchimento retroativo. Esta capacidade não define a mutação desses campos.

#### Scenario: Registro legado
- **WHEN** a consulta encontra chamado existente sem data de atribuição persistida
- **THEN** o registro é preservado e `atribuido_em` permanece nulo quando não houver valor persistido

#### Scenario: Dados retornados pelo detalhe
- **WHEN** o chamado possui responsável e data de atribuição persistidos
- **THEN** o detalhe canônico os retorna sem inferir ou alterar valores

### Requirement: Autorização e erros da consulta técnica são estáveis
Os contratos da fila global DEVEM (MUST) exigir autenticação e aplicar no Xano os perfis autorizados, independentemente da interface Reflex.

#### Scenario: Sessão ausente
- **WHEN** uma rota da fila global recebe requisição sem sessão válida
- **THEN** o Xano responde HTTP 401 sem consultar ou alterar chamados

#### Scenario: Perfil sem acesso global
- **WHEN** um Gerente solicita a fila ou detalhe técnico global
- **THEN** o Xano responde HTTP 403 sem expor dados

### Requirement: Reflex oferece jornada técnica de consulta global
O Reflex DEVE (MUST) reutilizar a fila e o detalhe existentes para Técnico, Diretoria e Administrador, exibindo pesquisa por número, filtros explícitos, responsável atual e timeline. A interface NÃO substitui a autorização do Xano.

#### Scenario: Técnico carrega a fila
- **WHEN** um Técnico autenticado acessa a fila
- **THEN** o Reflex consulta o Xano e apresenta a tabela global com estados de carregamento, vazio, sucesso e erro

#### Scenario: Escopo rápido exclusivo do Técnico
- **WHEN** Diretoria ou Administrador acessa a fila
- **THEN** a interface apresenta `Todos`, sem oferecer `Atribuídos a mim`

#### Scenario: Chamado terminal
- **WHEN** a interface apresenta chamado `Encerrado` ou `Cancelado`
- **THEN** ela mantém o detalhe disponível para consulta

#### Scenario: Sessão ou autorização rejeitada
- **WHEN** uma rota da fila responde HTTP 401 ou 403
- **THEN** o Reflex encerra a sessão em 401, preserva a sessão em 403 e não trata proteção visual como autorização

#### Scenario: Erro de contrato ou carregamento da fila
- **WHEN** a consulta da fila recebe resposta incompatível, falha de rede ou filtro inválido
- **THEN** o Reflex informa o erro correspondente sem encerrar a sessão nem apresentar a falha como problema de identidade

### Requirement: Timeline global preserva comentários e eventos legados
A timeline do chamado DEVE (MUST) apresentar comentários existentes e eventos legados de atribuição, reatribuição e liberação em uma única timeline cronológica, do mais recente para o mais antigo, pelo instante efetivo e por `id` decrescente no empate. A capacidade preserva os dados estruturados existentes sem backfill ou conversão do histórico.

#### Scenario: Comentários e eventos legados intercalados
- **WHEN** um chamado possui comentários e eventos históricos de responsável com instantes distintos
- **THEN** Técnico, Diretoria e Administrador veem todos na mesma timeline do evento mais recente para o mais antigo

#### Scenario: Evento legado de responsável
- **WHEN** a timeline contém evento histórico de atribuição, reatribuição ou liberação
- **THEN** a interface mostra seu tipo, autor, instante e responsáveis anterior e resultante quando aplicáveis

#### Scenario: Interações históricas
- **WHEN** uma interação existente não possui tipo de evento estruturado
- **THEN** ela continua apresentada como comentário sem backfill ou autoria inventada

## REMOVED Requirements

### Requirement: Técnico pode consultar detalhe global somente leitura
**Reason**: O requisito anterior restringia a consulta aos pressupostos da assunção imediata.
**Migration**: O detalhe global de consulta é definido pelo requisito canônico adicionado nesta change.

### Requirement: Schema registra a atribuição sem backfill
**Reason**: A change não define mais mutação independente de responsável; preserva somente a leitura compatível desses dados.
**Migration**: A gestão operacional é definida pela change `tratativa-operacional-chamados`.

### Requirement: Assunção é autoatribuição idempotente com consistência best-effort no plano Free
**Reason**: O comando imediato de assunção foi substituído pelo Save operacional posterior.
**Migration**: Usar exclusivamente a tratativa definida em `tratativa-operacional-chamados`.

### Requirement: Autorização e erros da jornada técnica são estáveis
**Reason**: A regra anterior misturava consulta global com autorização de assunção obsoleta.
**Migration**: A autorização de consulta permanece nesta change; a operacional é definida pela change posterior.

### Requirement: Assunção efetiva atualiza a última atualização observável
**Reason**: A semântica de assunção imediata não é comportamento atual.
**Migration**: A atualização decorrente de Save é definida em `tratativa-operacional-chamados`.

### Requirement: Reflex oferece a jornada técnica mínima
**Reason**: A jornada anterior expunha o controle imediato `Assumir`.
**Migration**: A fila e o detalhe de consulta permanecem; a tratativa é definida pela change posterior.
