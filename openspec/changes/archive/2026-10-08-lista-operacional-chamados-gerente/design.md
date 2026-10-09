# Design

## Context

Ver `proposal.md` para a motivação e as delta specs para o contrato observável.
Hoje `GET /gerente/chamados` aplica corretamente o escopo por Loja, mas retorna
somente uma lista simples ordenada por identificador decrescente. O Reflex a
renderiza como cards e mantém os campos do formulário apenas no DOM. A change
anterior já disponibilizou `descricao` e `ultima_atualizacao_em` no modelo e no
detalhe; esta change não altera comentários nem o detalhe.
Por decisão humana posterior, chamado válido possui obrigatoriamente
`criado_em` e `ultima_atualizacao_em`; ambos nascem com o mesmo instante
funcional, sem compatibilidade operacional para timestamps nulos.

## Goals / Non-Goals

**Goals:**

- Evoluir o contrato existente de lista sem quebrar o escopo por Loja.
- Garantir que filtros, ordenação e total sejam calculados no Xano e possam
  receber paginação posteriormente sem mudar a forma de `items` e `total`.
- Separar no State os controles em edição daqueles efetivamente aplicados.
- Converter a lista em tabela acessível e aplicar `DESIGN.md` apenas aos
  componentes tocados.

**Non-Goals:**

- Não criar schema, tabela, relação, endpoint, paginação ou metadados de página.
- Não alterar regras de detalhe, comentários, status, atribuição, tratativa
  técnica ou regras de abertura autorizadas no backend. Os DTOs técnicos podem
  transportar os timestamps funcionais obrigatórios já persistidos para manter
  a representação tipada do chamado coerente, sem alterar a jornada Técnica.
- Não introduzir busca textual parcial, filtros temporais por atualização,
  dashboards, exportação ou refatoração visual global.

## Decisions

### 1. Um contrato estruturado de lista preserva evolução para paginação

`GET /gerente/chamados` continuará sendo o único endpoint de lista. Sua resposta
passará a ter a forma `{items, total}`: `items` é o recorte atual e `total` é a
quantidade após escopo e filtros. Nesta change o recorte contém todos os itens
retornados, portanto `items.length` é a quantidade exibida; a adição futura de
paginação poderá limitar `items` sem alterar o significado de `total`.

O endpoint aceitará somente entradas opcionais controladas: `numero`, `status`,
`ativo_id`, `data_inicio`, `data_fim`, `ordenar_por` e `direcao`. Não recebe
`lojas_id`, campo SQL, expressão ou metadados de página.

**Alternativas consideradas:**

- Filtrar e ordenar no Reflex: rejeitada porque deixa de representar o conjunto
  total e se torna incorreta quando houver paginação.
- Criar endpoint paralelo: rejeitada porque a consulta existente já possui
  autenticação e escopo adequados.

### 2. Whitelists explícitas protegem filtros e ordenação

O Xano validará status contra o vocabulário canônico, verificará que o Totem
informado pertence à Loja autenticada e aceitará somente campos/direções de
ordenação aprovados. A função usará ramos explícitos para cada ordenação, nunca
nome de coluna ou expressão fornecidos pelo cliente.

O default é `criado_em DESC, id DESC`. Título, Status, Prioridade, Totem e
Categoria usam texto alfabético case-insensitive; número e datas usam ordem
natural. Totem representa o nome textual retornado pelo contrato. Como ambos os timestamps funcionais são obrigatórios
para chamado válido, cada ramo temporal usa `db.query` direta com desempate por
`id`, sem partição ou merge para valores nulos.

A implementação deve confirmar pelo parser/MCP que `db.query` suporta a projeção
`to_lower` usada no sort textual. Se isso exigir campo
persistido, SQL arbitrário ou recurso fora do plano Free, o Apply para e pede
decisão humana em vez de alterar o modelo.

### 3. Período de abertura usa intervalo semiaberto no backend

A UI aceitará apenas datas de calendário de abertura. O State as converterá no
fuso operacional `America/Sao_Paulo` para início do dia e primeiro instante do
dia seguinte ao fim; o Xano aplicará `criado_em >= inicio` e `criado_em < fim
exclusivo`. Assim, as duas datas selecionadas são inclusivas para a pessoa
usuária, sem depender de `23:59:59.999` e sem tocar em `ultima_atualizacao_em`.

Início posterior ao fim é entrada inválida. Cada limite é opcional para permitir
intervalo aberto em um dos lados, mas o formato de data deve ser estrito.

### 4. State diferencia rascunho de consulta aplicada

`ChamadosGerenteState` manterá valores editáveis dos filtros, um snapshot dos
filtros aplicados, `ordenar_por`, `direcao`, `items`, `total`, loading e erro.
Aplicar copia os valores válidos para o snapshot e consulta; Limpar zera ambos e
consulta novamente mantendo a ordenação atual. A quantidade exibida é derivada
somente de `items`, sem segunda consulta ou carregamento auxiliar.

### 5. Sessão confirmada não é invalidada por consulta secundária

As ações de lista reutilizam a identidade já confirmada, sem repetir `/me` a
cada filtro ou ordenação. Erros de disponibilidade, timeout ou contrato da
consulta são mensagens sanitizadas de serviço e não limpam token, perfil ou
sessão confirmada. Apenas uma resposta de autenticação realmente inválida pode
limpar a sessão e redirecionar para login. O bloqueio de carregamento impede
uma consulta concorrente de sobrescrever um estado de lista mais atual.

### 6. Abertura preserva backend e torna o sucesso observável

Salvar preserva o POST funcional existente. Limpar e Descartar são eventos
locais: o primeiro reverte controles do formulário e o segundo reverte e navega
para a lista; Voltar apenas navega. O sucesso será apresentado como feedback
Reflex disparado antes da navegação ao detalhe, sem novo endpoint e sem depender
de mensagem que o carregamento de rota posterior limpe antes de ser percebida.

## Risks / Trade-offs

- **[Ordenação textual case-insensitive não suportada pelo sort do Xano]** →
  validar a projeção `to_lower` por parser/MCP e runtime antes do Apply; parar
  diante de necessidade de schema ou recurso não aprovado.
- **[Total e items aplicarem predicados diferentes]** → concentrar escopo e
  filtros validados na mesma função e cobrir combinações em testes.
- **[Conversão temporal deslocar dias]** → normalizar datas no fuso operacional
  e testar limites de início/fim de período.
- **[Registro histórico sem timestamp funcional]** → não fazer backfill nem
  fallback; apenas reportar sua existência antes de qualquer ação sobre dados.
- **[Input opcional materializado pelo runtime Xano]** → manter a correção de
  normalização como assunto separado desta simplificação temporal; não usar
  `0` para mascarar ausência de número ou Totem.
- **[Sucesso perdido no redirecionamento]** → usar feedback de navegação Reflex
  observável e cobrir a sequência de evento no State/UI.

## Migration Plan

1. Inventariar e validar o contrato de lista, filtros e capacidades de sort do
   Xano Free.
2. Evoluir a função/endpoint existente e seus testes sem modificar records.
3. Adaptar DTO, cliente, State e tabela Reflex; preservar rotas de abertura e
   detalhe.
4. Validar parser/MCP, suíte, compile Reflex, OpenSpec e dry-run antes de push
   autorizado.
5. Publicar somente após gate humano, validar runtime seguro e arquivar após
   reconciliação das evidências.
