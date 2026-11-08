# Design

## Context

Ver [proposal.md](./proposal.md) para motivação, decisões aprovadas e escopo. Os requisitos delta estão em `specs/`.

Estado atual verificado na branch `explore-monitoramento-xano` após `8df737a`:

- **Status:** `chamados.status` é `text` sem enum; as listas canônicas estão repetidas em `validar_save_tratativa_chamado.xs`, `listar_chamados_gerente.xs`, `listar_chamados_tecnico.xs`, `salvar_preferencia_filtros_gerente.xs`, `salvar_preferencia_fila_tecnica.xs`, `assumir_chamado_tecnico.xs`, `verificar_falhas_GET.xs` (deduplicação de heartbeat) e, no Reflex, em `app/chamados/shared.py` (`_STATUS_ATRIBUICAO_PERMITIDA`), `app/chamados/gerente/state.py` (`status_filtros`) e `app/chamados/tecnico/state.py`. `Reaberto` não aparece em nenhum desses pontos.
- **Histórico:** `interacoes_chamado` possui `tipo_evento` ∈ {`comentario`, `atribuicao`, `reatribuicao`, `liberacao`, `alteracao_chamado`}, `alteracoes` (json), `visibilidade` ∈ {`publica`, `interna`}, `mensagem`, `criado_em`, `usuarios_id`. O Save grava um único evento `alteracao_chamado` **interno** com os pares anterior/resultante, inclusive de status. A criação de chamado (manual e heartbeat) não grava evento de status. `assumir_chamado_tecnico` não altera status. Não existe job de encerramento automático.
- **Leitura pública:** `listar_comentarios_publicos_gerente` filtra `visibilidade = publica` e `mensagem` não vazia. `obter_chamado_tecnico` (timeline completa) exige Técnico, Diretoria ou Administrador.
- **Exposição privada:** `interacoes_chamado_GET.xs` filtra o Gerente apenas por `ativo.lojas_id`; `interacoes_chamado_id_GET.xs` usa `exigir_escopo_loja`. Nenhum dos dois filtra visibilidade. Nenhum código Reflex, Simulator ou Fiscal consome esses endpoints. `chamados_GET.xs`/`chamados_id_GET.xs` genéricos retornam o registro de chamado (sem interações) no escopo da Loja.
- **Transação:** `db.transaction { stack { ... } }` já é usado em `validar_save_tratativa_chamado`, `criar_comentario_publico_gerente`, `criar_comentario_operacional`, `assumir_chamado_tecnico`, `verificar_falhas_GET` e `primeiro_acesso_trocar_senha_POST`, no workspace Free.

## Goals / Non-Goals

**Goals:**

- Operação de rejeição autorizada a Gerente da Loja ou solicitante associado, com justificativa validada e reabertura `Resolvido` → `Reaberto`.
- `Reaberto` integrado a todas as listas de status, filas, filtros, atribuição e deduplicação.
- Histórico público de status gravado a partir desta change, distinto de comentários e da auditoria privada.
- Bloqueio no backend da leitura de interações privadas pelo Gerente em qualquer contrato.
- Reflex do Gerente com rejeição, histórico público e confirmação de publicação.

**Non-Goals:**

- Cálculo ou exibição de consumo de SLA (a regra é documentada, a contagem não existe hoje).
- Job de encerramento automático e aceitação explícita da solução.
- Backfill de eventos públicos, projeção da auditoria interna ou migração de `Solução Rejeitada`.
- Alterar o escopo dos GETs genéricos para Técnico, Diretoria ou Administrador.
- Publicação de comentário pela interface própria do solicitante.
- Ampliar o acesso do solicitante a chamados aos quais não está associado.

## Decisions

### D1. Rejeição é uma operação funcional própria

Contrato autenticado específico no grupo `MIRA Service Desk`, separado do Save e único para as interfaces do Gerente e do solicitante. Caminho sugerido: `POST /chamados/{chamados_id}/rejeitar-solucao`, fora do prefixo `/gerente/` porque o solicitante autorizado pelo vínculo pode não ser Gerente da Loja do chamado; o nome final é confirmado no Apply sem alterar o comportamento. Entrada mínima: `chamados_id`, `justificativa` e `ultima_atualizacao_em` do detalhe confirmado. A identidade vem de `$auth.id`; autor, status, visibilidade e timestamps são definidos pelo Xano.

