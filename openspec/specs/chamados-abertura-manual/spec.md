## Purpose

Definir a fundação persistida e os contratos funcionais pelos quais o Gerente abre um chamado manual e acompanha todos os chamados vinculados aos ativos de sua Loja, preservando a compatibilidade do criador automático existente.

## Requirements

### Requirement: Novos chamados preservam origem, abertura e SLA aplicado
O sistema DEVE (MUST) persistir em cada chamado criado pelos fluxos funcionais novos a origem canônica, `criado_em` como único timestamp de negócio da abertura e `sla_horas_aplicado` como snapshot numérico do `sla_horas` vigente na categoria no instante da criação. `created_at` PODE (MAY) continuar existindo como metadado técnico, mas NÃO DEVE (MUST NOT) ser tratado como uma segunda referência funcional de abertura.

#### Scenario: Fundação preenchida em chamado manual
- **WHEN** o Xano cria um chamado por uma submissão manual válida
- **THEN** o registro recebe `origem = "manual"`, `criado_em` definido pelo backend no instante da criação e `sla_horas_aplicado` igual ao valor numérico vigente da categoria

#### Scenario: Fundação preenchida em chamado automático
- **WHEN** o heartbeat cria um novo chamado pela regra automática existente
- **THEN** o registro recebe `origem = "automatico"`, `criado_em` definido pelo backend no instante da criação e `sla_horas_aplicado` igual ao valor numérico vigente da categoria do heartbeat

#### Scenario: Valores de criação enviados pelo cliente
- **WHEN** um consumidor tenta informar ou substituir `origem`, `criado_em`, `created_at`, `sla_horas_aplicado`, `solicitante_id`, `tecnico_id`, `lojas_id` ou `status` na abertura manual
- **THEN** esses valores não são usados como autoridade para a criação e o Xano aplica exclusivamente os valores derivados pelo contrato funcional

### Requirement: Evolução do schema preserva dados legados sem inferência
O sistema DEVE (MUST) adicionar `descricao`, `origem` e `sla_horas_aplicado` de forma fisicamente compatível com chamados existentes e manter `criado_em` compatível com valores ausentes. Os valores novos DEVEM (MUST) ser obrigatórios nos fluxos definidos por esta capacidade, mas registros anteriores NÃO DEVEM (MUST NOT) receber origem, descrição, timestamp de negócio ou SLA histórico inferidos de categoria, título, usuário, `created_at` ou qualquer outra heurística.

#### Scenario: Chamado legado sem os novos dados
- **WHEN** a evolução do schema encontra um chamado existente sem origem, descrição, `criado_em` ou snapshot de SLA
- **THEN** o registro permanece armazenado com esses valores ausentes e nenhum dado histórico é fabricado

#### Scenario: Consulta de chamado legado atribuível a uma Loja
- **WHEN** um chamado legado possui relação válida com um ativo da Loja do Gerente, mas algum dado novo está ausente
- **THEN** o contrato de consulta pode retorná-lo com o valor correspondente nulo, sem substituí-lo por uma inferência

#### Scenario: Chamado legado sem ativo válido
- **WHEN** um chamado legado não possui relação válida com um ativo e, por isso, não pode ser atribuído com segurança à Loja do Gerente
- **THEN** ele não é exposto nos contratos da Loja e permanece armazenado para tratamento posterior explícito

### Requirement: Categorias declaram permissão de abertura manual
O sistema DEVE (MUST) persistir em cada categoria a propriedade booleana `permite_abertura_manual`. Somente categorias com valor explícito `true` e com `sla_horas` numérico válido PODEM (MAY) ser usadas pelo contrato de abertura manual; categorias legadas sem classificação explícita DEVEM (MUST) permanecer indisponíveis para essa abertura, e a categoria usada pelo heartbeat DEVE (MUST) possuir valor `false`. A classificação das categorias existentes DEVE (MUST) ocorrer por identificador mediante decisão humana explícita, sem seleção automática por nome, descrição, tipo ou qualquer outra inferência.

#### Scenario: Categoria permitida
- **WHEN** uma categoria possui `permite_abertura_manual = true` e um `sla_horas` numérico válido
- **THEN** ela é disponibilizada ao Gerente e pode classificar um novo chamado manual

#### Scenario: Categoria não permitida
- **WHEN** uma categoria possui `permite_abertura_manual = false`
- **THEN** ela não é retornada no catálogo de abertura manual e é rejeitada se seu identificador for enviado diretamente

