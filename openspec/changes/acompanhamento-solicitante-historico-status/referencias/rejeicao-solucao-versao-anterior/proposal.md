# Proposal

## Why

A tarefa da Sprint 3 "Acompanhamento e retorno do solicitante" exige que o Gerente acompanhe o ciclo de vida completo dos chamados da própria Loja, comente sem acessar conteúdo privado e rejeite uma solução com justificativa obrigatória, sem receber permissões técnicas.

A inspeção da versão atual (após `8df737a`) mostrou que:

- não existe operação de rejeição de solução no Xano nem no Reflex;
- a rejeição estava restrita ao solicitante na versão anterior desta change, o que diverge do requisito oficial;
- o status `Reaberto` não existe no domínio, nas specs, no Xano nem no Reflex;
- as transições de status só são gravadas como auditoria interna (`tipo_evento = alteracao_chamado`, `visibilidade = interna`) pelo Save operacional; não há histórico público de status;
- `GET /interacoes_chamado` e `GET /interacoes_chamado/{id}` (grupo genérico `APIS from table interacoes_chamado`) autorizam o Gerente apenas pelo vínculo com a Loja, sem filtrar visibilidade, e retornam comentários internos e eventos de auditoria por acesso direto;
- a publicação de comentário do Gerente trata POST e a consulta posterior do detalhe no mesmo bloco de erro.

## What Changes

- **Rejeição de solução:** nova operação funcional específica no Xano, separada do Save operacional. Podem rejeitar: o Gerente da Loja à qual o chamado pertence (inclusive chamado automático sem solicitante humano) e o solicitante humano associado ao chamado. Técnico, Diretoria e Administrador não recebem essa permissão por perfil.
- **Justificativa obrigatória:** não vazia após trim, validada no Xano e registrada como comentário público associado ao chamado e ao usuário autenticado.
- **Reabertura automática:** a rejeição executa `Resolvido` → `Reaberto` e registra, na mesma unidade de escrita, comentário público com a justificativa, evento público de transição de status, evento de auditoria privado, novo status e `ultima_atualizacao_em`.
- **`Reaberto` substitui `Solução Rejeitada`** como status canônico resultante da rejeição. `Reaberto` é não terminal, integra filas, filtros, atribuição, deduplicação de heartbeat e herda a regra de SLA antes atribuída a `Solução Rejeitada`. O Save operacional não pode definir `Reaberto` nem `Solução Rejeitada` como destino. `Solução Rejeitada` permanece aceito somente como valor persistido legado (leitura, filtro e saída por Save), sem migração de dados.
- **Histórico público de status:** toda transição efetiva de status feita a partir desta change (Save operacional e rejeição) passa a gravar um evento público estruturado, distinto do comentário público e da auditoria privada. O Gerente consulta esse histórico por contrato próprio. Transições anteriores não são reconstruídas.
- **Acesso próprio do solicitante:** o solicitante humano associado consulta, por contratos e interface próprios, somente os chamados aos quais está associado, independentemente de sua Loja atual, com detalhe, comentários públicos, histórico público e a ação de rejeição. A autorização é validada no Xano pelo vínculo `solicitante_id`.
- **Autor no histórico público:** cada evento público de status exibe o nome de exibição e o perfil do autor humano, ou `Sistema` para evento automático, sem e-mail, identificadores internos ou dados de auditoria.
- **Novo valor de `tipo_evento`:** `alteracao_status`, aditivo em `interacoes_chamado.tipo_evento`, para o evento público de transição. Nesta etapa é somente decisão documental: nenhum schema, dado ou workspace Xano é alterado; a implementação depende da aprovação formal do Apply.
- **Segurança de interações privadas:** os GETs genéricos de `interacoes_chamado` deixam de atender o Gerente; o Gerente lê interações exclusivamente pelos contratos funcionais que filtram conteúdo público.
- **Reflex do Gerente:** ação de rejeitar no detalhe `Resolvido`, histórico público de status separado dos comentários, comentário público também em chamado terminal (já implementado) e confirmação de publicação independente da atualização posterior do detalhe.
- **Documentos de domínio:** `docs/project-overview.md` e `docs/domain-model.md` alinhados a essas regras nesta mesma change.

