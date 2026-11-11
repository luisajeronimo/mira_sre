# Design

## Context

Estado em `06cc763`: `Solução Rejeitada` integra a lista canônica do Save, das listagens, dos filtros, das preferências e da deduplicação de heartbeat. Não existe operação de rejeição. O Gerente já é autorizado pela Loja em `obter_chamado_gerente_autorizado` e comenta publicamente por `criar_comentario_publico_gerente`. O Save grava `alteracao_chamado` com `alteracoes.status = {anterior, resultante}` e `comentario_interacao_id`.

## Goals / Non-Goals

**Goals:** rejeição específica, auditável e autorizada ao Gerente da Loja, com justificativa obrigatória, sem novas permissões técnicas e sem status novo.

**Non-Goals:** alterar Save, filas, filtros, enum ou schema; rejeição pelo solicitante não Gerente; SLA; encerramento.

## Decisions

### D1. Contrato

`POST /gerente/chamados/{chamados_id}/rejeitar-solucao` (nome final no Apply) com entrada `justificativa` e `ultima_atualizacao_em` do detalhe confirmado. Identidade de `$auth.id`; autor, status, visibilidade e timestamps definidos pelo Xano.

Ordem de validação, antes de qualquer escrita: autenticação e troca de senha (via `exigir_perfil` com Gerente); chamado e Loja (`obter_chamado_gerente_autorizado`: 404 inexistente, 403 outra Loja ou Gerente sem Loja); justificativa não vazia após trim (422); status persistido `Resolvido` (409, inclusive `Encerrado` e `Cancelado`); `ultima_atualizacao_em` igual ao persistido (409).

### D2. Escritas

Dentro de `db.transaction`, após releitura do chamado e revalidação de Loja, status e `ultima_atualizacao_em`:

1. `db.add interacoes_chamado` comentário: `tipo_evento = comentario`, `visibilidade = publica`, `mensagem = justificativa`, autor Gerente, `criado_em = instante`.
2. `db.patch chamados`: `status = "Solução Rejeitada"`, `ultima_atualizacao_em = instante`; demais campos inalterados.
3. `db.add interacoes_chamado` evento: `tipo_evento = alteracao_chamado`, `alteracoes = {status: {anterior: "Resolvido", resultante: "Solução Rejeitada"}, comentario_interacao_id}`, autor Gerente, `criado_em = instante`, sem `visibilidade`.

O formato de 3 é o mesmo do Save; por H-1 a transição aparece no histórico público, e a linha do tempo de status usada pelo SLA permanece consistente.

### D3. Consistência

O risco é o mesmo do Save atual: a documentação oficial do Xano diverge sobre rollback após falha de função que não é operação de banco. A prova E0.3 em runtime foi **bloqueada por restrição de plano**: a API rejeitou a publicação de `workflow_test` com `Please upgrade to access workflow tests`. Em 2026-11-08, a responsável aceitou formalmente essa limitação funcional para prosseguir no plano Free sem prova de rollback; o pacote recebeu validação estática via MCP e testes locais, registrados em [prova-e03/README.md](./prova-e03/README.md). A atomicidade de D2 permanece não comprovada em runtime. Uma rejeição simultânea a um Save ou ao encerramento sob comando é decidida pela revalidação de status e `ultima_atualizacao_em`; a janela residual de concorrência permanece registrada.

### D4. Reflex

Ação "Rejeitar solução" no detalhe do Gerente somente quando `status == Resolvido`; campo de justificativa obrigatório; envio de `justificativa` e `ultima_atualizacao_em`; carregamento sem envio duplicado; sucesso somente com o detalhe retornado; em erro preserva a justificativa; em 409 informa e recarrega. Reutiliza `app/components/visual.py`. Não altera os demais controles do detalhe.

## Risks / Trade-offs

- [Transação não comprovada] → prova E0.3 bloqueada pelo plano Free; limitação aceita em 2026-11-08, sem afirmar rollback em runtime.
- [Corrida com Save ou encerramento automático] → revalidação e controle otimista; limitação registrada.
- [Divergência com o domínio] → resolvida por DR2-1; docs de domínio atualizados.
- [Save ainda define `Solução Rejeitada`] → mantido por DR2-2; a rejeição não é o único caminho para esse status.

## Migration Plan

Sem schema e sem migração da funcionalidade. Ordem após a aceitação formal da limitação E0.3: função e endpoint com testes XanoScript validados no MCP → dry-run e push seletivo aprovados → Reflex → validação integrada. O pacote temporário da prova não foi publicado porque `workflow_test` exige plano pago; o bloqueio e o [plano de execução e rollback](./prova-e03/plano-execucao-rollback.md) permanecem como evidência. Reversão da funcionalidade: ocultar a ação e desativar o endpoint; registros gravados permanecem.
