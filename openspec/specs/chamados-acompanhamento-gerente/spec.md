# chamados-acompanhamento-gerente Specification

## Purpose

Definir o acompanhamento público e seguro de chamados pelo Gerente, com comentários autorizados por Loja e uma data funcional da última alteração observável, sem expor interações internas ou criar tratativa completa.

## Requirements

### Requirement: Última atualização representa alteração observável pelo Gerente
Todo chamado válido DEVE (MUST) possuir `criado_em` e `ultima_atualizacao_em`. Na criação manual ou automática, o Xano DEVE (MUST) definir ambos com o mesmo instante funcional, calculado uma única vez; `criado_em` permanece imutável. Atribuição efetiva, mudança de status e comentário Público ou Interno autorizado DEVEM (MUST) atualizar somente `ultima_atualizacao_em`; leitura e eventos internos sem comentário ou consequência funcional NÃO DEVEM (MUST NOT) atualizá-lo.

#### Scenario: Criação inicializa os timestamps funcionais
- **WHEN** um fluxo funcional cria chamado válido
- **THEN** `criado_em` e `ultima_atualizacao_em` recebem o mesmo instante funcional definido pelo Xano

#### Scenario: Criação inicializa a última atualização
- **WHEN** um fluxo funcional cria novo chamado válido
- **THEN** `ultima_atualizacao_em` recebe o mesmo instante funcional de `criado_em`

#### Scenario: Evento observável posterior
- **WHEN** atribuição efetiva, mudança de status ou comentário Público autorizado ocorre
- **THEN** `criado_em` permanece imutável e o Xano atualiza `ultima_atualizacao_em` no mesmo ato

#### Scenario: Atribuição efetiva atualiza a data
- **WHEN** uma atribuição altera o Técnico responsável de um chamado
- **THEN** o Xano atualiza somente `ultima_atualizacao_em` no mesmo ato da alteração

#### Scenario: Mudança de status futura atualiza a data
- **WHEN** um fluxo funcional autorizado altera o status de um chamado
- **THEN** o Xano atualiza somente `ultima_atualizacao_em` no mesmo ato da alteração de status

#### Scenario: Comentário interno operacional
- **WHEN** um perfil operacional publica comentário Interno autorizado
- **THEN** o Xano atualiza `ultima_atualizacao_em` sem tornar o conteúdo do comentário visível ao Gerente

#### Scenario: Evento interno não visível
- **WHEN** ocorre diagnóstico ou outra operação interna sem comentário nem consequência funcional
- **THEN** o evento não altera `ultima_atualizacao_em`

### Requirement: Dados legados permanecem sem última atualização inferida
O sistema NÃO DEVE (MUST NOT) fazer backfill ou derivar `criado_em` ou `ultima_atualizacao_em` de `created_at`, atribuição, interações ou outro timestamp aproximado. Registros históricos com ausência desses dados não são chamados válidos para a jornada operacional e não recebem compatibilidade de leitura nesta change.

#### Scenario: Registro histórico com timestamp ausente
- **WHEN** existe registro com `criado_em` ou `ultima_atualizacao_em` ausente
- **THEN** o sistema não altera o registro nem fabrica timestamp; a existência é somente reportada antes de qualquer ação de dados

#### Scenario: Chamado legado sem dado confiável
- **WHEN** um chamado histórico não possui `ultima_atualizacao_em`
- **THEN** a change não faz backfill nem substitui o valor por data técnica; esse registro não recebe compatibilidade temporal na jornada operacional

### Requirement: Detalhe autorizado expõe a última atualização funcional
O DTO de `GET /gerente/chamados/{chamados_id}` DEVE (MUST) retornar `criado_em` e `ultima_atualizacao_em` como timestamps funcionais obrigatórios do chamado válido autorizado, sem usar `created_at` ou timestamp inferido como fallback.

#### Scenario: Detalhe de chamado válido
- **WHEN** o Gerente autorizado consulta chamado válido
- **THEN** a resposta contém os dois timestamps funcionais definidos pelo Xano

