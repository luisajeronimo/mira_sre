# chamados-fila-atribuicao-tecnica Specification

## Purpose

Definir a fila técnica de consulta global do MIRA, com filtros explícitos,
escopos aprovados, detalhe canônico e histórico compatível para Técnico,
Diretoria e Administrador, sem definir a tratativa operacional.

## Requirements

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

### Requirement: Detalhe técnico distingue o criador de sistema
O detalhe global somente leitura de um chamado para Técnico DEVE (MUST) expor
`criador_sistema` separadamente de `origem`, `solicitante` e Técnico
responsável. Quando um chamado novo de heartbeat tiver
`criador_sistema = "bot_fiscalizacao"`, o contrato DEVE (MUST) preservar
origem automática, solicitante humano ausente e essa autoria de sistema. Esta
capacidade NÃO DEVE (MUST NOT) introduzir criador humano fictício, alterar as
visões da fila, incluir coluna de autoria na lista, mudar atribuição ou ampliar
tratativa.

#### Scenario: Técnico consulta chamado automático atual
- **WHEN** um Técnico autenticado consulta o detalhe de chamado criado pelo
  heartbeat após esta capacidade
- **THEN** o contrato retorna `origem = "automatico"`, `solicitante = null` e
  `criador_sistema = "bot_fiscalizacao"` como campos distintos

#### Scenario: Técnico consulta chamado manual
- **WHEN** um Técnico autenticado consulta o detalhe de chamado manual
- **THEN** o contrato preserva o solicitante humano existente e retorna
  `criador_sistema = null`

#### Scenario: Técnico consulta chamado legado
- **WHEN** um Técnico autenticado consulta um chamado sem autoria de sistema
  persistida
- **THEN** o contrato retorna `criador_sistema = null` sem fabricar autoria
  histórica

### Requirement: Detalhe técnico preserva segurança e credenciais apartadas
A autoria exposta no detalhe global DEVE (MUST) representar apenas o ator lógico canônico do domínio e NÃO DEVE (MUST NOT) revelar, aceitar ou depender de cabeçalho, segredo, chave de automação, token de usuário ou variável de ambiente. Autenticação humana e autorização dos perfis globais permanecem aplicadas no Xano.

#### Scenario: Consumidor tenta informar autoria
- **WHEN** um consumidor tenta informar ou substituir autoria de sistema por payload, parâmetro ou credencial técnica em uma rota de leitura
- **THEN** o contrato não usa esse valor como autoridade e não modifica o chamado

### Requirement: Detalhe técnico apresenta o Bot sem ampliar a fila
O Reflex DEVE (MUST) mostrar no detalhe técnico existente `Criado por: Bot de
Fiscalização` quando `criador_sistema` for `bot_fiscalizacao`, mantendo
`Origem: Automático` como informação distinta. Quando `criador_sistema` for
nulo, a interface NÃO DEVE (MUST NOT) inventar o Bot. A fila técnica e suas
colunas permanecem inalteradas.

#### Scenario: Detalhe técnico de incidente de heartbeat
- **WHEN** o detalhe técnico recebe um chamado automático atual com
  `criador_sistema = "bot_fiscalizacao"`
- **THEN** a interface apresenta o Bot como criador e a origem automática em
  campos separados, sem adicionar coluna à fila

#### Scenario: Detalhe técnico de registro sem autoria
- **WHEN** o detalhe técnico recebe `criador_sistema = null`
- **THEN** a interface não mostra o Bot como criador e continua apresentando os
  demais dados disponíveis sem inferência

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
O sistema DEVE (MUST) substituir, na jornada operacional, comandos imediatos de assumir, atribuir, reatribuir e liberar por Save pendente de Responsável. A fila e o detalhe permanecem contratos de consulta; ao concluir esta change, somente o Save transacional é caminho funcional autorizado para mudança de responsável, sem alterar status.

#### Scenario: Detalhe não oferece controles imediatos de responsável
- **WHEN** Técnico, Diretoria ou Administrador abre um chamado não terminal
- **THEN** a jornada operacional apresenta apenas o campo `Responsável` e o botão Salvar, sem controles separados Assumir, Atribuir, Reatribuir ou Liberar

#### Scenario: Contratos anteriores não formam caminho alternativo de tratativa
- **WHEN** a migração técnica interna concluir
- **THEN** comandos imediatos anteriores não permanecem autorizados como caminho funcional alternativo para alterar Responsável

#### Scenario: Fila preserva escopo e consulta
- **WHEN** um perfil autorizado consulta a fila global ou o detalhe
- **THEN** Todos, Atribuídos a mim, filtros, pesquisa, tabela e DTO de consulta mantêm seu comportamento aprovado

#### Scenario: Atribuição via Save válida
- **WHEN** um perfil operacional salva Responsável Técnico em chamado não terminal sem responsável
- **THEN** o Save aplica atribuição conforme a spec de tratativa, sem usar comando imediato

#### Scenario: Save sem diferença de Responsável
- **WHEN** o Save informa Responsável igual ao já persistido e não há outra diferença funcional
- **THEN** o Xano retorna o detalhe sem alterar `tecnico_id`, `atribuido_em`, `ultima_atualizacao_em` ou histórico

#### Scenario: Responsável divergente no Save
- **WHEN** o estado persistido no momento do Save diverge do rascunho de responsável do cliente
- **THEN** o Xano valida o estado atual e não sobrescreve silenciosamente mudança incompatível

#### Scenario: Dois Técnicos concorrem
- **WHEN** duas pessoas salvam mudanças de Responsável simultaneamente
- **THEN** o Xano aplica a transação conforme o estado persistido e retorna o detalhe canônico sem afirmar garantia matemática além dos recursos Free

