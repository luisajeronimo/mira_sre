# Dashboard de causas e recorrência

## Purpose

Permitir a Técnico, Diretoria e Administrador identificar concentração de Incidentes por Loja e Categoria e repetição de chamados por Totem, com filtros explícitos e resultados reproduzíveis sobre fatos persistidos.

## ADDED Requirements

### Requirement: Consulta de causas exige perfil operacional autenticado
Os contratos de dados e filtros DEVEM (MUST) exigir Técnico, Diretoria ou Administrador autenticado com troca de senha concluída, autorizando no Xano antes de ler dados. Gerente, perfis não oficiais e sessões inválidas NÃO DEVEM (MUST NOT) receber indicadores.

#### Scenario: Acesso permitido e negado
- **WHEN** Técnico, Diretoria ou Administrador consulta com sessão válida, ou Gerente, perfil não oficial ou sessão inválida tenta consultar
- **THEN** os três perfis operacionais recebem os mesmos indicadores; acessos indevidos são negados

### Requirement: Base comum utiliza Incidentes não cancelados
Os três indicadores DEVEM (MUST) usar chamados não cancelados com Categoria existente do tipo Incidente, Totem existente e `criado_em` válido. A Categoria vigente, inclusive inativa, DEVE (MUST) ser a causa. Exclusões por dados ausentes, Cancelados e Requisições DEVEM (MUST) ser informadas separadamente, sem estimar dados nem regravar histórico.

#### Scenario: Categoria e dados ausentes
- **WHEN** existem Incidentes de Categoria inativa, Requisições, Cancelados e registros sem Categoria ou Totem
- **THEN** a Categoria inativa participa; Requisições, Cancelados e inconsistências ficam fora da base, em contagens próprias

#### Scenario: Chamado sem data
- **WHEN** um registro não possui data de criação
- **THEN** ele não entra nos indicadores ou como predecessor; a quantidade sem data é identificada como não atribuível ao período, sem inventar timestamp

### Requirement: Período e filtros de causas são explícitos
Os painéis DEVEM (MUST) aceitar `[t0,t1)` em America/Sao_Paulo com comparação UTC, Loja histórica na abertura, Totem e Categoria, em seleção única opcional. O padrão DEVE (MUST) ser os últimos 30 dias civis até a consulta, com Hoje e personalizado. Hoje DEVE (MUST) ser o dia civil completo observado somente até a consulta. Entradas inválidas DEVEM (MUST) ser rejeitadas.

#### Scenario: Transferência e falta de vínculo
- **WHEN** o Totem foi transferido após abrir o chamado, ou não tem vínculo histórico comprovado
- **THEN** usa-se a Loja na abertura; sem vínculo, o chamado permanece globalmente em causas/recorrência, fora do ranking e dos recortes por Loja, com contagem explícita

#### Scenario: Filtros combinados e inválidos
- **WHEN** são aplicados Loja, Totem e Categoria válidos, ou período invertido/futuro e IDs inválidos
- **THEN** filtros válidos são combinados por E, podendo resultar em vazio; entradas inválidas são rejeitadas sem agregados

### Requirement: Ranking apresenta no máximo cinco Lojas
O Top 5 DEVE (MUST) contar Incidentes elegíveis criados no período por Loja histórica comprovada, ordenar por quantidade decrescente e ID crescente nos empates e retornar até cinco Lojas com quantidade e identificação. Sem Loja comprovada NÃO DEVE (MUST NOT) ser criado grupo fictício no ranking.

#### Scenario: Empate no limite
- **WHEN** seis Lojas têm o mesmo volume positivo
- **THEN** aparecem as cinco de menor ID, sem alterar a contagem total de Incidentes do recorte

### Requirement: Pareto apresenta concentração por Categoria
O Pareto DEVE (MUST) ordenar todas as Categorias com Incidentes elegíveis no período por volume decrescente e ID crescente, exibindo quantidade, participação e percentual acumulado. DEVE (MUST) destacar o menor prefixo cuja soma atinge pelo menos 80% da base, incluindo a Categoria que cruza o limiar, sem impor participação exata de 20% das Categorias.

#### Scenario: Limite exato e cruzamento
- **WHEN** os volumes são 6, 2, 1 e 1
- **THEN** as duas primeiras Categorias formam o grupo de 80%, com acumulados 60%, 80%, 90% e 100%

### Requirement: Recorrência mantém a janela consolidada
A recorrência DEVE (MUST) seguir `indicadores-operacionais`: mesmo Totem e Categoria, predecessor elegível estritamente anterior até 30 dias corridos inclusive, podendo anteceder t0 ou pertencer à Loja anterior. DEVE (MUST) retornar recorrentes, elegíveis, taxa e detalhamento por Loja e Totem; sem elegíveis, taxa indisponível; com elegíveis sem repetição, zero.

#### Scenario: Janela e instantes iguais
- **WHEN** predecessor está exatamente 30 dias antes, mais antigo que isso ou no mesmo instante
- **THEN** apenas o primeiro torna o chamado recorrente; instantes iguais não são predecessores entre si

#### Scenario: Predecessor fora do período e após transferência
- **WHEN** um Incidente no período tem predecessor válido antes de t0 e em outra Loja do mesmo Totem
- **THEN** ele é recorrente e pertence à Loja histórica de sua própria abertura

### Requirement: Interface distingue resultados e explica regras
A aba Causas e recorrência DEVE (MUST) apresentar os três painéis, filtros efetivos, regra de Categoria, janela de recorrência, bases e exclusões devolvidos pelo Xano. Carregamento, erro e vazio DEVEM (MUST) ser distinguíveis; falha após trocar filtros NÃO DEVE (MUST NOT) exibir resultados anteriores como atuais. O frontend NÃO DEVE (MUST NOT) agregar chamados brutos.

#### Scenario: Vazio e erro
- **WHEN** a consulta retorna base vazia ou falha após alterar o recorte
- **THEN** o vazio mostra listas vazias e taxa indisponível; a falha mostra erro sem resultados antigos