A função valida, nesta ordem e antes de qualquer escrita: identidade e troca de senha pendente; existência do chamado (404); autorização (D2, 403); justificativa não vazia após trim (422); status persistido igual a `Resolvido` (409); `ultima_atualizacao_em` igual ao persistido (409).

**Alternativas rejeitadas:** reutilizar o Save (permitiria à equipe rejeitar em nome do solicitante e mistura papéis); compor comentário + mudança de status em duas chamadas do Reflex (sem consistência).

### D2. Autorização por Loja do Gerente ou por vínculo de solicitante

Autorizado se, e somente se:

- o usuário autenticado tem perfil `gerente`, possui Loja e `ativo.lojas_id` do chamado é igual à Loja dele; **ou**
- `chamados.solicitante_id` não é nulo e é igual a `$auth.id`.

Nenhum outro perfil é autorizado por papel. Chamado automático (sem solicitante humano) é rejeitável somente pelo Gerente da Loja. A condição do solicitante não consulta a Loja atual do usuário: um solicitante transferido de Loja continua autorizado pelo vínculo, e um usuário sem vínculo não ganha autorização por pertencer à Loja do chamado, salvo se for Gerente dessa Loja. A função não reutiliza `obter_chamado_gerente_autorizado` como está, porque ele exige perfil Gerente e Loja; ela consulta o chamado com o Totem e aplica a regra acima. Identificadores enviados pelo cliente não participam da decisão.

### D3. Unidade de escrita da rejeição

Dentro de um único `db.transaction`:

**Revalidação (somente leituras):**

1. Reler o chamado com o Totem (`ativos_referencia`) e reler a identidade autenticada.
2. Revalidar a autorização de D2 com os dados atuais do chamado (`ativo.lojas_id`, `solicitante_id`) e a identidade atual; não depender somente da autorização feita antes da transação.
3. Revalidar `status == "Resolvido"`.
4. Revalidar `ultima_atualizacao_em` igual ao informado.

**Escritas (exatamente quatro):**

5. `db.patch chamados` com `status = "Reaberto"` e `ultima_atualizacao_em = instante`, sem tocar responsável, prioridade, categoria ou SLA.
6. `db.add interacoes_chamado` com `tipo_evento = comentario`, `visibilidade = publica`, `mensagem = justificativa`, `usuarios_id = $auth.id`, `criado_em = instante`.
7. `db.add interacoes_chamado` com `tipo_evento = alteracao_status`, `visibilidade = publica`, `alteracoes = {status: {anterior: "Resolvido", resultante: "Reaberto"}}`, `mensagem = null`, `usuarios_id = $auth.id`, `criado_em = instante`.
8. `db.add interacoes_chamado` com `tipo_evento = alteracao_chamado`, `visibilidade = interna`, `alteracoes` com o par de status e a referência `comentario_interacao_id`, `usuarios_id = $auth.id`, `criado_em = instante`.

As leituras de confirmação após cada escrita (padrão de `validar_save_tratativa_chamado`) não são escritas. A ordem das quatro escritas é a aprovada e não deve ser alterada no Apply sem nova decisão.

**Garantia de consistência — gate E0.3 obrigatório:** o projeto **não** assume que `precondition`, `throw` ou erro tratado dentro de `db.transaction` desfazem escritas anteriores (mesma ressalva registrada em `2026-10-04-monitoramento-heartbeat-incidentes-automaticos`). Antes de implementar a rejeição, e antes de ampliar o Save com o evento público, o Apply deve consultar a documentação oficial do Xano e o Xano Developer MCP e registrar separadamente:

- **comportamento documentado:** o que a documentação oficial afirma sobre rollback de `db.transaction` diante de erro, `precondition` e `throw`, e sobre disponibilidade no plano Free;
- **comportamento observado:** o que o parser/MCP e os testes efetivamente demonstraram;
- **hipótese:** o que não foi demonstrado.

Se o rollback não puder ser confirmado, o Apply é interrompido e alternativas são apresentadas à responsável, sem reordenar escritas por iniciativa própria. Em qualquer caso, não há prova de isolamento: o parser rejeitou a propriedade `isolation`, e duas requisições exatamente simultâneas podem permanecer sujeitas à ordem de gravação do Xano. A revalidação dentro da transação reduz, mas não elimina, a janela de corrida. Não se declara atomicidade garantida sem evidência.