#### Scenario: Chamado inelegível para edição funcional
- **WHEN** o Save tenta editar Responsável de chamado Encerrado, Cancelado ou com estado inválido
- **THEN** o Xano rejeita a transação sem efeito parcial

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** o responsável atual é Técnico diferente do ator autenticado
- **THEN** Técnico, Diretoria e Administrador podem selecioná-lo ou trocá-lo pelo Save conforme a autorização da tratativa

#### Scenario: Campos sob autoridade do Xano
- **WHEN** o cliente informa timestamp, autor de evento ou valores funcionais fora do contrato
- **THEN** o Xano rejeita ou ignora esses valores sem permitir substituir regras de backend

#### Scenario: Registro legado
- **WHEN** a consulta encontra chamado existente sem data de atribuição persistida
- **THEN** o registro é preservado e `atribuido_em` permanece nulo quando não houver valor persistido

#### Scenario: Dados retornados pelo detalhe
- **WHEN** o chamado possui responsável e data de atribuição persistidos
- **THEN** o detalhe canônico os retorna sem inferir ou alterar valores

### Requirement: Autorização e erros da consulta técnica são estáveis
Os contratos de consulta e tratativa global DEVEM (MUST) exigir autenticação e aplicar no Xano os perfis e regras funcionais autorizados. Falha de sessão DEVE (MUST) ser 401, perfil ou escopo sem permissão 403, chamado inexistente 404, entrada ou estado funcional inválido 422 e falha interna 5xx; CRUD genérico NÃO DEVE (MUST NOT) contornar a autorização.

#### Scenario: Erro de autenticação e autorização
- **WHEN** uma chamada de tratativa recebe sessão inválida ou perfil sem permissão
- **THEN** o Xano responde respectivamente 401 ou 403 sem alterar chamado ou interações

#### Scenario: Contrato de Save inválido
- **WHEN** o cliente informa valor incompatível para o Save
- **THEN** o Xano responde 422 sem persistir efeito parcial

#### Scenario: Sessão ausente
- **WHEN** rota de consulta ou tratativa recebe requisição sem sessão válida
- **THEN** o Xano responde 401 sem consultar ou alterar chamado

#### Scenario: Perfil sem acesso global
- **WHEN** um Gerente solicita a fila ou detalhe técnico global
- **THEN** o Xano responde 403 sem expor dados

#### Scenario: Gerente ou Diretoria tenta usar rota técnica
- **WHEN** Gerente usa rota global ou perfil não autorizado usa operação fora da tratativa prevista
- **THEN** o Xano responde 403 sem expor ou alterar chamado

#### Scenario: CRUD genérico continua negado
- **WHEN** usuário tenta alterar chamado por CRUD genérico
- **THEN** nenhum chamado é modificado

### Requirement: Reflex oferece jornada técnica de consulta global
O Reflex DEVE (MUST) preservar a fila e o detalhe globais existentes e acrescentar a tratativa pendente somente ao detalhe. A interface DEVE (MUST) manter Estado persistido e pendente distintos, usar a resposta canônica pós-commit depois de Salvar e manter erro, carregamento, vazio e sucesso mutuamente coerentes.

#### Scenario: Save bem-sucedido atualiza o detalhe
- **WHEN** o Xano retorna sucesso para Save
- **THEN** o Reflex substitui valores persistidos e pendentes pelo detalhe retornado, sem alterar a fila por filtro local

#### Scenario: Save falha
- **WHEN** o Xano rejeita ou falha ao salvar
- **THEN** o Reflex informa a falha, conserva o detalhe persistido e não apresenta seleção pendente como se tivesse sido confirmada

#### Scenario: Status pendente exige comentário no Reflex
- **WHEN** o usuário altera Status no rascunho
- **THEN** o Reflex exige comentário associado antes de Salvar, fixa Público para Resolvido, Aguardando Solicitante e Cancelado e permite Público ou Interno para os demais destinos, sem substituir a validação definitiva do Xano

#### Scenario: Escopo rápido exclusivo do Técnico
- **WHEN** Diretoria ou Administrador acessa a fila
- **THEN** a interface preserva a tabela global sem apresentar `Atribuídos a mim`

#### Scenario: Técnico carrega a fila
- **WHEN** Técnico autenticado acessa a fila
- **THEN** o Reflex preserva a tabela global e seus estados aprovados de carregamento, vazio, sucesso e erro

#### Scenario: Chamado terminal
- **WHEN** a interface apresenta chamado `Encerrado` ou `Cancelado`
- **THEN** ela mantém o detalhe disponível para consulta e bloqueia edição funcional

#### Scenario: Save de Responsável bem-sucedido
- **WHEN** o Xano retorna sucesso para Save que atribui Responsável
- **THEN** o Reflex atualiza o detalhe pelo DTO canônico e a fila é atualizada ou recarregada sem aplicar filtro local

#### Scenario: Conflito ao salvar Responsável
- **WHEN** o Xano informa conflito ou estado divergente ao salvar responsável
- **THEN** o Reflex informa a falha sem substituir o detalhe confirmado e recarrega quando necessário

#### Scenario: Sessão ou autorização rejeitada
- **WHEN** rota de tratativa responde 401 ou 403
- **THEN** o Reflex encerra sessão em 401, preserva-a em 403 e não trata proteção visual como autorização

#### Scenario: Erro de contrato ou carregamento da fila
- **WHEN** a consulta da fila recebe resposta incompatível, falha de rede ou filtro inválido
- **THEN** o Reflex informa o erro correspondente sem encerrar a sessão nem apresentar a falha como problema de identidade

#### Scenario: Consulta não oferece controles imediatos de responsável
- **WHEN** um perfil apenas consulta fila ou detalhe sem editar o rascunho
- **THEN** a consulta não altera o chamado e a fila não passa a oferecer controles imediatos de responsável

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
