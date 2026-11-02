# Spec Delta

## ADDED Requirements

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
Aplicar ou limpar DEVE (MUST) substituir integralmente as coleções confirmadas na preferência do usuário e escopo atuais. `Todos` e `Atribuídos a mim` permanecem isolados; Diretoria e Administrador continuam sem escopo pessoal. Preferência anterior com valor escalar DEVE (MUST) ser restaurada como coleção unitária, sem exigir backfill.

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

## MODIFIED Requirements

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
