# Spec Delta

## ADDED Requirements

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
compactos. Data e visibilidade DEVEM (MUST) ficar à direita, sem alterar
comentário, evento, ordem cronológica ou controles de tratativa.

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
- **THEN** autor, conteúdo, data e visibilidade permanecem disponíveis na mesma
  ordem, com visibilidade em badge discreto à direita

#### Scenario: Tratativa e histórico mantêm acabamento compacto
- **WHEN** um perfil global visualiza o detalhe autorizado
- **THEN** número, título e ação existente do Totem compartilham o cabeçalho,
  campos e comentário usam borda rose sutil, e múltiplas alterações do mesmo
  evento são exibidas em grade de duas colunas sem alterar fatos, ordem ou acesso