### D4. `Reaberto` substitui `Solução Rejeitada`

Lista canônica de destino e leitura: `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido`, `Reaberto`, `Encerrado`, `Cancelado`.

- `Reaberto` só é alcançado pela operação de rejeição. O Save rejeita `Reaberto` e `Solução Rejeitada` como destino.
- `Reaberto` é não terminal: Save pode alterá-lo para qualquer destino permitido; atribuição permitida; bloqueia deduplicação de heartbeat.
- `Solução Rejeitada` passa a ser **legado de leitura**: continua aceito como status persistido atual (o Save pode retirar o chamado desse estado), em filtros de lista e preferências, e na deduplicação, enquanto existirem registros com esse valor. Não é destino de nenhum fluxo. Nenhum dado é migrado.
- A regra de SLA de retomada passa a valer para `Reaberto`; a contagem não está implementada e permanece fora do escopo.

### D5. Evento público de status com `tipo_evento = alteracao_status`

Valor aditivo no enum `interacoes_chamado.tipo_evento`. Registro sempre `visibilidade = publica`, `mensagem = null`, `alteracoes = {status: {anterior, resultante}}` e nada mais. É gravado:

- pelo Save, na mesma transação, quando houver diferença efetiva de status, além do evento interno `alteracao_chamado` existente;
- pela rejeição (D3).

A criação de chamado não gera evento; o estado inicial é apresentado a partir do próprio chamado. Fluxos futuros que alterem status (por exemplo, encerramento automático) deverão gravar o mesmo evento por suas próprias changes.

**Alternativa rejeitada:** reutilizar `alteracao_chamado` com visibilidade pública (mistura auditoria e evento público no mesmo tipo).

**Consequência na timeline técnica:** `obter_chamado_tecnico` retorna todas as interações, então cada mudança de status passa a aparecer também como `alteracao_status`. O Reflex técnico deve apresentá-lo sem duplicar a leitura do evento interno; o detalhe é tratado na task correspondente.

### D6. Consulta do histórico público pelo Gerente

Novo contrato de leitura, separado da consulta de comentários (caminho sugerido `GET /gerente/chamados/{chamados_id}/historico-status`), autorizado como o detalhe do Gerente. Filtra `tipo_evento = alteracao_status` e `visibilidade = publica`, ordena por `criado_em` decrescente e retorna somente `id`, `status_anterior`, `status_resultante`, `criado_em` e `autor`. Não retorna `alteracoes` bruto, `usuarios_id`, e-mail nem dados de auditoria.

**Autor do evento:** o Xano projeta `autor = {nome, perfil}` a partir de `usuarios.nome` e `usuarios.role`, com `perfil` traduzido para o rótulo oficial (`Gerente`, `Técnico`, `Diretoria`, `Administrador`). Evento gravado sem usuário (`usuarios_id` nulo), reservado a fluxos automáticos, retorna `autor = {nome: "Sistema", perfil: null}`. Usuário existente sem perfil reconhecido (`role` nulo ou fora dos quatro valores oficiais) retorna `autor = {nome, perfil: null}` e não é classificado como `Sistema`. Evento com `usuarios_id` preenchido cujo usuário não seja encontrado retorna `autor = null`, sem ser rotulado como `Sistema` e sem inferir autoria. Hoje nenhum fluxo automático altera status (não há job de encerramento automático); a regra de `Sistema` vale para fluxos automáticos futuros e é verificada por teste com evento sem usuário. O DTO de comentários públicos permanece com `autor.nome` apenas. A consulta de comentários públicos passa a filtrar explicitamente `tipo_evento` nulo ou `comentario`, para que eventos públicos nunca apareçam como comentário.

Histórico anterior: transições gravadas antes desta change existem somente na auditoria interna ou não foram gravadas; não são exibidas. A interface informa que o histórico de status começa a partir da implantação.

### D7. GETs genéricos de interações negam o Gerente

`interacoes_chamado_GET.xs` e `interacoes_chamado_id_GET.xs` deixam de aceitar o perfil Gerente (403), preservando o comportamento atual dos demais perfis. Negar é preferido a filtrar porque nenhum consumidor usa esses endpoints e os contratos funcionais já cobrem a leitura pública; filtrar manteria uma segunda superfície de leitura sem DTO sanitizado. `chamados_GET`/`chamados_id_GET` genéricos não retornam interações e não são alterados.

