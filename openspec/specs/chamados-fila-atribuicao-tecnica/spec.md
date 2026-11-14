# chamados-fila-atribuicao-tecnica Specification

## Purpose

Definir a fila técnica de consulta global do MIRA, com filtros explícitos,
escopos aprovados, detalhe canônico e histórico compatível para Técnico,
Diretoria e Administrador, sem definir a tratativa operacional.

## Requirements

### Requirement: Ordenação global é autorizada e estável no Xano
O Xano DEVE (MUST) ordenar a fila global antes de responder. Aceita somente
`numero`, `titulo`, `status`, `prioridade`, `totem`, `categoria`, `aberto_por`, `responsavel`, `criado_em` e
`ultima_atualizacao_em`, com `ASC` ou `DESC`; `numero` e os timestamps
funcionais são numéricos e os demais campos são textuais sem distinção de
caixa. `criado_em` e `ultima_atualizacao_em` DEVEM (MUST) ordenar
cronologicamente. `id` DEVE (MUST) desempatar de forma estável na mesma direção.
O padrão é `numero` em `DESC`, mapeado internamente para `chamados.id`; ao
escolher nova coluna, a interface inicia em `ASC` e novo clique alterna a
direção. `id` NÃO DEVE (MUST NOT) ser exposto como coluna ou campo adicional de
ordenação. Limpar filtros NÃO DEVE (MUST NOT) alterar a ordenação persistida.

#### Scenario: Filtro e ordenação combinados
- **WHEN** usuário aplica filtros válidos e escolhe ordenação autorizada
- **THEN** o Xano retorna a interseção filtrada na ordem solicitada, sem ordenar
  somente a coleção local

#### Scenario: Empate ordenado
- **WHEN** dois chamados possuem o mesmo valor na coluna ordenada
- **THEN** o Xano os ordena por `id` na mesma direção escolhida

#### Scenario: Ordenação inválida
- **WHEN** cliente informa campo ou direção fora da whitelist
- **THEN** o Xano responde HTTP 422 sem retornar lista ou alterar preferência

#### Scenario: Limpeza preserva ordenação
- **WHEN** usuário limpa filtros com ordenação previamente confirmada
- **THEN** a lista remove somente os filtros e preserva a mesma ordenação

#### Scenario: Filtro por Técnico responsável
- **WHEN** usuário seleciona um Técnico do catálogo disponível
- **THEN** a consulta usa o identificador desse Técnico e retorna somente os
  chamados atualmente atribuídos a ele

#### Scenario: Filtro Não atribuído
- **WHEN** usuário seleciona `Não atribuído`
- **THEN** a consulta retorna somente chamados sem Técnico responsável

#### Scenario: Ordenação por responsável
- **WHEN** usuário ordena por Responsável em ASC ou DESC
- **THEN** o Xano ordena pelo mesmo texto exibido na coluna, usando o nome do
  Técnico ou `Não atribuído`, sem diferenciar caixa e nunca pelo identificador;
  esse rótulo participa da ordem alfabética nas duas direções e empates usam
  `id` na direção solicitada

#### Scenario: Ordenação por quem abriu o chamado
- **WHEN** usuário ordena por Aberto por em ASC ou DESC
- **THEN** o Xano ordena pelo mesmo texto apresentado na coluna sem diferenciar
  caixa e desempata por `id` na direção solicitada

#### Scenario: Responsável persiste por escopo
- **WHEN** Técnico confirma o filtro ou a ordenação por Responsável em um escopo
- **THEN** a preferência daquele escopo preserva esses critérios sem alterar a
  preferência do outro escopo

#### Scenario: Coluna de atribuição não integra a fila global
- **WHEN** usuário consulta a tabela da fila global
- **THEN** a tabela não exibe a coluna `Atribuído em`, sem remover o dado dos
  detalhes, APIs ou histórico

### Requirement: Fila global comunica a direção da ordenação
A fila global de Técnico, Diretoria e Administrador DEVE (MUST) exibir, junto
ao título ordenável ativo, somente a seta da direção confirmada: subida para
`ASC` e descida para `DESC`. Títulos inativos NÃO DEVEM (MUST NOT) exibir seta,
e a interface NÃO DEVE (MUST NOT) exibir os literais `ASC` ou `DESC`.