#### Scenario: Categoria legada sem classificação
- **WHEN** a migração encontra uma categoria existente sem decisão explícita sobre abertura manual
- **THEN** a categoria permanece com `permite_abertura_manual = false` e não é classificada por nome, descrição ou tipo ITIL

#### Scenario: Gate humano de classificação das categorias existentes
- **WHEN** o inventário das categorias existentes apresenta identificador, nome, tipo atual, SLA atual, vínculo com o heartbeat e valor atual ou proposto de `permite_abertura_manual`
- **THEN** a implementação aguarda decisão humana explícita sobre os identificadores que receberão `true` e não altera os dados remotos antes dessa aprovação

#### Scenario: Categoria do heartbeat
- **WHEN** a categoria já utilizada pela criação automática é preparada para o schema evoluído
- **THEN** ela recebe explicitamente `permite_abertura_manual = false` sem alterar a forma como o heartbeat a localiza

### Requirement: SLA da categoria possui representação numérica segura
O sistema DEVE (MUST) representar `categorias_servico.sla_horas` e `chamados.sla_horas_aplicado` em formato numérico compatível entre si. Antes da mudança de tipo, a implementação DEVE (MUST) identificar e verificar todos os consumidores existentes de `categorias_servico.sla_horas`, incluindo XanoScript, Python e demais contratos locais relevantes, e definir a adaptação ou a evidência de compatibilidade de cada consumidor. A migração somente DEVE (MUST) converter valores textuais existentes cuja equivalência numérica seja inequívoca e DEVE (MUST) interromper a ativação dos novos contratos diante de consumidor incompatível ou de valor vazio, não numérico ou ambíguo em categoria que precise participar de um novo fluxo.

#### Scenario: Consumidores do SLA auditados antes da mudança de tipo
- **WHEN** a implementação prepara a alteração de `categorias_servico.sla_horas` de texto para decimal
- **THEN** todos os usos existentes em XanoScript, Python e contratos locais relevantes estão inventariados, classificados quanto à compatibilidade e cobertos por adaptação ou verificação antes de a alteração ser aplicada

#### Scenario: Consumidor incompatível identificado
- **WHEN** a auditoria encontra um consumidor que depende da representação textual e ainda não possui adaptação validada
- **THEN** a mudança de tipo permanece bloqueada sem alterar dados ou contratos remotos

#### Scenario: Valor textual inequivocamente numérico
- **WHEN** uma categoria existente possui `sla_horas` textual cuja conversão preserva exatamente seu valor numérico
- **THEN** a migração converte o valor para a representação numérica aprovada sem atribuir outro SLA

#### Scenario: Valor incompatível
- **WHEN** a auditoria encontra `sla_horas` vazio, não numérico ou ambíguo em uma categoria que será usada na abertura manual ou pelo heartbeat
- **THEN** a migração ou ativação é interrompida para correção explícita, sem escolher um SLA padrão

#### Scenario: Alteração posterior da categoria
- **WHEN** o `sla_horas` de uma categoria é alterado depois da criação de um chamado
- **THEN** o `sla_horas_aplicado` já persistido no chamado permanece inalterado

### Requirement: Grupo funcional fornece catálogo de ativos da Loja
O sistema DEVE (MUST) fornecer no grupo `mira-service-desk` uma consulta autenticada de ativos para o Gerente que retorne somente os ativos cuja `lojas_id` corresponda à Loja derivada da identidade autenticada. A resposta DEVE (MUST) conter uma coleção de itens com `id`, `nome_ativo`, `tipo` e `status_atual`.

#### Scenario: Gerente consulta ativos permitidos
- **WHEN** um Gerente autenticado e associado a uma Loja consulta `GET /gerente/ativos`
- **THEN** o Xano retorna `items` contendo somente os ativos dessa Loja e os campos públicos previstos pelo contrato

#### Scenario: Gerente sem Loja
- **WHEN** um Gerente autenticado sem associação válida de Loja consulta o catálogo de ativos
- **THEN** o Xano rejeita a operação como não autorizada sem retornar ativos

#### Scenario: Outro perfil consulta o catálogo do Gerente
- **WHEN** um Técnico ou usuário da Diretoria consulta `GET /gerente/ativos`
- **THEN** o Xano rejeita a operação como não autorizada

