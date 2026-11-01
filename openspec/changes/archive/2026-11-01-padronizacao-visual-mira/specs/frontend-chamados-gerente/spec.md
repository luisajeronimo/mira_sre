# Spec Delta

## ADDED Requirements

### Requirement: Jornada local apresenta filtros, tabela e detalhe compactos
A lista e o detalhe de chamados do Gerente DEVERÃO (MUST) usar filtros
rotulados, períodos `Abertura` e `Atualização` com `De`/`Até` alinhados, tabela
legível e grid compacto de dados. Cabeçalhos DEVEM (MUST) usar rose com texto
branco forte sem ocultar a ordenação ativa. As ações DEVEM (MUST) permanecer
alinhadas no topo do painel de filtros, e a borda arredondada da tabela NÃO
DEVE (MUST NOT) ser encoberta pelo conteúdo interno. O botão existente de criar
chamado DEVE (MUST) usar a ação primária, e `Chamado` DEVE (MUST) identificar a
coluna de título e ocorrência. As demais colunas DEVEM (MUST) ocupar larguras
equivalentes e ter conteúdo centralizado nos dois eixos. A mudança NÃO DEVE (MUST NOT) alterar escopo,
filtros, ordenação, drawer ou ações.

O hover dos cabeçalhos ordenáveis DEVE (MUST) ocupar toda a célula e mudar
somente o fundo rose, sem alteração de geometria. A tabela DEVE (MUST) caber na
área desktop sem barra horizontal e sem ocultar suas colunas.

#### Scenario: Gerente consulta a lista da Loja
- **WHEN** o Gerente abre sua lista de chamados
- **THEN** filtros e tabela existentes permanecem funcionais e são apresentados
  em cards consistentes, sem dados ou indicadores novos

#### Scenario: Gerente seleciona período em calendário
- **WHEN** o Gerente abre `Abertura` ou `Atualização` e escolhe um primeiro e
  um segundo dia
- **THEN** o calendário rose preenche visualmente os mesmos valores `De` e
  `Até` já usados pelo filtro, sem alterar persistência ou consulta

#### Scenario: Gerente consulta o detalhe
- **WHEN** o Gerente abre um chamado autorizado
- **THEN** status, origem, prioridade, categoria, Totem, Loja, responsável,
  datas e SLA aparecem como rótulos e valores compactos, e o drawer do Totem
  continua disponível

O detalhe DEVE (MUST) reunir os dados em uma única superfície branca com grid
limpo, labels fortes, status e prioridade discretamente destacados e descrição
em área própria; campos individuais NÃO DEVEM (MUST NOT) simular cards com
bordas rosas grandes.

O cabeçalho do detalhe DEVE (MUST) apresentar número e título com a mesma
tipografia no formato `Chamado #ID - título`, mantendo a ação do Totem maior e
com texto forte. O painel de dados DEVE (MUST) conter somente cabeçalho e grid;
descrição e comentário DEVEM (MUST) permanecer fora dele. A origem DEVE (MUST)
ser exibida em maiúsculas sem alterar o valor recebido.
A descrição DEVE (MUST) usar a mesma superfície branca do painel de dados.

#### Scenario: Cabeçalho e comentário recebem acabamento visual
- **WHEN** o Gerente consulta ou comenta um chamado autorizado
- **THEN** a faixa do detalhe mantém número, título e a ação existente do Totem,
  os campos usam labels fortes e borda rose sutil, e o campo e cards de
  comentários preservam conteúdo, postagem e visibilidade

### Requirement: Comentários públicos usam linha compacta e identificada
Cada comentário público visível ao Gerente DEVE (MUST) apresentar autor,
conteúdo, data e badge `PÚBLICO`, com data e identificação à direita. A
apresentação NÃO DEVE (MUST NOT) alterar visibilidade, postagem, ordem ou
conteúdo dos comentários.

#### Scenario: Comentário público existente
- **WHEN** o detalhe possui comentário público
- **THEN** mantém autor, conteúdo e data retornados, e apresenta `PÚBLICO` em
  badge discreto à direita

### Requirement: Abertura manual usa formulário visual estruturado
A página `/chamados/novo` DEVE (MUST) apresentar os cinco dados existentes em
uma superfície `Dados do chamado`, com título em largura total, Totem e
Categoria lado a lado, prioridades existentes em seleção horizontal e
descrição ampla. As ações existentes de voltar, limpar, descartar e enviar
DEVEM (MUST) permanecer disponíveis em hierarquia visual clara. A mudança NÃO
DEVE (MUST NOT) alterar campos, valores de prioridade, validações, regras de
SLA, eventos, payload, catálogos, autorização ou contratos.

#### Scenario: Gerente abre o formulário manual
- **WHEN** o Gerente autorizado acessa `/chamados/novo`
- **THEN** visualiza os cinco dados e as quatro ações existentes organizados
  conforme o padrão visual compartilhado, sem informação funcional adicional

#### Scenario: Gerente seleciona prioridade
- **WHEN** o Gerente escolhe uma das prioridades exibidas
- **THEN** a opção recebe estado visual selecionado e o mesmo handler atualiza
  o mesmo valor enviado pelo fluxo existente
