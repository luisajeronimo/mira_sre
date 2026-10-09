# Spec Delta

## MODIFIED Requirements

### Requirement: Novos chamados preservam origem, abertura e SLA aplicado
O sistema DEVE (MUST) persistir em cada chamado válido criado pelos fluxos manual e automático a origem canônica, `criado_em` como timestamp funcional imutável de abertura, `ultima_atualizacao_em` inicialmente igual a `criado_em` e `sla_horas_aplicado` como snapshot numérico do `sla_horas` vigente na categoria no instante da criação. Os dois timestamps DEVEM (MUST) usar o mesmo instante funcional definido uma única vez pelo backend. `created_at` PODE (MAY) continuar existindo como metadado técnico, mas NÃO DEVE (MUST NOT) ser tratado como uma segunda referência funcional de abertura.

#### Scenario: Abertura manual inicializa os dois timestamps
- **WHEN** o Xano cria um chamado manual válido
- **THEN** o registro recebe `criado_em` e `ultima_atualizacao_em` com o mesmo instante funcional do backend

#### Scenario: Fundação preenchida em chamado manual
- **WHEN** o Xano cria um chamado por uma submissão manual válida
- **THEN** o registro recebe `origem = "manual"`, os dois timestamps funcionais com o mesmo instante do backend e `sla_horas_aplicado` igual ao valor numérico vigente da categoria

#### Scenario: Incidente automático inicializa os dois timestamps
- **WHEN** o heartbeat cria um incidente automático elegível
- **THEN** o registro recebe `criado_em` e `ultima_atualizacao_em` com o mesmo instante funcional do backend

#### Scenario: Fundação preenchida em chamado automático
- **WHEN** o heartbeat cria um novo chamado pela regra automática existente
- **THEN** o registro recebe `origem = "automatico"`, os dois timestamps funcionais com o mesmo instante do backend e `sla_horas_aplicado` igual ao valor numérico vigente da categoria do heartbeat

#### Scenario: Abertura posterior não altera a data inicial
- **WHEN** um evento observável posterior ocorre no chamado
- **THEN** `criado_em` permanece imutável e somente `ultima_atualizacao_em` pode ser atualizada conforme o contrato aplicável

#### Scenario: Valores de criação enviados pelo cliente
- **WHEN** um consumidor tenta informar ou substituir `origem`, `criado_em`, `ultima_atualizacao_em`, `created_at`, `sla_horas_aplicado`, `solicitante_id`, `tecnico_id`, `lojas_id` ou `status` na abertura manual
- **THEN** esses valores não são usados como autoridade e o Xano aplica exclusivamente os valores derivados pelo contrato funcional

### Requirement: Evolução do schema preserva dados legados sem inferência
O sistema NÃO DEVE (MUST NOT) fazer backfill ou inferir `criado_em` ou `ultima_atualizacao_em` a partir de `created_at`, atribuição, interação ou qualquer timestamp aproximado. Registros históricos que ainda tenham esses campos ausentes não são compatíveis com a consulta operacional desta change; a existência deles DEVE (MUST) ser apenas reportada antes de qualquer ação sobre dados.

#### Scenario: Registro histórico sem timestamp funcional
- **WHEN** há registro existente com `criado_em` ou `ultima_atualizacao_em` ausente
- **THEN** o sistema não o preenche nem inventa data, e a change não oferece fallback de leitura

#### Scenario: Chamado legado sem os novos dados
- **WHEN** a evolução encontra chamado existente sem origem, descrição, timestamp funcional ou snapshot de SLA
- **THEN** o registro permanece armazenado com esses valores ausentes e nenhum dado histórico é fabricado

#### Scenario: Consulta de chamado legado atribuível a uma Loja
- **WHEN** um chamado legado possui ativo da Loja do Gerente, mas algum timestamp funcional está ausente
- **THEN** a consulta operacional desta change não inventa valor nem oferece compatibilidade temporal para ele

#### Scenario: Chamado legado sem ativo válido
- **WHEN** um chamado legado não possui relação válida com um ativo e, por isso, não pode ser atribuído com segurança à Loja do Gerente
- **THEN** ele não é exposto nos contratos da Loja e permanece armazenado para tratamento posterior explícito

### Requirement: Gerente acompanha todos os chamados da própria Loja
O sistema DEVE (MUST) fornecer `GET /gerente/chamados` e `GET /gerente/chamados/{chamados_id}` no grupo `mira-service-desk`. A lista DEVE (MUST) retornar `items` com resumo funcional e `total` correspondente à consulta atual; o detalhe DEVE (MUST) retornar um objeto `chamado` com os campos do contrato de criação. Ambos DEVEM (MUST) determinar pertencimento à Loja pela relação persistida entre chamado, ativo e Loja, independentemente do solicitante e da origem.

