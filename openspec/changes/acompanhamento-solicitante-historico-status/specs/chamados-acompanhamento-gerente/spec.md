# Spec Delta

## ADDED Requirements

### Requirement: Histórico público de status é projetado de alteracao_chamado
O sistema DEVE (MUST) fornecer ao Gerente autenticado uma consulta específica, somente de leitura, do histórico público de status, autorizada no Xano pela mesma relação chamado → Totem → Loja do detalhe, e DEVE (MUST) oferecer a mesma consulta ao solicitante pelo contrato do solicitante. O histórico DEVE (MUST) ser projetado das interações `tipo_evento = alteracao_chamado` do chamado autorizado que representem transição válida de status: `alteracoes.status` presente, com `anterior` e `resultante` textuais não vazios e diferentes entre si, e `criado_em` preenchido. Interações sem transição válida de status DEVEM (MUST) ser ignoradas. A seleção NÃO DEVE (MUST NOT) usar o campo `visibilidade`, inclusive valores históricos armazenados em eventos operacionais. O DTO DEVE (MUST) conter exclusivamente `id`, `status_anterior`, `status_resultante`, `criado_em` e `autor`, ordenado por `criado_em` decrescente e `id` decrescente. `autor` DEVE (MUST) ser `{nome, perfil}` com rótulo oficial (`Gerente`, `Técnico`, `Diretoria` ou `Administrador`) para autor humano com perfil oficial; `{nome, perfil: null}` para usuário existente com perfil nulo ou não oficial, sem classificá-lo como `Sistema`; `{nome: "Sistema", perfil: null}` para evento gravado sem usuário; e `null` quando o evento possui usuário que não é encontrado. A projeção NÃO DEVE (MUST NOT) retornar `alteracoes` bruto nem suas demais chaves (responsável, prioridade, Categoria, SLA, referência a comentário), comentários, outros eventos operacionais, e-mail, identificadores de usuário, Loja do autor ou outro dado operacional restrito. A consulta NÃO DEVE (MUST NOT) criar, alterar ou gravar interações. O histórico contém somente transições registradas pelo Save operacional desde sua implantação; transições anteriores, inclusive a criação do chamado, NÃO DEVEM (MUST NOT) ser reconstruídas ou inferidas. Sem transições válidas, a consulta DEVE (MUST) retornar lista vazia.

#### Scenario: Histórico autorizado do Gerente
- **WHEN** um Gerente consulta o histórico de chamado da própria Loja que teve mudanças de status pelo Save
- **THEN** recebe uma entrada por transição válida, do mais recente ao mais antigo, com somente status anterior, status resultante, momento e autor

#### Scenario: Save sem mudança de status
- **WHEN** o chamado possui `alteracao_chamado` que altera somente responsável, prioridade, Categoria ou SLA
- **THEN** essa interação não aparece no histórico

#### Scenario: Transição inválida ou incompleta
- **WHEN** `alteracoes.status` está ausente, malformado, sem `anterior` ou `resultante`, com valores iguais, ou a interação não possui `criado_em`
- **THEN** a interação é ignorada, sem completar valores ausentes

#### Scenario: Chamado sem transições registradas
- **WHEN** o chamado não possui transição válida, inclusive por ter mudado de status antes da implantação do Save
- **THEN** o Xano retorna lista vazia sem erro e sem inferir transições

#### Scenario: Seleção independente de visibilidade
- **WHEN** um `alteracao_chamado` com transição válida possui `visibilidade` nula, `interna` ou `publica` armazenada
- **THEN** sua inclusão decorre somente do tipo, da transição e do chamado autorizado

#### Scenario: Demais diferenças não são expostas
- **WHEN** o mesmo `alteracao_chamado` registra também responsável, prioridade, Categoria, SLA ou referência a comentário
- **THEN** o DTO contém somente o par de status, o momento e o autor

#### Scenario: Leitura sem efeito
- **WHEN** o histórico é consultado
- **THEN** nenhum chamado, interação ou `ultima_atualizacao_em` é criado ou alterado

