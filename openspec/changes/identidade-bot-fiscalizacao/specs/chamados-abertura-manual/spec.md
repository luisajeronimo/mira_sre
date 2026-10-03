## ADDED Requirements

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