#### Scenario: Detalhe de chamado legado
- **WHEN** o Gerente autorizado consulta chamado histórico com `ultima_atualizacao_em` ausente
- **THEN** o contrato não inventa timestamp nem usa `created_at` como fallback; o registro não é compatível com a jornada operacional desta change

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

### Requirement: Gerente consulta comentários públicos do chamado da própria Loja
O sistema DEVE (MUST) fornecer consulta específica de comentários públicos por chamado ao Gerente autenticado, autorizada pela Loja resolvida pelo vínculo histórico do Totem em `criado_em` (`vinculo-historico-totem-loja`), com resultados em ordem decrescente de `criado_em`. O DTO contém somente `id`, `conteudo`, `criado_em` e `autor`. `autor` é nulo ou objeto apenas com `nome`; para o comentário comprovadamente gerado pelo encerramento sob comando, DEVE (MUST) ser `{nome: "Sistema"}`. Nenhum identificador de usuário, e-mail, perfil, Loja, credencial ou dado interno do autor é exposto.

#### Scenario: Consulta autorizada ordenada
- **WHEN** um Gerente consulta comentários públicos de chamado comprovadamente aberto em sua Loja
- **THEN** recebe somente comentários públicos, do mais recente ao mais antigo, com conteúdo, data funcional e autor limitado ao nome público

#### Scenario: Comentário gerado pelo encerramento sob comando
- **WHEN** a consulta inclui o comentário público vinculado à transição `Resolvido` → `Encerrado` criada pelo comando de encerramento, sem usuário humano
- **THEN** o DTO desse comentário retorna `autor = {nome: "Sistema"}`

#### Scenario: Relação de autor ausente ou incompatível
- **WHEN** um comentário público não possui autor projetável com segurança e não é comprovadamente o comentário do encerramento sob comando
- **THEN** o DTO retorna `autor = null`, sem inferir autoria nem expor identificador ou atributo interno

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta comentários de chamado comprovadamente aberto em outra Loja
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta comentários de identificador inexistente
- **THEN** o Xano responde como recurso não encontrado

#### Scenario: Loja histórica não demonstrável
- **WHEN** não é possível comprovar a Loja de abertura do chamado legado
- **THEN** o Xano não libera comentários ao Gerente por inferência da Loja atual do Totem

#### Scenario: Chamado sem Loja histórica
- **WHEN** um Gerente consulta comentários de chamado cuja Loja resolvida é nula
- **THEN** o Xano responde como não autorizado sem retornar comentários

### Requirement: Gerente publica comentário público em chamado da própria Loja
O sistema DEVE (MUST) fornecer comando específico para o Gerente autenticado publicar comentário Público não vazio em chamado historicamente autorizado de sua Loja, inclusive quando estiver Encerrado ou Cancelado. Autor, visibilidade e `criado_em` DEVEM (MUST) ser definidos pelo Xano; o comando DEVE (MUST) atualizar `ultima_atualizacao_em` junto da criação, sem modificar campos funcionais nem reabrir chamado terminal.

#### Scenario: Comentário público válido
- **WHEN** Gerente autorizado envia conteúdo não vazio para chamado historicamente autorizado de sua Loja
- **THEN** o Xano cria comentário Público com autor da sessão, atualiza `ultima_atualizacao_em` e retorna somente o DTO sanitizado

#### Scenario: Chamado terminal permite comentário público
- **WHEN** o chamado autorizado da Loja do Gerente está Encerrado ou Cancelado e recebe comentário Público não vazio
- **THEN** o Xano cria somente o comentário, atualiza `ultima_atualizacao_em` e preserva os campos funcionais

#### Scenario: Gerente tenta comentário Interno
- **WHEN** o Gerente tenta criar comentário Interno ou informar visibilidade distinta de Público
- **THEN** o Xano rejeita a operação sem criar interação