### Requirement: Grupo funcional fornece categorias de abertura manual
O sistema DEVE (MUST) fornecer no grupo `mira-service-desk` uma consulta autenticada para o Gerente que filtre categorias exclusivamente por `permite_abertura_manual = true`. A resposta DEVE (MUST) conter `items` com `id`, `nome`, `tipo_itil`, `descricao` e `sla_horas`, sem usar nome, descrição ou tipo ITIL como critério implícito de permissão.

#### Scenario: Consulta de categorias manuais
- **WHEN** um Gerente autenticado consulta `GET /gerente/categorias`
- **THEN** o Xano retorna somente categorias explicitamente permitidas para abertura manual

#### Scenario: Categoria automática não é oferecida
- **WHEN** a categoria do heartbeat possui `permite_abertura_manual = false`
- **THEN** ela não aparece na resposta do catálogo manual

### Requirement: Gerente pode abrir chamado manual da própria Loja
O sistema DEVE (MUST) aceitar em `POST /gerente/chamados` somente `ativos_referencia_id`, `categorias_servico_id`, `prioridade`, `titulo` e `descricao` como dados funcionais fornecidos pelo Gerente. Todos os cinco valores DEVEM (MUST) estar presentes; `titulo` e `descricao` DEVEM (MUST) ser rejeitados quando ausentes, vazios ou compostos somente por espaços após remoção de espaços nas extremidades. Esta capacidade NÃO DEVE (MUST NOT) introduzir limite mínimo ou máximo de caracteres para esses campos.

#### Scenario: Abertura manual válida
- **WHEN** um Gerente autenticado envia ativo de sua Loja, categoria permitida, uma prioridade oficial, título e descrição válidos
- **THEN** o Xano cria um novo chamado com `status = "Novo"`, `origem = "manual"`, solicitante igual ao usuário autenticado e os dados de abertura e SLA definidos pelo backend

#### Scenario: Prioridade oficial
- **WHEN** o Gerente informa `Baixa`, `Média`, `Alta` ou `Urgente`
- **THEN** o Xano preserva exatamente o valor escolhido no novo chamado sem derivá-lo da categoria ou de outra matriz

#### Scenario: Prioridade fora do vocabulário
- **WHEN** o Gerente informa uma prioridade diferente de `Baixa`, `Média`, `Alta` ou `Urgente`
- **THEN** o Xano rejeita a submissão como contrato inválido sem criar chamado

#### Scenario: Campo obrigatório ausente, vazio ou composto somente por espaços
- **WHEN** ativo, categoria, prioridade, título ou descrição está ausente, ou `titulo` ou `descricao` está vazio ou fica vazio após remoção de espaços nas extremidades
- **THEN** o Xano rejeita a submissão como contrato inválido sem criar chamado

#### Scenario: Ativo de outra Loja
- **WHEN** um Gerente autenticado informa um ativo pertencente a outra Loja
- **THEN** o Xano rejeita a operação como não autorizada sem criar chamado e sem usar uma Loja informada pelo cliente

#### Scenario: Categoria inexistente ou não permitida
- **WHEN** o Gerente informa uma categoria inexistente ou com `permite_abertura_manual` diferente de `true`
- **THEN** o Xano rejeita a submissão sem criar chamado

#### Scenario: Submissões manuais repetidas
- **WHEN** duas submissões manuais válidas são processadas separadamente, ainda que tenham os mesmos dados
- **THEN** o Xano cria um novo chamado para cada submissão e não aplica a deduplicação do heartbeat

### Requirement: Resposta da abertura contém o chamado criado
O sistema DEVE (MUST) responder à criação válida com status HTTP de criação e um objeto `chamado` contendo `id`, `titulo`, `descricao`, `status`, `prioridade`, `origem`, `criado_em`, `sla_horas_aplicado`, ativo, categoria, solicitante e técnico responsável quando existir. A resposta NÃO DEVE (MUST NOT) expor credenciais, campos internos de autenticação nem tratar `created_at` como data funcional.

#### Scenario: Resposta de criação
- **WHEN** o chamado manual é persistido com sucesso
- **THEN** o Xano retorna HTTP 201 e o objeto funcional do chamado criado com `tecnico` nulo enquanto não houver atribuição

### Requirement: Criação de chamado inicializa a última atualização observável
Todo chamado criado pelos fluxos manual e automático DEVE (MUST) persistir `ultima_atualizacao_em` com o mesmo valor funcional de `criado_em`. O valor NÃO DEVE (MUST NOT) ser recebido de consumidores nem substituído por `created_at` técnico.