#### Scenario: Lista da Loja
- **WHEN** um Gerente autenticado consulta a lista de chamados
- **THEN** o Xano retorna todos os chamados associados a ativos de sua Loja, incluindo chamados de outros solicitantes e chamados automáticos, sem retornar chamados de outras Lojas

#### Scenario: Detalhe da própria Loja
- **WHEN** um Gerente consulta o identificador de um chamado relacionado a um ativo de sua Loja
- **THEN** o Xano retorna o detalhe funcional do chamado

#### Scenario: Detalhe de outra Loja
- **WHEN** um Gerente consulta o identificador de um chamado relacionado a um ativo de outra Loja
- **THEN** o Xano rejeita a operação como não autorizada sem retornar os dados do chamado

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta um identificador de chamado que não existe
- **THEN** o Xano responde como recurso não encontrado

## ADDED Requirements

### Requirement: Lista operacional da Loja possui consulta controlada
`GET /gerente/chamados` DEVE (MUST) retornar em cada item `id`, `titulo`, `descricao`, `status`, `prioridade`, Totem, Categoria, `criado_em` e `ultima_atualizacao_em`, além de `total` filtrado. O contrato NÃO DEVE (MUST NOT) aceitar Loja do cliente, metadados de paginação ou campo de consulta arbitrário.

#### Scenario: Resumo operacional completo
- **WHEN** a consulta autorizada encontra chamados no escopo da Loja
- **THEN** cada item contém os dados funcionais necessários à lista e `total` representa a quantidade de chamados que atendem à mesma consulta

#### Scenario: Resumo com datas funcionais obrigatórias
- **WHEN** a consulta autorizada encontra chamado válido
- **THEN** `criado_em` e `ultima_atualizacao_em` são timestamps funcionais definidos, sem fallback para `created_at`

### Requirement: Filtros da lista são restritos ao escopo da Loja
A lista DEVE (MUST) aceitar somente filtros opcionais de número exato, status canônico, Totem pertencente à Loja autorizada e intervalo inclusivo de `criado_em`. Critério inválido, status não canônico ou Totem fora do escopo DEVE (MUST) resultar em erro funcional sem ampliar a consulta.

#### Scenario: Combinação de filtros
- **WHEN** o Gerente aplica mais de um filtro válido
- **THEN** o Xano retorna somente chamados da própria Loja que atendem simultaneamente aos critérios e informa o total filtrado

#### Scenario: Período inclusivo de abertura
- **WHEN** o Gerente informa início e fim válidos do período
- **THEN** a consulta inclui chamados abertos nos dois dias-limite e não filtra por `ultima_atualizacao_em`

#### Scenario: Totem de outra Loja
- **WHEN** o Gerente informa identificador de Totem que não pertence à sua Loja
- **THEN** o Xano rejeita a consulta como não autorizada sem retornar chamados

### Requirement: Ordenação da lista é autorizada, determinística e server-side
A lista DEVE (MUST) ordenar no Xano somente por número, título, status, prioridade, Totem, Categoria, abertura ou última atualização, em `ASC` ou `DESC`. Sem seleção explícita, a ordem DEVE (MUST) ser `criado_em DESC, id DESC`; filtros não a alteram. Número usa ordem numérica; Título, Status, Prioridade, Totem textual e Categoria usam ordem alfabética case-insensitive; datas usam ordem cronológica. Chamados válidos possuem ambas as datas funcionais, portanto a ordenação temporal é direta e cronológica.

#### Scenario: Ordem padrão
- **WHEN** o Gerente não informa critério de ordenação
- **THEN** o Xano retorna chamados por `criado_em DESC` e `id DESC` como desempate

#### Scenario: Ordenação textual case-insensitive de prioridade
- **WHEN** o Gerente ordena por prioridade
- **THEN** a ordem ascendente é Alta, Baixa, Média, Urgente e a descendente é sua inversão, sem diferenças de maiúsculas/minúsculas, com desempate determinístico por identificador

#### Scenario: Ordenação cronológica de datas funcionais
- **WHEN** a ordenação selecionada é `criado_em` ou `ultima_atualizacao_em` em qualquer direção
- **THEN** o Xano aplica ordem cronológica na direção solicitada e desempate determinístico por identificador

#### Scenario: Ordenação inválida
- **WHEN** o cliente informa campo ou direção fora da whitelist
- **THEN** o Xano rejeita a entrada sem executar ordenação arbitrária
