# Delta: chamados-fila-atribuicao-tecnica

## MODIFIED Requirements

### Requirement: Fila técnica oferece somente as visões aprovadas
A fila global DEVE (MUST) manter os filtros explícitos de número, Status,
Totem, Responsável e período de abertura e adicionar Prioridade canônica.
O filtro Responsável DEVE (MUST) usar o identificador de Técnico e aceitar a
opção `Não atribuído` para chamados sem responsável. Técnico DEVE
(MUST) manter preferências independentes de filtros e ordenação para `Todos` e
`Atribuídos a mim`; Diretoria e Administrador DEVEM (MUST) usar somente
`Todos`. A seleção de escopo rápido NÃO DEVE (MUST NOT) persistir: todo login
inicia em `Todos`.

#### Scenario: Visão de chamados não atribuídos
- **WHEN** um Técnico consulta a fila global
- **THEN** a interface não apresenta uma visão rápida de chamados não atribuídos

#### Scenario: Visão de chamados atribuídos a mim
- **WHEN** um Técnico seleciona `Atribuídos a mim`
- **THEN** o Xano retorna somente chamados cujo responsável atual é o próprio
  Técnico autenticado

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** um chamado possui responsável diferente do usuário autenticado
- **THEN** ele continua consultável em `Todos`, sem criar visão específica

#### Scenario: Status nulo ou inelegível
- **WHEN** um chamado possui status nulo ou qualquer status persistido
- **THEN** o Xano não infere nem altera o status e a fila não o exclui apenas
  por ser diferente de `Novo`

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
- **WHEN** um Técnico limpa filtros operacionais dentro de `Atribuídos a mim`
- **THEN** a consulta remove filtros, mantém o escopo atual até nova seleção e
  preserva sua ordenação

#### Scenario: Todos sem filtro
- **WHEN** um perfil autorizado consulta a fila sem filtros
- **THEN** o Xano retorna todos os chamados globais permitidos, inclusive
  atribuídos, não atribuídos, terminais e não terminais

#### Scenario: Consulta global por Diretoria ou Administrador
- **WHEN** usuário autenticado de Diretoria ou Administrador consulta a fila
- **THEN** o Xano retorna a mesma visão global permitida ao Técnico

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

#### Scenario: Perfil global sem escopo pessoal
- **WHEN** Diretoria ou Administrador carrega ou salva preferência da fila
- **THEN** a interface não exibe `Atribuídos a mim` e o Xano responde HTTP 403
  se receber o escopo enumerado `Atribuídos a mim`

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

## ADDED Requirements

### Requirement: Ordenação global é autorizada e estável no Xano
O Xano DEVE (MUST) ordenar a fila global antes de responder. Aceita somente
`numero`, `titulo`, `status`, `prioridade`, `totem`, `categoria`, `responsavel`, `criado_em` e
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
- **THEN** o Xano ordena alfabeticamente pelo nome do Técnico sem diferenciar
  caixa, mantém os chamados sem responsável após qualquer nome nas duas
  direções e desempata por `id` na direção solicitada

#### Scenario: Responsável persiste por escopo
- **WHEN** Técnico confirma o filtro ou a ordenação por Responsável em um escopo
- **THEN** a preferência daquele escopo preserva esses critérios sem alterar a
  preferência do outro escopo

#### Scenario: Coluna de atribuição não integra a fila global
- **WHEN** usuário consulta a tabela da fila global
- **THEN** a tabela não exibe a coluna `Atribuído em`, sem remover o dado dos
  detalhes, APIs ou histórico

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
- **WHEN** Gerente acessa a preferência global, ou Diretoria/Administrador usa
  `Atribuídos a mim`
- **THEN** o Xano responde HTTP 403 sem retornar ou alterar preferência

#### Scenario: Preferência inválida
- **WHEN** save informa filtro, Prioridade, Status, período, coluna ou direção inválidos
- **THEN** o Xano responde HTTP 422 sem alterar a última preferência válida
