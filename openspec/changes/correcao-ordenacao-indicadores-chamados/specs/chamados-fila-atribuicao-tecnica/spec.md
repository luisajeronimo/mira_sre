# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