#### Scenario: Comentário fora do escopo
- **WHEN** o Gerente tenta comentar chamado fora da Loja histórica comprovada de sua sessão ou jornada autorizada
- **THEN** o Xano rejeita a operação sem expor ou alterar o chamado

#### Scenario: Autoridade do cliente é ignorada
- **WHEN** o cliente tenta informar autor, Loja, timestamp, status ou outro campo funcional junto do comentário
- **THEN** o Xano usa somente identidade, escopo, visibilidade Pública e data definidos pelo backend

#### Scenario: Comentário vazio ou somente espaços
- **WHEN** o conteúdo está ausente, vazio ou fica vazio após remoção de espaços nas extremidades
- **THEN** o Xano rejeita a operação sem criar interação ou alterar `ultima_atualizacao_em`

#### Scenario: Chamado terminal permanece somente leitura
- **WHEN** o chamado possui status Encerrado ou Cancelado
- **THEN** o Gerente pode consultar e publicar comentário Público autorizado, mas não altera nenhum campo funcional

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

### Requirement: Visibilidade de comentário não define autorização do chamado
Público/Interno DEVE (MUST) classificar somente comentários. O acesso do Gerente ao chamado e ao status atual DEVE (MUST) continuar derivado da sessão e da Loja histórica demonstrável na abertura. O contrato público de comentários DEVE (MUST) retornar somente interações de comentário explicitamente públicas, sem inferir que evento operacional sem visibilidade seja público ou privado.

#### Scenario: Gerente consulta status atual
- **WHEN** o Gerente autorizado abre chamado comprovadamente de sua Loja após alteração operacional de Status
- **THEN** o detalhe apresenta o Status atual persistido independentemente da visibilidade dos comentários associados

#### Scenario: Comentário interno permanece protegido
- **WHEN** chamado autorizado possui comentário Interno e eventos operacionais
- **THEN** a consulta pública não retorna o comentário Interno nem usa os eventos para contornar essa restrição

#### Scenario: Evento operacional não é comentário privado
- **WHEN** evento operacional novo ou histórico não possui classificação funcional de visibilidade
- **THEN** o contrato de comentários não o retorna nem o classifica como comentário Público ou Interno

#### Scenario: Escopo da change no histórico do Gerente
- **WHEN** o Gerente consulta o acompanhamento autorizado
- **THEN** permanece com o detalhe atual e os comentários públicos vigentes, sem receber por esta change a timeline operacional global dos perfis internos

### Requirement: Transferência de Totem preserva escopo histórico de chamado
Listagem, detalhe e comentários do Gerente DEVEM (MUST) autorizar chamados pela Loja demonstrável em `criado_em`. Uma transferência NÃO DEVE (MUST NOT) expor chamados antigos ao Gerente da Loja de destino nem ocultar da origem os chamados cuja Loja histórica seja comprovada. Sem comprovação, a autorização DEVE (MUST) falhar fechada.

#### Scenario: Gerente da Loja de origem
- **WHEN** Totem é transferido e Gerente da Loja de origem consulta chamado anterior com vínculo histórico comprovado
- **THEN** o Xano mantém o chamado consultável e comentável conforme as regras existentes da jornada

#### Scenario: Gerente da Loja de destino
- **WHEN** Gerente da Loja de destino tenta consultar chamado anterior à transferência
- **THEN** o Xano rejeita sem expor chamado ou comentários

#### Scenario: Loja de origem não demonstrável
- **WHEN** um chamado legado anterior ao primeiro vínculo comprovado não permite determinar a Loja da abertura
- **THEN** nenhum Gerente o recebe por inferência do vínculo atual; o registro permanece preservado

