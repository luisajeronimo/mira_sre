# Spec Delta

## ADDED Requirements

### Requirement: Rejeição de solução reabre o chamado
O Xano DEVE (MUST) oferecer uma operação autenticada específica de rejeição de solução, separada do Save da tratativa operacional. A operação DEVE (MUST) validar, antes de qualquer escrita, a autorização definida em `autorizacao-perfis`, a justificativa não vazia após trim e o status persistido `Resolvido`. Dentro da unidade de escrita, o Xano DEVE (MUST) reler o chamado e revalidar, com os dados atuais do chamado e a identidade autenticada, a autorização, o status `Resolvido` e `ultima_atualizacao_em`, sem depender exclusivamente da validação anterior. Ao confirmar, o Xano DEVE (MUST) executar exatamente quatro escritas na mesma unidade: a atualização do chamado para `Reaberto` com `ultima_atualizacao_em`; o comentário público com a justificativa e o usuário autenticado como autor; o evento público de transição `Resolvido` → `Reaberto`; e o evento de auditoria privado. Leituras de confirmação não são escritas. A operação NÃO DEVE (MUST NOT) alterar responsável, prioridade, Categoria, SLA aplicado ou outros dados funcionais, nem aplicar outro status depois de `Reaberto`. Autor, visibilidade, status e timestamps DEVEM (MUST) ser definidos pelo Xano.

#### Scenario: Gerente da Loja rejeita solução
- **WHEN** um Gerente autenticado rejeita, com justificativa não vazia, um chamado `Resolvido` ligado a Totem da própria Loja, sendo ou não o solicitante
- **THEN** o Xano registra comentário público com a justificativa e o Gerente como autor, evento público `Resolvido` → `Reaberto`, auditoria privada, status `Reaberto` e `ultima_atualizacao_em`, preservando os demais dados funcionais

#### Scenario: Gerente rejeita chamado automático sem solicitante humano
- **WHEN** o chamado `Resolvido` foi criado pelo Bot de Fiscalização, não possui solicitante humano e pertence à Loja do Gerente
- **THEN** o Xano aceita a rejeição do Gerente nas mesmas condições

#### Scenario: Solicitante associado rejeita solução
- **WHEN** o usuário autenticado é o solicitante humano associado e o chamado está `Resolvido`
- **THEN** o Xano aceita a rejeição e registra os mesmos itens com esse usuário como autor

#### Scenario: Justificativa ausente ou vazia
- **WHEN** a justificativa está ausente, vazia ou contém somente espaços após trim
- **THEN** o Xano rejeita a operação como entrada inválida sem alterar status, criar interação ou atualizar `ultima_atualizacao_em`

#### Scenario: Chamado não está Resolvido
- **WHEN** o status persistido no momento da operação é diferente de `Resolvido`
- **THEN** o Xano rejeita a operação como conflito sem registrar justificativa, evento ou alteração

#### Scenario: Detalhe desatualizado
- **WHEN** o `ultima_atualizacao_em` informado difere do valor persistido
- **THEN** o Xano rejeita a operação como conflito sem efeito parcial

#### Scenario: Chamado inexistente
- **WHEN** o identificador não corresponde a chamado existente
- **THEN** o Xano responde como recurso não encontrado

#### Scenario: Reabertura não aplica transição posterior
- **WHEN** a rejeição é concluída
- **THEN** o chamado permanece `Reaberto` até uma ação posterior autorizada pelo Save operacional

#### Scenario: Autorização perdida antes da escrita
- **WHEN** a autorização foi aceita na validação inicial, mas a releitura dentro da unidade de escrita mostra que o usuário não atende mais a nenhuma condição de autorização
- **THEN** o Xano nega a operação sem executar nenhuma das quatro escritas

#### Scenario: Status alterado antes da escrita
- **WHEN** a releitura dentro da unidade de escrita mostra status diferente de `Resolvido` ou `ultima_atualizacao_em` divergente
- **THEN** o Xano rejeita a operação como conflito sem executar nenhuma das quatro escritas

#### Scenario: Falha em uma das quatro escritas
- **WHEN** falha a atualização do chamado, o comentário público, o evento público ou a auditoria privada
- **THEN** o Xano não confirma sucesso; a ausência de efeito parcial só é declarada se o gate de transação e rollback do design tiver sido confirmado com evidência