#### Scenario: Abertura manual inicializa a data
- **WHEN** um Gerente abre chamado manual válido
- **THEN** o registro persiste `criado_em` e `ultima_atualizacao_em` com o mesmo instante definido pelo Xano

#### Scenario: Resposta da abertura preserva a data funcional
- **WHEN** a abertura manual é concluída com sucesso
- **THEN** o DTO funcional retorna `ultima_atualizacao_em` igual a `criado_em`, sem expor `created_at`

### Requirement: Gerente acompanha todos os chamados da própria Loja
O sistema DEVE (MUST) fornecer `GET /gerente/chamados` e `GET /gerente/chamados/{chamados_id}` no grupo `mira-service-desk`. A lista DEVE (MUST) retornar `items` com resumo funcional e o detalhe DEVE (MUST) retornar um objeto `chamado` com os campos do contrato de criação; ambos DEVEM (MUST) determinar pertencimento à Loja pela relação persistida entre chamado, ativo e Loja, independentemente do solicitante e da origem.

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
- **WHEN** o Gerente consulta um identificador de chamado que não existe
- **THEN** o Xano responde como recurso não encontrado

### Requirement: Contratos funcionais preservam autenticação e negação por padrão
Todas as operações de `mira-service-desk` DEVEM (MUST) exigir autenticação da tabela `usuarios`, autorizar somente o perfil Gerente nesta capacidade e aplicar o escopo persistido de Loja no Xano. Os contratos funcionais NÃO DEVEM (MUST NOT) reabrir os endpoints genéricos de POST, PATCH ou DELETE nem atribuir autorização ao Reflex.

#### Scenario: Token ausente ou inválido
- **WHEN** uma operação funcional recebe uma requisição sem token válido
- **THEN** o Xano responde como não autenticado sem consultar ou modificar dados protegidos

#### Scenario: Perfil autenticado sem permissão
- **WHEN** um Técnico ou usuário da Diretoria chama uma operação funcional reservada ao Gerente
- **THEN** o Xano responde como não autorizado sem executar a operação

#### Scenario: Mutação genérica direta
- **WHEN** um usuário tenta usar os CRUDs genéricos existentes para criar, editar ou excluir chamado
- **THEN** a negação consolidada permanece aplicada e nenhum registro é modificado

### Requirement: Erros funcionais possuem classificação estável
Os contratos de `mira-service-desk` DEVEM (MUST) distinguir autenticação ausente ou inválida, falta de autorização, recurso inexistente, entrada incompatível com o contrato e indisponibilidade do serviço, sem retornar dados protegidos ou executar mutação parcial.

#### Scenario: Classificação dos erros HTTP
- **WHEN** uma chamada funcional falha
- **THEN** o contrato usa 401 para sessão não autenticada, 403 para perfil ou escopo não autorizado, 404 para recurso inexistente, 422 para entrada inválida e resposta 5xx para falha interna ou indisponibilidade do backend

### Requirement: Compatibilidade automática é limitada aos novos dados compartilhados
O criador automático de heartbeat DEVE (MUST) criar incidente somente em uma transição elegível Online → Offline, com título, status `Novo`, prioridade `Urgente`, categoria, ativo, origem `automatico`, solicitante humano ausente, `criador_sistema = "bot_fiscalizacao"`, `criado_em` definido pelo backend e snapshot de SLA. A consulta de incidente equivalente DEVE (MUST) usar ativo, categoria e os status vigentes não terminais. Se encontrar equivalente, NÃO DEVE (MUST NOT) criar chamado nem alterar origem, autoria, status, SLA, solicitante ou qualquer dado do registro existente.

#### Scenario: Heartbeat cria incidente compatível
- **WHEN** uma transição elegível do heartbeat não encontra incidente equivalente não terminal
- **THEN** o Xano cria o registro com os dados compartilhados aprovados e sem solicitante humano

#### Scenario: Heartbeat encontra incidente equivalente
- **WHEN** uma transição elegível encontra incidente equivalente não terminal
- **THEN** nenhum novo chamado é criado e nenhum registro existente recebe alteração de origem, autoria, status, SLA ou solicitante