#### Scenario: Direção ativa na fila global
- **WHEN** a fila é exibida com uma coluna e direção confirmadas
- **THEN** somente o ícone correspondente à direção ativa aparece no respectivo
  cabeçalho, e os demais cabeçalhos não exibem ícone

#### Scenario: Alternância conserva a ordenação existente
- **WHEN** usuário clica um título ordenável da fila global
- **THEN** o mecanismo atual solicita a ordenação correspondente e atualiza o
  destaque para a direção confirmada, sem alterar filtros, preferências ou
  demais colunas

### Requirement: Preferências da fila pertencem ao usuário autenticado
O Xano DEVE (MUST) persistir uma preferência canônica por usuário autenticado e
escopo permitido. Um save válido substitui integralmente a preferência anterior
do mesmo usuário+escopo; a última escrita válida vence. O cliente NÃO DEVE
(MUST NOT) escolher o usuário da preferência.

#### Scenario: Usuários distintos
- **WHEN** dois usuários salvam filtros ou ordenação
- **THEN** cada um lê somente sua própria preferência, inclusive quando possuem
  o mesmo perfil

#### Scenario: Escritas concorrentes válidas
- **WHEN** duas escritas válidas atingem a mesma preferência de usuário+escopo
- **THEN** a última escrita válida persiste o conjunto completo de critérios

#### Scenario: Sessão ausente ou expirada
- **WHEN** consulta ou save de preferência ocorre sem sessão válida
- **THEN** o Xano responde HTTP 401 sem retornar ou alterar preferência

#### Scenario: Perfil ou escopo negado
- **WHEN** Gerente acessa a preferência global
- **THEN** o Xano responde HTTP 403 sem retornar ou alterar preferência

#### Scenario: Preferência inválida
- **WHEN** save informa filtro, Prioridade, Status, período, coluna ou direção inválidos
- **THEN** o Xano responde HTTP 422 sem alterar a última preferência válida

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
capacidade NÃO DEVE (MUST NOT) introduzir criador humano fictício, mudar
atribuição ou ampliar tratativa.

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

### Requirement: Detalhe técnico e fila apresentam autoria persistida
O Reflex DEVE (MUST) mostrar no detalhe técnico existente `Criado por: Bot de
Fiscalização` quando `criador_sistema` for `bot_fiscalizacao`, mantendo
`Origem: Automático` como informação distinta. Quando `criador_sistema` for
nulo, a interface NÃO DEVE (MUST NOT) inventar o Bot no detalhe. A fila técnica
DEVE (MUST) mostrar a coluna não ordenável `Aberto por` imediatamente antes de
`Responsável`: chamados automáticos mostram `Bot de Fiscalização`, chamados
manuais mostram o nome do solicitante e registros sem identificação mostram
`Não informado`, sem criar filtro ou alterar a ordenação existente.

#### Scenario: Detalhe técnico de incidente de heartbeat
- **WHEN** o detalhe técnico recebe um chamado automático atual com
  `criador_sistema = "bot_fiscalizacao"`
- **THEN** a interface apresenta o Bot como criador e a origem automática em
  campos separados

#### Scenario: Fila técnica mostra quem abriu o chamado
- **WHEN** a fila recebe chamados automáticos, manuais e sem identificação
- **THEN** a coluna `Aberto por`, antes de `Responsável`, mostra respectivamente
  `Bot de Fiscalização`, o nome persistido do solicitante ou `Não informado`

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

### Requirement: Fila global inclui filtros básicos completos e Loja

A fila de Técnico, Diretoria e Administrador DEVE (MUST) oferecer número,
Status, Totem, período de abertura, período de última atualização e Loja, além
dos filtros globais já aprovados. Loja DEVE (MUST) aparecer como coluna e todos
os critérios DEVEM (MUST) ser filtrados no Xano e persistidos por usuário e
escopo sem alterar ordenação ou escopo rápido.

#### Scenario: Filtro de Loja confirmado
- **WHEN** perfil global aplica Loja válida junto aos demais filtros
- **THEN** a resposta contém somente chamados daquela Loja e a preferência
  restaurada conserva o mesmo identificador de Loja