## Capabilities

### New Capabilities

Nenhuma. A mudança estende capacidades existentes.

### Modified Capabilities

- `chamados-acompanhamento-gerente`: rejeição de solução com reabertura; histórico público de status com autor; consulta própria do solicitante; separação entre comentários públicos e eventos públicos; correção do título do requisito de comentário.
- `autorizacao-perfis`: autorização da rejeição por Loja do Gerente ou vínculo de solicitante, independente da Loja atual do solicitante; consulta do solicitante restrita aos chamados associados; proibição de leitura de interações privadas por CRUD genérico.
- `tratativa-operacional-chamados`: lista canônica com `Reaberto` no lugar de `Solução Rejeitada`; Save não define `Reaberto`/`Solução Rejeitada`; Save grava evento público de transição.
- `chamados-fila-atribuicao-tecnica`: `Reaberto` como status não terminal em fila, filtros, preferências e atribuição; tratamento do legado `Solução Rejeitada`.
- `monitoramento-disponibilidade-totens`: `Reaberto` integra a deduplicação de incidentes vigentes.
- `frontend-chamados-gerente`: rejeição, histórico público com autor, interface própria do solicitante, comentário em terminal e confirmação de publicação.

## Impact

- **Xano (schema):** valor aditivo `alteracao_status` em `interacoes_chamado.tipo_evento`. `chamados.status` é texto livre validado por funções; não há alteração de schema em `chamados`.
- **Xano (funções/APIs):** nova operação de rejeição compartilhada pelas interfaces do Gerente e do solicitante; nova consulta de histórico público do Gerente; novos contratos de consulta do solicitante (lista, detalhe, comentários públicos e histórico público) autorizados pelo vínculo `solicitante_id`; ajustes nas listas de status de `validar_save_tratativa_chamado`, `listar_chamados_gerente`, `listar_chamados_tecnico`, `salvar_preferencia_filtros_gerente`, `salvar_preferencia_fila_tecnica`, `assumir_chamado_tecnico` e `verificar_falhas_GET`; Save passa a gravar evento público; GETs genéricos de `interacoes_chamado` negam Gerente.
- **Reflex:** `app/chamados/gerente/` (State e páginas), nova interface do solicitante em `/chamados/solicitados` e `/chamados/solicitados/[chamado_id]` com item de menu "Chamados solicitados" para todos os perfis oficiais (`app/app.py`, `app/components/navegacao.py`), `app/chamados/shared.py`, `app/chamados/tecnico/state.py` (opções de status) e `app/services/service_desk.py` (cliente e DTOs).
- **Testes:** XanoScript (autorização, rejeição, histórico, GETs genéricos, listas de status) e Python (cliente, State, páginas).
- **Dados:** sem backfill, sem migração de `Solução Rejeitada` e sem eventos retroativos.
- **Limitação de escopo desta Sprint:** a lista do solicitante é ordenada por `ultima_atualizacao_em` decrescente, sem filtros, preferências salvas ou paginação.
- **Fora do escopo:** telemetria do Totem na interface do solicitante (`resumo_totem = null`, sem drawer), publicação de comentário pela interface do solicitante (o solicitante que também é Gerente da Loja continua comentando pela jornada do Gerente), cálculo de SLA (não implementado hoje), job de encerramento automático após três dias em `Resolvido` (não existe hoje), aceitação explícita da solução, dashboards, alteração dos GETs genéricos para Técnico/Diretoria/Administrador, publicação remota no Xano.

## Decisões aprovadas pela responsável