#### Scenario: Autor humano com perfil oficial
- **WHEN** o evento possui usuário existente com perfil oficial
- **THEN** o DTO apresenta somente nome de exibição e rótulo oficial do perfil

#### Scenario: Autor sem perfil reconhecido
- **WHEN** o usuário do evento existe, mas seu perfil é nulo ou não é um dos quatro perfis oficiais
- **THEN** o DTO retorna `autor = {nome, perfil: null}`, sem classificá-lo como `Sistema`

#### Scenario: Evento sem usuário
- **WHEN** o evento foi gravado sem usuário
- **THEN** o DTO apresenta `autor = {nome: "Sistema", perfil: null}`

#### Scenario: Usuário do evento não encontrado
- **WHEN** o evento possui usuário preenchido que não é encontrado
- **THEN** o DTO retorna `autor = null`, sem rotular como `Sistema` e sem inferir autoria

#### Scenario: Conteúdo não pertencente ao histórico
- **WHEN** o chamado possui comentários públicos, comentários internos e eventos de atribuição, reatribuição ou liberação
- **THEN** nenhum desses registros nem seus campos aparecem no histórico

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta o histórico de chamado de outra Loja
- **THEN** o Xano responde como não autorizado sem retornar eventos

#### Scenario: Perfil sem permissão no contrato do Gerente
- **WHEN** Técnico, Diretoria ou Administrador usa o contrato de histórico exclusivo do Gerente
- **THEN** o Xano responde como não autorizado

#### Scenario: Histórico do solicitante
- **WHEN** o solicitante associado consulta o histórico pelo contrato do solicitante
- **THEN** recebe o mesmo DTO; sem vínculo, recebe a resposta de recurso não encontrado

### Requirement: Solicitante consulta, somente para leitura, os chamados aos quais está associado
O sistema DEVE (MUST) fornecer ao usuário autenticado contratos próprios e somente de leitura da lista, do detalhe e dos comentários públicos dos chamados em que ele é o solicitante associado, autorizados conforme `autorizacao-perfis`. A lista DEVE (MUST) conter somente chamados cujo `solicitante_id` é o do usuário, com o mesmo DTO de item da lista do Gerente, ordenada por `ultima_atualizacao_em` decrescente e `id` decrescente, e nesta Sprint NÃO DEVE (MUST NOT) oferecer filtros, preferências salvas ou paginação. O detalhe DEVE (MUST) conter os mesmos campos funcionais do detalhe do Gerente, exceto `resumo_totem`, que DEVE (MUST) ser sempre `null`, e `solicitante` e `tecnico`, que DEVEM (MUST) conter somente `nome` quando presentes, sem identificador de usuário; o detalhe do Gerente permanece inalterado. Os comentários DEVEM (MUST) usar o mesmo filtro e o mesmo DTO público dos comentários do Gerente. Os contratos NÃO DEVEM (MUST NOT) retornar chamados de outros solicitantes, comentários internos, eventos operacionais além da projeção do histórico público de status, timeline técnica ou telemetria, nem oferecer comentário, rejeição de solução, Save, atribuição ou outra escrita.

#### Scenario: Solicitante de outra Loja acompanha o chamado
- **WHEN** um usuário que abriu o chamado como Gerente da Loja A hoje está associado à Loja B
- **THEN** a lista contém o chamado e o detalhe e os comentários públicos são retornados

#### Scenario: Lista restrita ao vínculo
- **WHEN** um usuário consulta a lista do solicitante
- **THEN** recebe somente seus chamados, sem chamados automáticos nem de outros solicitantes, sem contagem ou metadado de chamados de terceiros

#### Scenario: Ordenação estável
- **WHEN** dois chamados do usuário possuem o mesmo `ultima_atualizacao_em`
- **THEN** o de maior `id` aparece primeiro

#### Scenario: Usuário sem chamados associados
- **WHEN** o usuário autenticado não é solicitante de nenhum chamado
- **THEN** a lista é vazia, sem erro de autorização