#### Scenario: Última atualização confirmada
- **WHEN** perfil global confirma período de última atualização
- **THEN** a fila retorna somente chamados atualizados no intervalo inclusivo e
  restaura o período após novo login

#### Scenario: Loja inválida
- **WHEN** o cliente informa Loja inexistente ou inválida
- **THEN** o Xano responde 422 sem consultar ou alterar a preferência válida

### Requirement: Fila global ordena pela Loja exibida

A coluna Loja da fila global DEVE (MUST) ser ordenável. O primeiro clique DEVE
(MUST) solicitar ordem ascendente e o clique seguinte ordem descendente; o
cabeçalho ativo DEVE (MUST) exibir somente a seta correspondente. O Xano DEVE
(MUST) ordenar pelo nome de Loja exibido, sem depender da ordenação local do
Reflex, e desempatar pelo ID do chamado. A ordenação DEVE (MUST) permanecer na
preferência existente, isolada por usuário e escopo.

#### Scenario: Loja ascendente persistida
- **WHEN** perfil global ordena a coluna Loja pela primeira vez
- **THEN** o Xano retorna as Lojas em ordem alfabética ascendente, desempata
  pelo ID e a preferência do mesmo usuário e escopo passa a usar `loja` e
  `ASC`

#### Scenario: Loja descendente persistida
- **WHEN** perfil global aciona novamente a coluna Loja já ativa
- **THEN** o Xano retorna as Lojas em ordem alfabética descendente, desempata
  pelo ID e a preferência do mesmo usuário e escopo passa a usar `loja` e
  `DESC`

### Requirement: Detalhe global direciona ao Monitoramento do Totem

O detalhe autorizado a Técnico, Diretoria e Administrador DEVE (MUST) oferecer
ação para abrir `/monitoramento` com o Totem do chamado selecionado. A seleção
DEVE (MUST) sobreviver à recarga pela URL e manter a autorização consolidada do
Monitoramento.

#### Scenario: Abertura do detalhe do Totem
- **WHEN** perfil global aciona Detalhe do Totem em chamado autorizado
- **THEN** a rota abre o painel existente com aquele Totem carregado

#### Scenario: Perfil não autorizado
- **WHEN** perfil sem acesso ao Monitoramento manipula a URL de seleção
- **THEN** a rota mantém sua negação consolidada sem expor dados do Totem

### Requirement: Fila global organiza filtros e tabela sem mudar consulta
A fila global DEVE (MUST) identificar cada filtro existente por rótulo visível,
organizar os períodos `Abertura` e `Atualização` com `De`/`Até` alinhados e
apresentar tabela legível. Cabeçalhos DEVEM (MUST) ser centralizados, rose com
texto branco forte e manter a seta somente na ordenação ativa. As ações DEVEM
(MUST) permanecer alinhadas no topo do painel de filtros, e a borda arredondada
da tabela NÃO DEVE (MUST NOT) ser encoberta pelo conteúdo interno. Categoria
DEVE (MUST) priorizar quebra visual após `/`, sem alterar valor, filtros,
ordenação ou resultados.

A coluna `Título` DEVE (MUST) receber o espaço remanescente para leitura; as
demais colunas DEVEM (MUST) compartilhar larguras equivalentes e centralizar
seu conteúdo vertical e horizontalmente. A célula de título DEVE (MUST)
apresentar o título e uma prévia compacta da descrição já retornada pela fila,
no mesmo padrão visual da lista do Gerente.

O hover dos cabeçalhos ordenáveis DEVE (MUST) modificar somente o fundo rose,
sem deslocamento, e a tabela DEVE (MUST) acomodar todas as colunas no desktop
sem barra horizontal.
A fila global NÃO DEVE (MUST NOT) exibir uma coluna separada `Ações`; o número
do chamado DEVE (MUST) continuar oferecendo o acesso existente ao detalhe.

#### Scenario: Perfil global usa filtros existentes
- **WHEN** Técnico, Diretoria ou Administrador abre a fila global
- **THEN** todos os filtros, períodos e ações continuam disponíveis com os
  mesmos valores e persistências, em grade visualmente identificada e alinhada

#### Scenario: Perfil global seleciona período em calendário
- **WHEN** o usuário abre `Abertura` ou `Atualização` e escolhe um primeiro e
  um segundo dia