1. Podem rejeitar: Gerente da própria Loja (sem precisar ser o solicitante, inclusive em chamado automático) e solicitante associado. Técnico e Diretoria não recebem a permissão automaticamente. Nenhuma permissão técnica é concedida ao Gerente. A autorização é validada no Xano.
2. Justificativa obrigatória após trim, registrada como comentário público do usuário autenticado e exibida no acompanhamento público, validada no backend.
3. A rejeição executa `Resolvido` → `Reaberto` registrando comentário público, evento público de reabertura, auditoria privada, status e `ultima_atualizacao_em` de forma consistente, sem prometer atomicidade não garantida.
4. O Gerente acompanha o histórico público de status da própria Loja, sem comentários internos nem detalhes de auditoria, distinguindo eventos públicos de comentários públicos.
5. A correção dos GETs genéricos integra esta change.
6. Nome oficial da change: `acompanhamento-solicitante-rejeicao-solucao` (renomeada a partir de `acompanhamento-retorno-solicitante`, sem change concorrente).
7. `docs/project-overview.md` e `docs/domain-model.md` são atualizados nesta change.
8. `Reaberto` substitui `Solução Rejeitada`; `Solução Rejeitada` permanece apenas como legado de leitura, sem migração.
9. O evento público de transição usa novo valor aditivo `alteracao_status` em `tipo_evento`.
10. O histórico público contém somente eventos gravados a partir desta change; não há projeção da auditoria interna nem backfill.
11. Solicitante transferido de Loja mantém a autorização de rejeitar pelo vínculo com o chamado, independentemente da Loja atual; o acesso à rejeição existe por interface própria do solicitante, restrita aos chamados associados, com validação no Xano.
12. O histórico público exibe nome de exibição e perfil do autor humano e `Sistema` para eventos automáticos, sem e-mail, identificadores internos ou dados desnecessários, preservando a separação entre evento público e auditoria privada.
13. A inclusão de `alteracao_status` está aprovada conceitualmente como tipo dos eventos públicos de mudança de status. Nesta etapa nenhuma alteração de schema, dado ou publicação no Xano é executada; a implementação depende da aprovação formal do Apply.
14. (G1) O detalhe na interface do solicitante retorna `resumo_totem = null` e não exibe o drawer de telemetria; o detalhe do Gerente não muda.
15. (G2) Rotas `/chamados/solicitados` e `/chamados/solicitados/[chamado_id]`; item "Chamados solicitados" para todos os perfis oficiais; lista vazia para quem não tem chamados associados; a visibilidade do menu não concede autorização.
16. (G3) Lista do solicitante ordenada por `ultima_atualizacao_em` decrescente, sem filtros, preferências salvas ou paginação nesta Sprint.
17. (G4) Autor humano existente sem perfil reconhecido é apresentado como `{nome, perfil: null}`, nunca como `Sistema`; `autor = null` quando `usuarios_id` está preenchido e o usuário não é encontrado.

## Comportamentos existentes a preservar

- Consulta da lista e do detalhe do Gerente limitada à Loja pela relação persistida chamado → Totem → Loja.
- Comentário do Gerente sempre Público, inclusive em `Encerrado` e `Cancelado`, sem alterar campos funcionais.
- Consulta de comentários públicos com DTO sanitizado (`id`, `conteudo`, `criado_em`, `autor.nome`).
- Save operacional exclusivo de Técnico, Diretoria e Administrador, com comentário obrigatório na mudança de status e auditoria interna `alteracao_chamado`.
- Mutação genérica (`POST`, `PATCH`, `DELETE`) negada por `autorizacao/negar_mutacao_generica`.
- Timeline técnica de `obter_chamado_tecnico` restrita a perfis operacionais.

## Gates antes da implementação

- Aprovação formal do Apply.
- Gate E0.3 do design: confirmação, com evidência, do comportamento de rollback de `db.transaction` no plano Free antes de implementar fluxos que dependam dele; sem confirmação, interromper e decidir alternativas.
- Merge do Reflex compatível com `alteracao_status` na `main` antes de publicar no Xano qualquer alteração que grave esse tipo.
- Aprovação do diff de schema (`alteracao_status`) e do dry-run antes de cada push ao Xano.