### D8. Consulta própria do solicitante

Novos contratos de leitura autorizados exclusivamente por `chamados.solicitante_id == $auth.id`, sem consultar a Loja atual do usuário nem o perfil:

- lista dos chamados em que o usuário é solicitante (caminho sugerido `GET /solicitante/chamados`), ordenada por `ultima_atualizacao_em` decrescente, sem filtros, sem preferências salvas e sem paginação nesta Sprint (limitação de escopo aprovada);
- detalhe desse chamado (`GET /solicitante/chamados/{chamados_id}`), com os mesmos campos funcionais do detalhe do Gerente, exceto `resumo_totem`, que é sempre `null`: o solicitante não recebe telemetria do Totem, inclusive quando transferido de Loja. O detalhe do Gerente não muda;
- comentários públicos e histórico público desse chamado, com os mesmos DTOs e filtros de visibilidade dos contratos do Gerente.

Chamado sem vínculo responde 403 e inexistente 404, sem expor dados. Os contratos não oferecem comentário, Save, atribuição nem timeline técnica. A rejeição usa o contrato único de D1. Nomes finais confirmados no Apply.

**Alternativa rejeitada:** ampliar `obter_chamado_gerente_autorizado` com o vínculo de solicitante. Misturaria as duas regras de escopo num contrato cujo nome e testes assumem escopo por Loja.

### D9. Reflex

- Detalhe do Gerente: ação "Rejeitar solução" visível quando `status == Resolvido` (todo detalhe carregado pelo contrato do Gerente já é da Loja).
- Interface própria do solicitante nas rotas `/chamados/solicitados` (lista) e `/chamados/solicitados/[chamado_id]` (detalhe), com comentários públicos, histórico público e a mesma ação de rejeição, sem botão Detalhe do Totem nem drawer de telemetria. Item de menu "Chamados solicitados" visível a todos os perfis oficiais; usuário sem chamados associados vê lista vazia. A visibilidade do item não concede autorização: o backend valida o vínculo em cada contrato. Para o solicitante que é Gerente da Loja do chamado, as duas interfaces levam ao mesmo contrato de rejeição.
- Histórico público com nome e perfil do autor, nome sem perfil quando o perfil não é reconhecido, `Sistema` para evento automático ou autor não informado quando `autor` for nulo.
- Na ação de rejeição de ambas as interfaces: Exige justificativa não vazia; envia `ultima_atualizacao_em` do detalhe; atualiza o detalhe somente com o resultado do Xano; em erro preserva a justificativa e não simula transição; em 409 informa e recarrega.
- Histórico público de status em seção própria, distinta dos comentários, com estados de carregamento, vazio e erro, e aviso de que eventos anteriores à implantação não são exibidos.
- Publicação de comentário: POST e GET posterior em tratamentos separados (o fluxo atual em `publicar_comentario` usa o mesmo `try`).
- Listas de status do Gerente e do Técnico incluem `Reaberto`; o Save técnico não oferece `Reaberto` nem `Solução Rejeitada` como destino.

## Risks / Trade-offs