- **THEN** o calendário rose preenche visualmente os mesmos valores `De` e
  `Até` já usados pelo filtro, sem consultar ou persistir dados antes da ação
  existente de aplicar

#### Scenario: Perfil global ordena a tabela
- **WHEN** o usuário altera a ordenação existente
- **THEN** somente o cabeçalho da coluna ativa exibe o indicador ascendente ou
  descendente, sem alteração no contrato de ordenação

#### Scenario: Perfil global abre o detalhe pela listagem
- **WHEN** Técnico, Diretoria ou Administrador seleciona o número do chamado
- **THEN** o detalhe existente é aberto sem depender de uma coluna `Ações`

#### Scenario: Perfil global identifica a ocorrência na listagem
- **WHEN** a fila global apresenta um chamado
- **THEN** a coluna de título exibe o título na primeira linha e uma prévia da
  descrição abaixo, sem consulta ou dado adicional

### Requirement: Detalhe operacional compacta apresentação sem mudar tratativa
O detalhe global DEVE (MUST) agrupar informações existentes em grid compacto de
rótulos e valores, inclusive Origem, e apresentar a linha do tempo em cards
compactos. Data e, somente para comentários, visibilidade DEVEM (MUST) ficar à
direita, sem alterar comentário, evento, ordem cronológica ou controles de
tratativa. Eventos operacionais NÃO DEVEM (MUST NOT) exibir classificação ou
badge de visibilidade.

Os dados do detalhe DEVEM (MUST) usar painel único e limpo com labels fortes e
descrição em área própria. O campo de comentário DEVE (MUST) aplicar sua borda
rose diretamente ao controle, sem fundo intermediário.

O cabeçalho do detalhe DEVE (MUST) apresentar número e título com a mesma
tipografia no formato `Chamado #ID - título`, mantendo a ação do Totem maior e
com texto forte. O painel de dados DEVE (MUST) conter somente cabeçalho e grid;
descrição e composição de comentário/tratativa DEVEM (MUST) ficar fora dele em
todos os perfis globais. A origem DEVE (MUST) ser exibida em maiúsculas sem
alterar o valor recebido.
A descrição DEVE (MUST) usar a mesma superfície branca do painel de dados.

#### Scenario: Linha do tempo existente é exibida
- **WHEN** o detalhe contém comentário ou evento autorizado
- **THEN** autor, conteúdo e data permanecem disponíveis na mesma ordem;
  comentário com classificação explícita exibe sua visibilidade em badge
  discreto à direita, e evento operacional não exibe classificação nem badge

#### Scenario: Tratativa e histórico mantêm acabamento compacto
- **WHEN** um perfil global visualiza o detalhe autorizado
- **THEN** número, título e ação existente do Totem compartilham o cabeçalho,
  campos e comentário usam borda rose sutil, e múltiplas alterações do mesmo
  evento são exibidas em grade de duas colunas sem alterar fatos, ordem ou acesso

### Requirement: Fila global aceita múltiplas opções nos filtros existentes
Status, Totem, Loja, Responsável e Prioridade DEVEM (MUST) aceitar zero ou mais opções na fila global. Cada dropdown DEVE (MUST) indicar as opções selecionadas e permitir marcá-las ou desmarcá-las sem remover as demais. A alteração permanece em rascunho até `Aplicar`; `Limpar filtros` remove todas as seleções desses filtros.

#### Scenario: Seleção de vários Status
- **WHEN** o usuário marca todos os Status exceto Encerrado e aplica os filtros
- **THEN** a consulta recebe todas as opções marcadas e pode retornar chamados em qualquer um desses Status, sem retornar Encerrado apenas por esse critério

#### Scenario: Seleção e desmarcação no dropdown
- **WHEN** o usuário marca duas opções e desmarca uma antes de Aplicar
- **THEN** o dropdown mantém indicada somente a opção restante e nenhuma consulta ou preferência é alterada antes de Aplicar

#### Scenario: Limpeza das coleções
- **WHEN** o usuário aciona `Limpar filtros`
- **THEN** todas as seleções múltiplas são esvaziadas, preservando o escopo rápido e a ordenação confirmados