#### Scenario: Detalhe sem telemetria e sem identificadores de usuário
- **WHEN** o solicitante consulta o detalhe de chamado associado, com ou sem Técnico responsável
- **THEN** o DTO contém `resumo_totem = null`, nenhum dado de telemetria, `solicitante` somente com `nome` e `tecnico` nulo ou somente com `nome`

#### Scenario: Conteúdo privado não é exposto ao solicitante
- **WHEN** o chamado associado possui comentários internos e eventos operacionais
- **THEN** os contratos de lista, detalhe e comentários do solicitante não retornam esses registros, e o contrato de histórico retorna somente o par de status projetado

#### Scenario: Acompanhamento sem escrita
- **WHEN** o chamado associado está em qualquer status, inclusive `Resolvido`
- **THEN** nenhum contrato do solicitante altera o chamado, cria interação ou oferece aceitação ou rejeição

## MODIFIED Requirements

### Requirement: Interações possuem visibilidade explícita e falham fechadas
Cada novo comentário criado por esta capacidade DEVE (MUST) possuir visibilidade explícita. Comentário sem confirmação de visibilidade pública NÃO DEVE (MUST NOT) ser retornado ao Gerente nem ao solicitante, inclusive registros legados sem essa classificação. Eventos operacionais não possuem visibilidade e NÃO DEVEM (MUST NOT) ser retornados ao Gerente nem ao solicitante, com a única exceção da projeção do par de status de `alteracao_chamado`, exposta exclusivamente pelos contratos de histórico público de status e sem os demais campos do evento; valores de visibilidade armazenados em eventos históricos NÃO DEVEM (MUST NOT) ser usados para classificá-los ou autorizá-los.

#### Scenario: Interação legada sem visibilidade
- **WHEN** um comentário existente não possui visibilidade explícita
- **THEN** ele não aparece na consulta de comentários do Gerente nem do solicitante

#### Scenario: Conteúdo interno
- **WHEN** um comentário é classificado como não público
- **THEN** ele não é retornado ao Gerente nem ao solicitante, independentemente de autoria, conteúdo ou data

#### Scenario: Evento operacional não é exposto
- **WHEN** o chamado possui `alteracao_chamado`, atribuição, reatribuição ou liberação, inclusive com metadado histórico de visibilidade
- **THEN** nenhum contrato do Gerente ou do solicitante retorna esses eventos, exceto o par de status projetado pelo histórico público

### Requirement: Comentários preservam segurança dos contratos funcionais
As consultas e criações de comentários DEVEM (MUST) exigir autenticação de `usuarios`, aplicar a autorização própria de cada contrato e manter os CRUDs genéricos fora do contrato funcional. Os contratos de comentários do Gerente DEVEM (MUST) autorizar exclusivamente Gerente no escopo da própria Loja. O contrato de comentários do solicitante DEVE (MUST) autorizar conforme o vínculo definido em `autorizacao-perfis` e é somente de leitura; a criação de comentário nesta capacidade permanece exclusiva do contrato do Gerente. As falhas DEVEM (MUST) ser classificadas como 401, 403, 404, 422 ou 5xx conforme a causa, sem expor conteúdo protegido.

#### Scenario: Perfil sem permissão
- **WHEN** Técnico, Diretoria ou outro perfil usa o contrato exclusivo de comentários do Gerente
- **THEN** o Xano responde como não autorizado sem ler ou criar comentários

#### Scenario: Solicitante sem vínculo
- **WHEN** um usuário consulta pelo contrato do solicitante os comentários de chamado do qual não é solicitante
- **THEN** o Xano responde como recurso não encontrado sem ler comentários

#### Scenario: Contrato do solicitante não cria comentário
- **WHEN** o solicitante acompanha um chamado pelos contratos do solicitante
- **THEN** não existe operação de criação de comentário nesses contratos

## RENAMED Requirements

- FROM: `### Requirement: Gerente publica comentário público em chamado não terminal`
- TO: `### Requirement: Gerente publica comentário público em chamado da própria Loja`