### Requirement: Gerente consulta o histórico público de status do chamado da própria Loja
O sistema DEVE (MUST) fornecer ao Gerente autenticado uma consulta específica do histórico público de status, autorizada pela mesma relação chamado → Totem → Loja do detalhe. A consulta DEVE (MUST) retornar somente eventos `alteracao_status` com visibilidade pública, ordenados por `criado_em` decrescente, em DTO com exclusivamente `id`, `status_anterior`, `status_resultante`, `criado_em` e `autor`. `autor` DEVE (MUST) conter somente `nome` (nome de exibição) e `perfil` (rótulo oficial `Gerente`, `Técnico`, `Diretoria` ou `Administrador`) quando o evento tiver autor humano; usuário existente sem perfil reconhecido DEVE (MUST) apresentar `autor = {nome, perfil: null}`, sem ser classificado como `Sistema`; evento automático, gravado sem usuário, DEVE (MUST) apresentar `autor.nome = "Sistema"` e `perfil` nulo; evento com `usuarios_id` preenchido cujo usuário não seja encontrado DEVE (MUST) retornar `autor = null`, sem ser rotulado como `Sistema`. Ela NÃO DEVE (MUST NOT) retornar comentários, eventos internos, `alteracoes` bruto, e-mail, identificadores de usuário, Loja do autor ou outro dado de auditoria. O histórico DEVE (MUST) conter somente eventos gravados a partir desta change; o sistema NÃO DEVE (MUST NOT) criar eventos retroativos nem derivar eventos da auditoria interna.

#### Scenario: Histórico autorizado
- **WHEN** um Gerente consulta o histórico de chamado da própria Loja
- **THEN** recebe as transições públicas de status do mais recente ao mais antigo, sem comentários nem auditoria

#### Scenario: Reabertura aparece no histórico
- **WHEN** uma rejeição foi concluída
- **THEN** o histórico contém o evento `Resolvido` → `Reaberto` e a consulta de comentários contém, separadamente, a justificativa

#### Scenario: Autor humano no histórico
- **WHEN** o evento foi gravado pelo Save de um Técnico ou pela rejeição de um Gerente
- **THEN** o DTO apresenta o nome de exibição e o perfil (`Técnico` ou `Gerente`) do autor, sem e-mail, identificador ou Loja

#### Scenario: Evento automático identificado como Sistema
- **WHEN** o evento público de status foi gravado sem usuário por fluxo automático
- **THEN** o DTO apresenta `autor.nome = "Sistema"` e `perfil` nulo

#### Scenario: Autor humano sem perfil reconhecido
- **WHEN** o usuário do evento existe, mas seu perfil é nulo ou não é um dos quatro perfis oficiais
- **THEN** o DTO retorna `autor = {nome, perfil: null}`, sem classificá-lo como `Sistema`

#### Scenario: Usuário do evento não encontrado
- **WHEN** o evento possui `usuarios_id` preenchido, mas o usuário não é encontrado
- **THEN** o DTO retorna `autor = null`, sem rotular como `Sistema` e sem inferir autoria

#### Scenario: Histórico não expõe dados privados
- **WHEN** o chamado possui comentários internos, auditoria `alteracao_chamado` e eventos de atribuição
- **THEN** nenhum desses registros nem seus campos aparecem no histórico público

#### Scenario: Chamado sem eventos registrados
- **WHEN** o chamado não possui eventos públicos de status, inclusive por ter transições anteriores a esta change
- **THEN** o Xano retorna lista vazia sem inferir eventos

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta o histórico de chamado de outra Loja
- **THEN** o Xano responde como não autorizado sem retornar eventos

#### Scenario: Perfil sem permissão
- **WHEN** Técnico, Diretoria ou Administrador usa o contrato exclusivo do Gerente
- **THEN** o Xano responde como não autorizado

### Requirement: Solicitante consulta os chamados aos quais está associado
O sistema DEVE (MUST) fornecer ao usuário humano autenticado contratos próprios de consulta da lista, do detalhe, dos comentários públicos e do histórico público dos chamados em que ele é o solicitante associado. A autorização DEVE (MUST) ser aplicada no Xano exclusivamente pelo vínculo `solicitante_id` com a identidade autenticada e NÃO DEVE (MUST NOT) depender da Loja atual do usuário. Os contratos de comentários e histórico DEVEM (MUST) usar os mesmos DTOs e filtros de visibilidade públicos dos contratos do Gerente. O detalhe do solicitante DEVE (MUST) conter os mesmos campos funcionais do detalhe do Gerente, exceto `resumo_totem`, que DEVE (MUST) ser sempre `null`; o detalhe do Gerente permanece inalterado. A lista DEVE (MUST) ser ordenada por `ultima_atualizacao_em` decrescente e, nesta Sprint, NÃO DEVE (MUST NOT) oferecer filtros, preferências salvas ou paginação. Os contratos NÃO DEVEM (MUST NOT) retornar chamados sem vínculo, comentários internos, auditoria ou timeline técnica, nem oferecer comentário, Save ou atribuição. A rejeição a partir dessa interface DEVE (MUST) usar a mesma operação de rejeição de solução.

#### Scenario: Solicitante transferido de Loja
- **WHEN** um usuário abriu o chamado como Gerente da Loja A e hoje está associado à Loja B
- **THEN** a lista do solicitante contém o chamado e o detalhe, os comentários públicos e o histórico público são retornados