### Requirement: Coleções combinam OR interno e AND entre filtros
O Xano DEVE (MUST) validar as coleções e combinar os valores do mesmo filtro com OR e filtros diferentes com AND. Coleção vazia NÃO DEVE (MUST NOT) restringir a consulta. Número, períodos, ordenação e escopo rápido DEVEM (MUST) conservar o comportamento vigente e participar da interseção quando informados.

#### Scenario: OR dentro de Status e Prioridade
- **WHEN** a consulta informa vários Status e várias Prioridades
- **THEN** cada chamado retornado corresponde a pelo menos um Status selecionado E a pelo menos uma Prioridade selecionada

#### Scenario: AND entre filtros diferentes
- **WHEN** a consulta combina Totens, Lojas e Responsáveis selecionados
- **THEN** cada chamado retornado corresponde a um Totem selecionado E a uma Loja selecionada E a um Responsável selecionado

#### Scenario: Não atribuído integra Responsável
- **WHEN** a consulta inclui `Não atribuído` junto de um ou mais Técnicos selecionados
- **THEN** o resultado pode conter chamados sem responsável OU atribuídos a qualquer Técnico selecionado, respeitando os demais filtros

#### Scenario: Valor inválido em coleção
- **WHEN** qualquer coleção contém opção inexistente, não reconhecida após a normalização vigente ou não autorizada
- **THEN** o Xano responde 422 sem retornar uma consulta parcial nem alterar a preferência confirmada

#### Scenario: Status normalizados em coleção
- **WHEN** a coleção de Status contém literais válidos com variação de maiúsculas e minúsculas
- **THEN** o Xano aceita cada opção sem diferenciar caixa e usa os respectivos literais canônicos na consulta e na preferência

### Requirement: Preferência global persiste coleções por usuário e escopo
Aplicar ou limpar DEVE (MUST) substituir integralmente as coleções confirmadas na preferência do usuário e escopo atuais. `Todos` e `Atribuídos a mim` permanecem isolados; os três perfis operacionais podem consultar ambos os escopos. Preferência anterior com valor escalar DEVE (MUST) ser restaurada como coleção unitária, sem exigir backfill.

#### Scenario: Restauração após novo login
- **WHEN** um usuário salva múltiplos valores, encerra a sessão e autentica novamente
- **THEN** a preferência de `Todos` restaura todas as seleções confirmadas antes da consulta

#### Scenario: Isolamento entre escopos do Técnico
- **WHEN** um Técnico confirma coleções diferentes em `Todos` e `Atribuídos a mim`
- **THEN** cada escopo restaura apenas suas próprias coleções

#### Scenario: Preferência escalar anterior
- **WHEN** o registro existente possui somente um valor escalar legado para filtro elegível e ainda não possui representação múltipla
- **THEN** o contrato o devolve como coleção com um elemento, preservando o valor confirmado

#### Scenario: Preferência nova explicitamente vazia
- **WHEN** a representação múltipla existe com coleções vazias após Limpar e o registro ainda contém valor escalar histórico
- **THEN** as coleções vazias prevalecem e nenhum filtro histórico reaparece após navegação ou novo login

#### Scenario: Não atribuído sem ID sentinela
- **WHEN** a preferência inclui chamados não atribuídos e Técnicos específicos
- **THEN** o contrato preserva os IDs positivos dos Técnicos separadamente da indicação booleana de incluir chamados sem responsável

#### Scenario: Rascunho não persiste
- **WHEN** o usuário marca ou desmarca opções sem Aplicar nem Limpar
- **THEN** nenhuma coleção persistida é modificada

### Requirement: Fila global preserva Loja histórica de chamados
Quando um Totem muda de Loja, a fila, o detalhe e filtros por Loja DEVEM (MUST) usar o vínculo demonstrável no `criado_em` de cada chamado, sem reclassificar fatos anteriores pelo vínculo atual. Chamado sem Loja histórica comprovável DEVE (MUST) continuar na consulta global sem atribuição de Loja presumida.

#### Scenario: Filtro por Loja após transferência
- **WHEN** perfil global filtra a fila pela Loja de origem após transferência de Totem com histórico comprovado
- **THEN** chamados anteriores à transferência continuam nesse resultado e novos chamados pertencem à Loja de destino

