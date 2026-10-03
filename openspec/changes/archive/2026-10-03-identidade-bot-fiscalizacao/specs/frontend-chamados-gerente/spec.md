## ADDED Requirements

### Requirement: Detalhe do Gerente apresenta criador de sistema sem ampliar a listagem
O Reflex DEVE (MUST) mostrar no detalhe existente do chamado para Gerente
`Criado por: Bot de Fiscalização` quando o contrato retornar
`criador_sistema = "bot_fiscalizacao"`, e manter a origem apresentada
separadamente como `Origem: Automático`. Quando a autoria de sistema for nula,
a interface NÃO DEVE (MUST NOT) inferir ou apresentar o Bot. Esta capacidade
NÃO DEVE (MUST NOT) criar uma coluna de autoria na listagem, redesenhar a tela
ou alterar a jornada de abertura manual.

#### Scenario: Detalhe de chamado automático atual da Loja
- **WHEN** um Gerente autorizado abre o detalhe de um chamado de heartbeat com
  `origem = "automatico"` e `criador_sistema = "bot_fiscalizacao"`
- **THEN** a interface mostra `Criado por: Bot de Fiscalização` e
  `Origem: Automático` como informações distintas

#### Scenario: Detalhe de chamado manual
- **WHEN** um Gerente autorizado abre o detalhe de chamado manual com
  `criador_sistema = null`
- **THEN** a interface mantém a apresentação do chamado manual e não exibe o
  Bot como criador

#### Scenario: Detalhe de chamado legado
- **WHEN** um Gerente autorizado abre o detalhe de chamado sem autoria de
  sistema persistida
- **THEN** a interface mantém o registro legível e não deduz autoria a partir
  da origem ou de outro dado histórico
