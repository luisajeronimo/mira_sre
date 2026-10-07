# Spec Delta

## Purpose

Definir o acompanhamento público e seguro de chamados pelo Gerente, com
comentários autorizados por Loja e uma data funcional da última alteração
observável, sem expor interações internas ou criar tratativa completa.

## ADDED Requirements

### Requirement: Última atualização representa alteração observável pelo Gerente
O sistema DEVE (MUST) manter `ultima_atualizacao_em` em cada chamado como o instante da última alteração observável pelo Gerente. A criação, atribuição efetiva, mudança de status e comentário público DEVEM (MUST) atualizá-lo; leitura e eventos internos não visíveis NÃO DEVEM (MUST NOT) atualizá-lo.

#### Scenario: Criação inicializa a última atualização
- **WHEN** um fluxo funcional cria um novo chamado
- **THEN** `ultima_atualizacao_em` recebe o mesmo instante funcional de `criado_em`

#### Scenario: Atribuição efetiva atualiza a data
- **WHEN** uma atribuição altera o Técnico responsável de um chamado
- **THEN** o Xano atualiza `ultima_atualizacao_em` no mesmo ato da alteração

#### Scenario: Mudança de status futura atualiza a data
- **WHEN** um fluxo funcional autorizado altera o status de um chamado
- **THEN** o Xano atualiza `ultima_atualizacao_em` no mesmo ato da alteração de status

#### Scenario: Evento interno não visível
- **WHEN** ocorre nota interna, work log, diagnóstico ou outra operação sem consequência visível ao Gerente
- **THEN** o evento não altera `ultima_atualizacao_em`

### Requirement: Dados legados permanecem sem última atualização inferida
Chamados existentes sem valor confiável de `ultima_atualizacao_em` DEVEM (MUST) permanecer nulos. O sistema NÃO DEVE (MUST NOT) fazer backfill ou derivar esse valor de `created_at`, `criado_em`, atribuição, interações ou outro timestamp aproximado.

#### Scenario: Chamado legado sem dado confiável
- **WHEN** um chamado histórico não possui `ultima_atualizacao_em`
- **THEN** a leitura preserva o valor nulo sem fabricar uma data funcional

### Requirement: Detalhe autorizado expõe a última atualização funcional
O DTO de `GET /gerente/chamados/{chamados_id}` DEVE (MUST) retornar
`ultima_atualizacao_em` como dado funcional do chamado autorizado. Quando o
registro legado não possuir esse valor, o DTO DEVE (MUST) devolvê-lo como
`null`, sem substituí-lo por timestamp técnico ou inferido.

#### Scenario: Detalhe de chamado legado
- **WHEN** o Gerente autorizado consulta chamado com `ultima_atualizacao_em`
  nulo
- **THEN** a resposta preserva `ultima_atualizacao_em = null`

### Requirement: Interações possuem visibilidade explícita e falham fechadas
Cada nova interação criada por esta capacidade DEVE (MUST) possuir visibilidade explícita. Interação sem confirmação de visibilidade pública NÃO DEVE (MUST NOT) ser retornada ao Gerente, inclusive registros legados sem essa classificação.

#### Scenario: Interação legada sem visibilidade
- **WHEN** uma interação existente não possui visibilidade explícita
- **THEN** ela não aparece na consulta de comentários do Gerente

#### Scenario: Conteúdo interno
- **WHEN** uma interação é classificada como não pública
- **THEN** ela não é retornada ao Gerente, independentemente de autoria, conteúdo ou data

### Requirement: Gerente consulta comentários públicos do chamado da própria Loja
O sistema DEVE (MUST) fornecer uma consulta específica de comentários públicos por chamado ao Gerente autenticado. Ela DEVE (MUST) autorizar o chamado pela relação persistida chamado, Totem e Loja, retornar somente DTO sanitizado de comentário público e ordenar por `criado_em` decrescente. O DTO público contém exclusivamente `id`, `conteudo`, `criado_em` e `autor`, sendo `autor` objeto nulo ou com somente o campo público `nome`; ele NÃO DEVE (MUST NOT) expor identificador de usuário, e-mail, perfil, Loja, credenciais ou qualquer atributo interno.

#### Scenario: Consulta autorizada ordenada
- **WHEN** um Gerente consulta os comentários públicos de chamado ligado a Totem de sua Loja
- **THEN** recebe somente comentários públicos, do mais recente ao mais antigo, com conteúdo, data funcional e autor limitado ao nome público

#### Scenario: Relação de autor ausente ou incompatível
- **WHEN** um comentário público possui relação de autor ausente ou que não pode ser projetada com segurança
- **THEN** o DTO retorna `autor = null`, sem vazar identificador ou atributo interno e sem inferir autoria

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta comentários de chamado associado a outra Loja
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta comentários de identificador inexistente
- **THEN** o Xano responde como recurso não encontrado

### Requirement: Gerente publica comentário público em chamado não terminal
O sistema DEVE (MUST) fornecer comando específico para o Gerente autenticado publicar comentário público não vazio em chamado de sua Loja que não esteja `Encerrado` nem `Cancelado`. Autor, visibilidade e `criado_em` DEVEM (MUST) ser definidos pelo Xano; o comando DEVE (MUST) atualizar `ultima_atualizacao_em` junto da criação.

#### Scenario: Comentário público válido
- **WHEN** um Gerente autorizado envia conteúdo não vazio para chamado não terminal de sua Loja
- **THEN** o Xano cria comentário público com autor da sessão e data do backend, atualiza `ultima_atualizacao_em` e retorna somente o DTO sanitizado

#### Scenario: Autoridade do cliente é ignorada
- **WHEN** o cliente tenta informar autor, Loja, visibilidade, timestamp ou status junto do comentário
- **THEN** esses valores não são usados como autoridade pelo Xano

#### Scenario: Comentário vazio ou somente espaços
- **WHEN** o conteúdo está ausente, vazio ou fica vazio após remoção de espaços nas extremidades
- **THEN** o Xano rejeita a operação como entrada inválida sem criar interação ou alterar `ultima_atualizacao_em`

#### Scenario: Chamado terminal permanece somente leitura
- **WHEN** o chamado possui status `Encerrado` ou `Cancelado`
- **THEN** o Gerente pode consultar comentários públicos, mas o Xano rejeita novo comentário sem criar interação ou alterar `ultima_atualizacao_em`

### Requirement: Comentários preservam segurança dos contratos funcionais
As consultas e criações de comentários DEVEM (MUST) exigir autenticação de `usuarios`, autorizar exclusivamente Gerente no escopo da própria Loja e manter os CRUDs genéricos fora do contrato funcional. As falhas DEVEM (MUST) ser classificadas como 401, 403, 404, 422 ou 5xx conforme a causa, sem expor conteúdo protegido.

#### Scenario: Perfil sem permissão
- **WHEN** Técnico, Diretoria ou outro perfil usa o contrato exclusivo de comentários do Gerente
- **THEN** o Xano responde como não autorizado sem ler ou criar comentários