#### Scenario: Chamado legado sem Loja comprovada
- **WHEN** um chamado global não possui vínculo histórico demonstrável
- **THEN** permanece consultável na fila global sem Loja atribuída e não aparece indevidamente em filtro por Loja atual do Totem

### Requirement: Fila global oferece escopos comuns aos perfis operacionais
A fila global DEVE (MUST) manter os filtros explícitos de número, Status,
Totem, Responsável e período de abertura e adicionar Prioridade canônica.
O filtro Responsável DEVE (MUST) usar o identificador de Técnico e aceitar a
opção `Não atribuído` para chamados sem responsável. Técnico, Diretoria e
Administrador DEVEM (MUST) manter preferências independentes de filtros e
ordenação para `Todos` e `Atribuídos a mim`. A seleção de escopo rápido NÃO DEVE (MUST NOT) persistir: todo login
inicia em `Todos`.

#### Scenario: Visão de chamados não atribuídos
- **WHEN** um Técnico consulta a fila global
- **THEN** a interface não apresenta uma visão rápida de chamados não atribuídos

#### Scenario: Visão de chamados atribuídos a mim
- **WHEN** um Técnico seleciona `Atribuídos a mim`
- **THEN** o Xano retorna somente chamados cujo responsável atual é o próprio Técnico autenticado

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** um chamado possui responsável diferente do usuário autenticado
- **THEN** ele continua consultável em `Todos`, sem criar visão específica

#### Scenario: Status nulo ou inelegível
- **WHEN** um chamado possui status nulo ou qualquer status persistido
- **THEN** o Xano não infere nem altera o status e a fila não o exclui apenas por ser diferente de `Novo`

#### Scenario: Visão inválida
- **WHEN** consulta ou preferência informa literal de escopo desconhecido, ou
  combinação contraditória de escopo
- **THEN** o Xano responde HTTP 422 sem retornar dados, salvar preferência ou
  inferir escopo

#### Scenario: Ordenação e ausência de paginação
- **WHEN** a consulta válida retorna chamados
- **THEN** os itens seguem a ordenação autorizada e estável e a resposta não
  introduz paginação ou busca avançada

#### Scenario: Escopo rápido combina com filtros operacionais
- **WHEN** um Técnico seleciona `Atribuídos a mim` e informa filtros válidos
- **THEN** o Xano retorna a interseção entre responsável, filtros e ordenação

#### Scenario: Limpeza preserva escopo rápido atual
- **WHEN** um Técnico limpa os filtros operacionais dentro de `Atribuídos a mim`
- **THEN** a consulta remove filtros, mantém o escopo atual até nova seleção e
  preserva sua ordenação

#### Scenario: Todos sem filtro
- **WHEN** um perfil autorizado consulta a fila sem filtros
- **THEN** o Xano retorna todos os chamados globais permitidos, inclusive atribuídos, não atribuídos, terminais e não terminais

#### Scenario: Consulta global por Diretoria ou Administrador
- **WHEN** um usuário autenticado de Diretoria ou Administrador consulta a fila
- **THEN** o Xano retorna a mesma visão global de chamados permitida ao Técnico

#### Scenario: Interseção de filtros explícitos
- **WHEN** perfil autorizado combina filtros válidos
- **THEN** o Xano retorna somente os chamados que correspondem à interseção

#### Scenario: Responsável não cria visão de navegação
- **WHEN** um chamado possui ou não possui Técnico responsável
- **THEN** ele permanece na tabela global e a interface não apresenta outras
  visões de atribuição

#### Scenario: Falha de consulta não confirma filtro no Reflex
- **WHEN** pesquisa, filtro ou ordenação candidata falha antes de confirmação
- **THEN** o Reflex mantém o último filtro, ordenação e resultado confirmados

#### Scenario: Gerente tenta consultar a fila global
- **WHEN** um Gerente tenta consultar a fila global
- **THEN** o Xano responde HTTP 403 sem expor chamados fora de seus contratos

#### Scenario: Preferências independentes do Técnico
- **WHEN** Técnico aplica filtros ou ordenação em um escopo e troca para o outro
- **THEN** a fila carrega somente a preferência persistida daquele escopo, sem
  reutilizar os critérios do escopo anterior

