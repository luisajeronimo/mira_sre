# Spec Delta

## ADDED Requirements

### Requirement: Detalhe apresenta histórico público de status
O Reflex DEVE (MUST) consultar o contrato de histórico público de status do Gerente e apresentá-lo em seção própria, distinta dos comentários, com status anterior, status resultante, data e autor, na ordem retornada pelo backend. O autor DEVE (MUST) ser apresentado como nome e perfil retornados, somente pelo nome quando `perfil` for nulo, como `Sistema` quando o backend assim o identificar, ou como autor não informado quando `autor` for nulo, sem inferir autoria ou perfil. A interface NÃO DEVE (MUST NOT) consumir a timeline técnica nem combinar comentários e transições em uma coleção derivada no cliente. A falha do histórico NÃO DEVE (MUST NOT) impedir a apresentação do detalhe nem dos comentários.

#### Scenario: Histórico carregado
- **WHEN** o contrato retorna transições
- **THEN** o Reflex apresenta a seção de histórico separada dos comentários

#### Scenario: Autor sem perfil reconhecido
- **WHEN** a transição retorna `autor` com nome e `perfil` nulo
- **THEN** o Reflex apresenta somente o nome, sem rotular como `Sistema`

#### Scenario: Histórico vazio
- **WHEN** o contrato retorna lista vazia
- **THEN** o Reflex informa que não há transições registradas e que transições anteriores à implantação do Save operacional não são exibidas

#### Scenario: Falha do histórico
- **WHEN** a consulta do histórico falha por motivo diferente de autenticação
- **THEN** o Reflex apresenta erro sanitizado na seção e mantém detalhe e comentários

#### Scenario: Histórico no detalhe do Gerente
- **WHEN** o Gerente abre chamado autorizado da própria Loja
- **THEN** o Reflex apresenta o histórico pelo contrato de histórico do Gerente, sem ações adicionais

### Requirement: Publicação de comentário confirma gravação independentemente da atualização do detalhe
Após o contrato de criação confirmar a persistência de comentário público, o Reflex DEVE (MUST) apresentar confirmação visual explícita, preservar na lista o DTO retornado pelo Xano e limpar o rascunho. Uma falha posterior ao consultar novamente o detalhe NÃO DEVE (MUST NOT) ser apresentada como falha da publicação já confirmada; o resultado da atualização do detalhe DEVE (MUST) ser comunicado separadamente.

#### Scenario: Publicação confirmada
- **WHEN** a criação do comentário público retorna sucesso confirmado pelo Xano
- **THEN** o Reflex apresenta confirmação visual, inclui o comentário retornado pelo servidor e limpa o rascunho

#### Scenario: Publicação não confirmada
- **WHEN** a criação do comentário público falha ou não retorna confirmação válida
- **THEN** o Reflex não apresenta sucesso nem descarta o rascunho e apresenta erro sanitizado da publicação

#### Scenario: Falha ao atualizar detalhe após publicação confirmada
- **WHEN** a publicação foi confirmada e a consulta posterior do detalhe falha
- **THEN** o Reflex mantém o comentário retornado e a confirmação de publicação e informa separadamente que o detalhe não foi atualizado

## MODIFIED Requirements

### Requirement: Reflex permite comentar chamado autorizado com rascunho descartável
O Reflex DEVE (MUST) oferecer ao Gerente autenticado envio de comentário para o contrato funcional específico e descarte exclusivamente local do rascunho, em chamado autorizado da própria Loja em qualquer status, inclusive `Encerrado` e `Cancelado`. A interface NÃO DEVE (MUST NOT) enviar autor, Loja, visibilidade, timestamp ou status como dados sob controle do cliente.

#### Scenario: Envio de comentário público
- **WHEN** o Gerente envia conteúdo de comentário não vazio em chamado autorizado da própria Loja
- **THEN** o Reflex chama o contrato específico, apresenta o comentário retornado e atualiza a visualização sem inventar dados locais

#### Scenario: Descarte do rascunho
- **WHEN** o Gerente descarta comentário ainda não enviado
- **THEN** o Reflex limpa somente o conteúdo local sem executar requisição nem alterar o chamado

#### Scenario: Chamado terminal
- **WHEN** o detalhe informa status `Encerrado` ou `Cancelado`
- **THEN** o Reflex mantém os comentários públicos visíveis e oferece envio de comentário público pelo contrato autorizado, sem reabrir ou editar o chamado