- **[Corrida entre rejeição e Save]** → revalidação de autorização, status e `ultima_atualizacao_em` dentro da transação; limitação de isolamento registrada (D3).
- **[Rollback não confirmado]** → gate E0.3 obrigatório; sem confirmação, o Apply para e alternativas são apresentadas para decisão. Sem fault injection no único workspace.
- **[Save existente já usa `precondition` após escritas]** → o resultado de E0.3 vale também para o Save atual; divergência encontrada é reportada, sem correção fora do escopo aprovado.
- **[Reflex antigo rejeita tipo de evento desconhecido]** → `TIPOS_EVENTO_TIMELINE` em `app/services/service_desk.py` gera `XanoContratoInvalido` para tipo novo; o Reflex compatível deve estar na `main` antes de publicar qualquer alteração Xano que grave `alteracao_status`.
- **[Mensagem de conflito fixa no cliente]** → `app/services/xano.py` mapeia todo 409 para mensagem de atribuição; a rejeição trata `XanoConflito` com mensagem própria no State.
- **[Continuidade do SLA]** → não há cálculo de SLA implementado; a regra de retomada em `Reaberto` é documental. Eventos `alteracao_status` gravados a partir desta change fornecem marcos futuros; chamados anteriores e o legado `Solução Rejeitada` não têm histórico confiável. Limitação registrada para change futura de SLA.
- **[Mudança de enum em tabela com dados]** → valor aditivo; nenhum registro existente é alterado; exige dry-run e aprovação antes do push.
- **[Histórico incompleto para chamados antigos]** → limitação explícita na spec e na UI.
- **[Duplicidade visual na timeline técnica]** → task de apresentação no Reflex técnico.
- **[Registros legados `Solução Rejeitada`]** → aceitos em leitura e saída por Save; não são migrados.
- **[Solicitante transferido de Loja]** → contratos e interface próprios autorizados pelo vínculo (D8), sem depender da Loja atual.
- **[Exposição de identidade no histórico]** → somente nome e rótulo de perfil; sem e-mail, IDs ou Loja do autor.
- **[Telemetria para solicitante transferido]** → `resumo_totem = null` no detalhe do solicitante e sem drawer.

## Migration Plan

Plano de execução do Apply, em ordem de dependência. Os pushes Xano são divididos em dois lotes: o primeiro não grava `alteracao_status`; o segundo só ocorre depois que o Reflex compatível estiver na `main`.

| # | Etapa | Depende de | Aprovação humana |
|---|---|---|---|
| 1 | Aprovar o início do Apply | — | sim |
| 2 | **E0.3** — validar `db.transaction`, rollback diante de erro/`precondition`/`throw`, alteração aditiva do enum e plano Free, registrando documentado, observado e hipótese | 1 | sim, se o rollback não for confirmado (parar e apresentar alternativas) |
| 3 | **E1** — negar Gerente nos GETs genéricos de `interacoes_chamado` (5.1, 5.2) | 2 | — |
| 4 | **E2** — Reflex compatível: `alteracao_status` aceito na timeline, `Reaberto` nas listas, destinos do Save sem `Reaberto`/`Solução Rejeitada` (6.5, 6.6) | 1 | — |
| 5 | **E3** — `Reaberto` nas listas XanoScript (2.1–2.3) | 2 | — |
| 6 | **E4** — enum `alteracao_status` (3.1) | 2 | sim (diff de schema) |
| 7 | Push Xano 1 (E1 + E3 + E4), com validação XanoScript, dry-run e revisão do diff; nenhum fluxo grava `alteracao_status` | 3, 5, 6 | sim (push) |
| 8 | Merge do Reflex compatível (E2) na `main` | 4 | sim (merge) |
| 9 | **E5** — Save grava evento público (3.2) | 2 confirmado, 7, 8 | — |
| 10 | **E6** — leitura pública e histórico do Gerente (3.3, 3.4) | 7 | — |
| 11 | **E7** — rejeição (4.1–4.3) | 2 confirmado, 10 | — |
| 12 | **E8** — contratos do solicitante (4A.1) | 10 | — |
| 13 | Push Xano 2 (E5–E8), com validação, dry-run e revisão | 8, 9–12 | sim (push) |
| 14 | **E9** — Reflex funcional (6.1–6.4, 6.3A) | 13 | — |
| 15 | **E10** — validação integrada e classificação dos resultados (7.0–7.3) | 14 | sim (aceitar limitações) |
| 16 | **E11** — conferência documental (8.1) | 15 | — |
| 17 | Revisão independente e Archive (8.2) | 16 | sim |

Após cada push, novo dry-run sem diferenças não aprovadas. Sem backfill e sem migração de `Solução Rejeitada`. Reversão: ocultar ações no Reflex e desativar os contratos novos; não excluir interações nem o valor de enum já gravados.

## Bloqueios de revisão humana

- Aprovação formal do Apply.
- Gate E0.3: sem confirmação de rollback, interromper e decidir alternativas.
- `alteracao_status` está aprovado conceitualmente; nesta etapa é somente decisão documental. Nenhuma alteração de schema, dado ou workspace Xano é feita antes do Apply aprovado, e cada push exige aprovação do diff e do dry-run.
- Merge do Reflex compatível na `main` antes do push que grava `alteracao_status`.
