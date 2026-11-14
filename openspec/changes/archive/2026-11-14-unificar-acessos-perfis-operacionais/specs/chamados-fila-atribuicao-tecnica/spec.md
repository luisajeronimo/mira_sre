## ADDED Requirements

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

## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Fila técnica oferece somente as visões aprovadas
**Reason**: Substituído pela decisão humana de acessos operacionais equivalentes, que revoga as restrições de perfil anteriores.
**Migration**: Aplicar o requisito "Fila global oferece escopos comuns aos perfis operacionais" nesta mesma capacidade; contratos e dados históricos permanecem compatíveis.

### Requirement: Reflex oferece jornada técnica de consulta global
**Reason**: Substituído pela decisão humana de acessos operacionais equivalentes, que revoga as restrições de perfil anteriores.
**Migration**: Aplicar o requisito "Reflex oferece jornada operacional compartilhada" nesta mesma capacidade; contratos e dados históricos permanecem compatíveis.

### Requirement: Jornada global usa rotas canônicas de chamados
**Reason**: Substituído pela decisão humana de acessos operacionais equivalentes, que revoga as restrições de perfil anteriores.
**Migration**: Aplicar o requisito "Jornada operacional compartilhada usa rotas canônicas de chamados" nesta mesma capacidade; contratos e dados históricos permanecem compatíveis.