#### Scenario: Login não restaura escopo pessoal
- **WHEN** Técnico encerra sessão após usar `Atribuídos a mim` e autentica novamente
- **THEN** inicia em `Todos` e carrega somente a preferência persistida de `Todos`

#### Scenario: Escopo pessoal compartilhado
- **WHEN** Diretoria ou Administrador carrega ou salva preferência da fila
- **THEN** pode usar `Atribuídos a mim`, com a mesma regra por identidade autenticada e sem se tornar elegível a responsável

#### Scenario: Filtros aplicados são persistidos
- **WHEN** um perfil global aplica ou limpa filtros válidos
- **THEN** somente número, Status, Totem, Responsável, período, Prioridade e ordenação
  confirmados são persistidos para seu usuário e escopo

#### Scenario: Rascunho não é preferência
- **WHEN** usuário edita filtros, mas não aplica nem limpa
- **THEN** nenhuma preferência durável é alterada

#### Scenario: Status normalizado
- **WHEN** Status válido é informado com variação de maiúsculas e minúsculas
- **THEN** o Xano o aceita sem diferenciar caixa, consulta pelo literal canônico
  e persiste esse literal

#### Scenario: Falha de lista ou persistência
- **WHEN** a consulta ou o save da preferência falha
- **THEN** o Reflex mantém o último resultado, filtros e ordenação confirmados,
  informa a falha e não confirma a preferência candidata

#### Scenario: Consulta candidata antecede persistência
- **WHEN** usuário aplica, limpa ou ordena uma preferência candidata válida
- **THEN** o Reflex consulta primeiro a lista candidata, salva somente após seu
  sucesso e confirma State e lista somente após ambas as etapas

### Requirement: Reflex oferece jornada operacional compartilhada
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

#### Scenario: Escopo rápido acessível aos perfis operacionais
- **WHEN** Diretoria ou Administrador acessa a fila
- **THEN** a interface apresenta os mesmos escopos de consulta do Técnico

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

### Requirement: Jornada operacional compartilhada usa rotas canônicas de chamados
O Reflex DEVE (MUST) apresentar a fila global existente em `/inicio` e `/chamados` e seu detalhe operacional existente em `/chamados/[chamado_id]` para Técnico, Diretoria e Administrador. A jornada DEVE reutilizar `ChamadosTecnicoState`, componentes, filtros, timeline e tratativa atuais; ela NÃO DEVE (MUST NOT) converter Diretoria ou Administrador em responsável de chamado.

#### Scenario: Perfil global acessa início ou lista canônica
- **WHEN** Técnico, Diretoria ou Administrador autenticado acessa `/inicio` ou `/chamados`
- **THEN** o Reflex revalida a identidade e apresenta a fila global existente

#### Scenario: Detalhe canônico global
- **WHEN** Técnico, Diretoria ou Administrador autenticado acessa `/chamados/[chamado_id]`
- **THEN** o Reflex carrega o detalhe, a timeline e a tratativa operacional existentes conforme o contrato atual

#### Scenario: Escopo rápido acessível aos perfis operacionais
- **WHEN** Técnico, Diretoria ou Administrador acessa a fila canônica
- **THEN** encontra os mesmos escopos de consulta; sua seleção não cria nem altera atribuições

#### Scenario: Troca de identidade não reutiliza o contexto da fila
- **WHEN** um Técnico usa `Atribuídos a mim`, encerra a sessão e outra identidade acessa `/inicio` ou `/chamados`
- **THEN** o Reflex descarta antes da consulta os dados, filtros e escopo da identidade anterior e solicita a fila apenas com o escopo permitido ao novo perfil
- **AND WHEN** o mesmo Técnico inicia uma nova sessão
- **THEN** os filtros desse usuário podem ser mantidos, mas `Atribuídos a mim` volta para `Todos`

#### Scenario: Navegação global canônica
- **WHEN** perfil global segue link de detalhe, retorna à fila ou seleciona `Início`
- **THEN** a navegação usa as rotas canônicas sem alterar filtros, contratos Xano ou comportamento de tratativa

#### Scenario: Gerente acessa rota global canônica
- **WHEN** Gerente tenta acessar uma rota que resolveria para a jornada global
- **THEN** o Reflex não apresenta a jornada global e o Xano continua respondendo 403 para contrato global indevido
