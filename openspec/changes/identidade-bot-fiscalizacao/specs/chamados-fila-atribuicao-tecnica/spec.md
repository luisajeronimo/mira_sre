## ADDED Requirements

### Requirement: Detalhe técnico distingue o criador de sistema
O detalhe global somente leitura de um chamado para Técnico DEVE (MUST) expor
`criador_sistema` separadamente de `origem`, `solicitante` e Técnico
responsável. Quando um chamado novo de heartbeat tiver
`criador_sistema = "bot_fiscalizacao"`, o contrato DEVE (MUST) preservar
origem automática, solicitante humano ausente e essa autoria de sistema. Esta
capacidade NÃO DEVE (MUST NOT) introduzir criador humano fictício, alterar as
visões da fila, incluir coluna de autoria na lista, mudar atribuição ou ampliar
tratativa.

#### Scenario: Técnico consulta chamado automático atual
- **WHEN** um Técnico autenticado consulta o detalhe de chamado criado pelo
  heartbeat após esta capacidade
- **THEN** o contrato retorna `origem = "automatico"`, `solicitante = null` e
  `criador_sistema = "bot_fiscalizacao"` como campos distintos

#### Scenario: Técnico consulta chamado manual
- **WHEN** um Técnico autenticado consulta o detalhe de chamado manual
- **THEN** o contrato preserva o solicitante humano existente e retorna
  `criador_sistema = null`

#### Scenario: Técnico consulta chamado legado
- **WHEN** um Técnico autenticado consulta um chamado sem autoria de sistema
  persistida
- **THEN** o contrato retorna `criador_sistema = null` sem fabricar autoria
  histórica

### Requirement: Detalhe técnico preserva segurança e credenciais apartadas
A autoria exposta no detalhe técnico DEVE (MUST) representar apenas o ator
lógico canônico do domínio e NÃO DEVE (MUST NOT) revelar, aceitar ou depender
de cabeçalho, segredo, chave de automação, token de usuário ou Environment
Variable. Autenticação humana, autorização exclusiva de Técnico e classificação
de erros do contrato permanecem as já consolidadas.

#### Scenario: Consumidor tenta informar autoria
- **WHEN** um consumidor tenta informar ou substituir autoria de sistema por
  payload, parâmetro ou credencial técnica em uma rota técnica de leitura
- **THEN** o contrato não usa esse valor como autoridade e não modifica o
  chamado

### Requirement: Detalhe técnico apresenta o Bot sem ampliar a fila
O Reflex DEVE (MUST) mostrar no detalhe técnico existente `Criado por: Bot de
Fiscalização` quando `criador_sistema` for `bot_fiscalizacao`, mantendo
`Origem: Automático` como informação distinta. Quando `criador_sistema` for
nulo, a interface NÃO DEVE (MUST NOT) inventar o Bot. A fila técnica e suas
colunas permanecem inalteradas.

#### Scenario: Detalhe técnico de incidente de heartbeat
- **WHEN** o detalhe técnico recebe um chamado automático atual com
  `criador_sistema = "bot_fiscalizacao"`
- **THEN** a interface apresenta o Bot como criador e a origem automática em
  campos separados, sem adicionar coluna à fila

#### Scenario: Detalhe técnico de registro sem autoria
- **WHEN** o detalhe técnico recebe `criador_sistema = null`
- **THEN** a interface não mostra o Bot como criador e continua apresentando os
  demais dados disponíveis sem inferência
