# Proposal

## Why

Cartão da Sprint 3 "Acompanhamento e retorno do solicitante" (estado informado: parcial; referência de planejamento `acompanhamento-solicitante-rejeicao-solucao`). O cartão exige que o Gerente rejeite uma solução com justificativa obrigatória, sem receber permissões técnicas.

Relação com as demais changes:

- O acompanhamento já está implementado e consolidado (lista, detalhe e comentários públicos do Gerente pela Loja, inclusive em terminal) ou em proposta em `acompanhamento-solicitante-historico-status` (histórico público projetado de `alteracao_chamado`, consulta do solicitante, GETs genéricos).
- A versão anterior da rejeição (com `Reaberto` e evento `alteracao_status`) está preservada, inativa, no histórico Git (commit `1f27556`, pasta `acompanhamento-solicitante-historico-status/referencias/rejeicao-solucao-versao-anterior/`, removida da árvore em 2026-11-08 para não duplicar specs superadas; ex.: `git show 1f27556:openspec/changes/acompanhamento-solicitante-historico-status/referencias/rejeicao-solucao-versao-anterior/README.md`). Esta change não a restaura.
- Os efeitos da rejeição sobre o SLA pertencem a `sla-resolucao-encerramento`.

## What Changes

- Operação autenticada específica de rejeição, separada do Save, autorizada somente ao Gerente da Loja à qual o chamado pertence (inclusive chamado automático).
- Somente chamado em `Resolvido`; resultado `Solução Rejeitada`, status canônico existente. Nenhum status novo.
- Justificativa obrigatória, não vazia após trim, validada no Xano e registrada como comentário público com o Gerente como autor.
- Registro de `alteracao_chamado` com o par `Resolvido → Solução Rejeitada` e o autor, sem visibilidade, no mesmo formato do Save; por H-1, a transição passa a constar do histórico público sem nova gravação de tipo próprio.
- Controle otimista por `ultima_atualizacao_em` e revalidação antes das escritas.
- Ação "Rejeitar solução" no detalhe do Gerente somente em `Resolvido`.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-acompanhamento-gerente`: operação de rejeição de solução pelo Gerente.
- `autorizacao-perfis`: autorização específica da rejeição.
- `frontend-chamados-gerente`: ação de rejeição no detalhe do Gerente.

## Impact

- Xano: nova função e endpoint de rejeição; nenhuma alteração de schema, enum, Save, filas, filtros, preferências ou deduplicação (`Solução Rejeitada` já é canônico em todos).
- Reflex: cliente, State e componente de rejeição no detalhe do Gerente.
- Escrita: três gravações (comentário público, chamado, `alteracao_chamado`), que dependem de atomicidade.
- Documentos de domínio: a regra que atribuía a rejeição ao solicitante é substituída por DR2-1.

## Fora do escopo

- `Reaberto`; evento `alteracao_status`; rejeição pelo solicitante; aceitação explícita; cálculo de SLA; encerramento automático.

## Decisões aprovadas (2026-11-04)

| ID | Decisão | Efeito |
|---|---|---|
| DR2-0 | Rejeição incluída na Sprint 3, condicionada à segurança | Substitui o adiamento aprovado na revisão de escopo; esta change entra no plano da Sprint |
| DT-1 | Prova E0.3 obrigatória antes de novas escritas que dependam de atomicidade | As tasks de escrita ficam bloqueadas até a prova e a aprovação do relatório; a revisão de 2026-11-08 autorizou a prova em datasource próprio de teste no workspace `152692`, branch `v1`, sem alterar o datasource ativo nem dados reais |
| DR2-1 | Somente o Gerente da própria Loja rejeita; o solicitante permanece somente leitura | Resolve a divergência com o domínio, que atribuía a rejeição ao solicitante |
| DR2-2 | `Solução Rejeitada` permanece canônico | Destino da rejeição; o Save continua aceitando esse destino, sem alteração nesta change |
| K-B | Histórico exibido na interface após validação | A transição da rejeição aparece no histórico do Gerente quando a seção for liberada em `acompanhamento-solicitante-historico-status` |

## Bloqueios

- **Histórico do gate E0.3:** não havia workspace separado. A responsável autorizou um datasource de teste no `v1` como alternativa, ciente de que os registros ficam separados mas o schema e os recursos publicados são compartilhados. A API do Xano bloqueou `workflow_test` no plano Free; a responsável aceitou essa limitação em 08/11/2026 e autorizou prosseguir. O endpoint foi publicado e testado em HTTP nos cenários registrados em `tasks.md`; rollback em runtime não foi comprovado. O plano está em [prova-e03/plano-execucao-rollback.md](./prova-e03/plano-execucao-rollback.md).
- **Encerramento do Apply em 11/11/2026:** a responsável dispensou a matriz XanoScript exaustiva restante. Os testes já executados permanecem válidos, sem declaração de que os cenários omitidos passaram.