#### Scenario: Loja Inativa existente
- **WHEN** Loja do Gerente já vinculado passa a `Inativa`
- **THEN** ele continua a consultar e comentar chamados historicamente autorizados conforme as regras existentes

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
O sistema DEVE (MUST) fornecer ao usuário autenticado contratos próprios e somente de leitura da lista, do detalhe e dos comentários públicos dos chamados em que ele é o solicitante associado, autorizados conforme `autorizacao-perfis`. A lista DEVE (MUST) conter somente chamados cujo `solicitante_id` é o do usuário, com o mesmo DTO de item da lista do Gerente, ordenada por `ultima_atualizacao_em` decrescente e `id` decrescente, e nesta Sprint NÃO DEVE (MUST NOT) oferecer filtros, preferências salvas ou paginação. O detalhe DEVE (MUST) conter os mesmos campos funcionais do detalhe do Gerente, exceto `resumo_totem`, que DEVE (MUST) ser sempre `null`, `solicitante` e `tecnico`, que DEVEM (MUST) conter somente `nome` quando presentes, sem identificador de usuário, e `sla_horas_aplicado`, que NÃO DEVE (MUST NOT) ser exposto ao solicitante conforme DE-8; o detalhe do Gerente permanece inalterado. Os comentários DEVEM (MUST) usar o mesmo filtro e o mesmo DTO público dos comentários do Gerente. Os contratos NÃO DEVEM (MUST NOT) retornar chamados de outros solicitantes, comentários internos, eventos operacionais além da projeção do histórico público de status, timeline técnica ou telemetria, nem oferecer comentário, rejeição de solução, Save, atribuição ou outra escrita.

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

### Requirement: Gerente rejeita solução de chamado Resolvido da própria Loja
O Xano DEVE (MUST) oferecer uma operação autenticada específica de rejeição de solução, separada do Save operacional. A operação DEVE (MUST) validar, antes de qualquer escrita, a autorização definida em `autorizacao-perfis`, a justificativa não vazia após trim, o status persistido `Resolvido` e o `ultima_atualizacao_em` informado. Ao confirmar, o Xano DEVE (MUST) registrar a justificativa como comentário público com o Gerente autenticado como autor, alterar o status para `Solução Rejeitada`, atualizar `ultima_atualizacao_em` e registrar `alteracao_chamado` com o par `Resolvido` → `Solução Rejeitada`, o autor e a referência ao comentário, sem visibilidade. A operação NÃO DEVE (MUST NOT) alterar responsável, prioridade, Categoria, SLA aplicado ou outros dados funcionais, nem criar status diferente dos canônicos vigentes. Autor, status, visibilidade e timestamps DEVEM (MUST) ser definidos pelo Xano.

#### Scenario: Rejeição válida
- **WHEN** o Gerente da Loja rejeita, com justificativa não vazia e `ultima_atualizacao_em` atual, chamado `Resolvido`
- **THEN** o chamado passa a `Solução Rejeitada`, a justificativa aparece como comentário público do Gerente e a transição aparece no histórico público de status

#### Scenario: Chamado automático da própria Loja
- **WHEN** o chamado `Resolvido` foi criado pelo Bot de Fiscalização para Totem da Loja do Gerente
- **THEN** a rejeição é aceita nas mesmas condições

#### Scenario: Justificativa ausente ou vazia
- **WHEN** a justificativa está ausente, vazia ou contém somente espaços
- **THEN** o Xano rejeita a operação como entrada inválida sem alterar status, criar interação ou atualizar `ultima_atualizacao_em`

#### Scenario: Status diferente de Resolvido
- **WHEN** o status persistido é diferente de `Resolvido`, inclusive `Encerrado` ou `Cancelado`
- **THEN** o Xano rejeita a operação como conflito sem nenhuma escrita

#### Scenario: Detalhe desatualizado
- **WHEN** o `ultima_atualizacao_em` informado difere do persistido
- **THEN** o Xano rejeita a operação como conflito sem nenhuma escrita

#### Scenario: Dados funcionais preservados
- **WHEN** a rejeição é concluída
- **THEN** responsável, prioridade, Categoria e SLA aplicado permanecem inalterados

#### Scenario: Cliente informa campos sob autoridade do Xano
- **WHEN** o cliente envia autor, Loja, status, visibilidade ou timestamp funcional
- **THEN** o Xano ignora ou rejeita esses valores e usa somente os definidos pelo backend