### Requirement: Chamado distingue origem de criador de sistema
O sistema DEVE (MUST) persistir no chamado um `criador_sistema` opcional,
independente de `origem` e de `solicitante_id`. Nesta capacidade, o único valor
canônico permitido para esse campo é `bot_fiscalizacao`, que identifica o Bot de
Fiscalização como ator de sistema não autenticável. `criador_sistema` NÃO DEVE
(MUST NOT) ser uma relação com `usuarios`, criar uma conta ou perfil humano,
conceder login, senha, sessão, token ou permissão, nem armazenar ou derivar
identidade de segredo, header, chave de automação ou Environment Variable.

#### Scenario: Chamado manual não recebe criador de sistema
- **WHEN** um usuário autorizado cria um chamado manual válido
- **THEN** o chamado preserva `origem = "manual"`, seu solicitante humano
  derivado pelo contrato existente e `criador_sistema = null`

#### Scenario: Heartbeat persiste autoria do Bot
- **WHEN** o Xano cria um novo chamado porque a regra de heartbeat determinou
  um incidente elegível
- **THEN** o chamado recebe `origem = "automatico"`, `solicitante_id` ausente
  e `criador_sistema = "bot_fiscalizacao"`, sem criar ou associar uma identidade
  autenticável ao Bot

#### Scenario: Credencial técnica não é autoria de domínio
- **WHEN** o Fiscal dispara a verificação autenticada por sua credencial técnica
- **THEN** a credencial somente autentica o processo no endpoint e não é
  persistida, exposta nem usada como valor de `criador_sistema`

### Requirement: Autoria de sistema preserva compatibilidade histórica
O sistema DEVE (MUST) adicionar `criador_sistema` de forma compatível com
chamados existentes. Registros anteriores sem esse campo DEVEM (MUST) continuar
legíveis com `criador_sistema = null`; a implementação NÃO DEVE (MUST NOT)
executar backfill nem inferir o Bot a partir de `origem`, título, categoria,
ativo, telemetria, usuário, timestamp ou qualquer outra heurística.

#### Scenario: Chamado legado sem autoria
- **WHEN** um chamado criado antes desta capacidade não possui
  `criador_sistema`
- **THEN** a leitura retorna autoria de sistema ausente e não identifica o Bot
  por inferência

#### Scenario: Chamado automático legado
- **WHEN** um chamado histórico possui `origem = "automatico"`, mas não possui
  `criador_sistema`
- **THEN** ele continua com autoria de sistema ausente e não é apresentado como
  criado pelo Bot de Fiscalização

### Requirement: Heartbeat acrescenta somente a autoria aprovada
O criador automático de heartbeat DEVE (MUST) preencher
`criador_sistema = "bot_fiscalizacao"` somente no novo registro que sua regra
atual decidir criar. Esta capacidade NÃO DEVE (MUST NOT) alterar o limite de
heartbeat, a consulta de telemetria, a decisão de disponibilidade, o papel do
Fiscal, o título, status, prioridade, categoria, ativo, SLA, conjunto de status
abertos, deduplicação, concorrência, retorno de telemetria ou encerramento
automático.

#### Scenario: Incidente equivalente continua sem nova autoria
- **WHEN** a verificação de heartbeat encontra incidente equivalente pela regra
  atual
- **THEN** nenhum novo chamado é criado e nenhum registro existente recebe ou
  tem alterado `criador_sistema`

### Requirement: Detalhe da Loja informa autoria de sistema separadamente
O detalhe de chamado consultado pelo Gerente DEVE (MUST) expor
`criador_sistema` além de `origem` e de `solicitante`, preservando suas
semânticas distintas. Para um chamado de heartbeat novo, o contrato DEVE (MUST)
permitir observar `origem = "automatico"`, solicitante humano ausente e
`criador_sistema = "bot_fiscalizacao"`. A visibilidade por Loja, autenticação e
autorização existentes NÃO DEVEM (MUST NOT) ser alteradas por essa autoria.

#### Scenario: Consulta autorizada de chamado automático atual
- **WHEN** um Gerente autorizado consulta o detalhe de um chamado automático
  criado pelo heartbeat após esta capacidade
- **THEN** o contrato retorna separadamente a origem automática, solicitante
  nulo e o criador de sistema `bot_fiscalizacao`

#### Scenario: Consulta de legado pela Loja
- **WHEN** um Gerente autorizado consulta um chamado legado sem autoria de
  sistema
- **THEN** o contrato mantém o chamado legível e retorna `criador_sistema` nulo
  sem alterar sua autorização por Loja