#### Scenario: Solicitante transferido rejeita solução
- **WHEN** esse solicitante transferido rejeita, com justificativa válida, o chamado `Resolvido` ao qual está associado
- **THEN** o Xano aceita a rejeição e reabre o chamado

#### Scenario: Usuário sem vínculo com o chamado
- **WHEN** um usuário consulta pelo contrato do solicitante um chamado do qual não é solicitante, ainda que pertença à Loja dele
- **THEN** o Xano responde como não autorizado sem retornar dados do chamado

#### Scenario: Lista restrita ao vínculo
- **WHEN** um usuário consulta a lista do solicitante
- **THEN** recebe somente chamados cujo `solicitante_id` é o seu, sem chamados automáticos nem de outros solicitantes, ordenados por `ultima_atualizacao_em` decrescente

#### Scenario: Usuário sem chamados associados
- **WHEN** o usuário autenticado não é solicitante de nenhum chamado
- **THEN** a lista é vazia, sem erro de autorização

#### Scenario: Detalhe do solicitante sem telemetria
- **WHEN** o solicitante consulta o detalhe de chamado associado, inclusive de Totem de outra Loja
- **THEN** o DTO contém `resumo_totem = null` e nenhum dado de telemetria do Totem

#### Scenario: Conteúdo privado não é exposto ao solicitante
- **WHEN** o chamado associado possui comentários internos e auditoria
- **THEN** os contratos do solicitante retornam somente comentários públicos e eventos públicos de status

## MODIFIED Requirements

### Requirement: Interações possuem visibilidade explícita e falham fechadas
Cada nova interação criada por esta capacidade DEVE (MUST) possuir visibilidade explícita. Interação sem confirmação de visibilidade pública NÃO DEVE (MUST NOT) ser retornada ao Gerente, inclusive registros legados sem essa classificação. Eventos públicos de status (`alteracao_status`) e comentários públicos DEVEM (MUST) ser registros distintos; eventos de auditoria (`alteracao_chamado`, atribuição, reatribuição e liberação) DEVEM (MUST) permanecer internos.

#### Scenario: Interação legada sem visibilidade
- **WHEN** uma interação existente não possui visibilidade explícita
- **THEN** ela não aparece na consulta de comentários nem no histórico do Gerente

#### Scenario: Conteúdo interno
- **WHEN** uma interação é classificada como não pública
- **THEN** ela não é retornada ao Gerente, independentemente de autoria, conteúdo ou data

#### Scenario: Evento de auditoria permanece interno
- **WHEN** o Save ou a rejeição grava a auditoria da alteração
- **THEN** o evento é interno e não é retornado ao Gerente por nenhum contrato

### Requirement: Gerente consulta comentários públicos do chamado da própria Loja
O sistema DEVE (MUST) fornecer uma consulta específica de comentários públicos por chamado ao Gerente autenticado. Ela DEVE (MUST) autorizar o chamado pela relação persistida chamado, Totem e Loja, retornar somente DTO sanitizado de comentário público e ordenar por `criado_em` decrescente. Somente interações públicas com `tipo_evento` nulo (legado) ou `comentario` e conteúdo não vazio DEVEM (MUST) ser retornadas; eventos públicos de status NÃO DEVEM (MUST NOT) aparecer nesta consulta. O DTO público contém exclusivamente `id`, `conteudo`, `criado_em` e `autor`, sendo `autor` objeto nulo ou com somente o campo público `nome`; ele NÃO DEVE (MUST NOT) expor identificador de usuário, e-mail, perfil, Loja, credenciais ou qualquer atributo interno.

#### Scenario: Consulta autorizada ordenada
- **WHEN** um Gerente consulta os comentários públicos de chamado ligado a Totem de sua Loja
- **THEN** recebe somente comentários públicos, do mais recente ao mais antigo, com conteúdo, data funcional e autor limitado ao nome público

#### Scenario: Justificativa de rejeição
- **WHEN** o chamado foi reaberto por rejeição
- **THEN** a justificativa aparece como comentário público com o nome do autor da rejeição

#### Scenario: Evento público de status não é comentário
- **WHEN** o chamado possui eventos `alteracao_status`
- **THEN** eles não são retornados pela consulta de comentários

#### Scenario: Relação de autor ausente ou incompatível
- **WHEN** um comentário público possui relação de autor ausente ou que não pode ser projetada com segurança
- **THEN** o DTO retorna `autor = null`, sem vazar identificador ou atributo interno e sem inferir autoria

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta comentários de chamado associado a outra Loja
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta comentários de identificador inexistente
- **THEN** o Xano responde como recurso não encontrado

## RENAMED Requirements

- FROM: `Gerente publica comentário público em chamado não terminal`
- TO: `Gerente publica comentário público em chamado da própria Loja`
