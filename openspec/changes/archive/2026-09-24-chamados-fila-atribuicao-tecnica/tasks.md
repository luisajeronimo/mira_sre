## 1. Preparação e auditoria

- [x] 1.1 Reconfirmar `AGENTS.md`, contexto do projeto, specs consolidadas e ausência de changes arquivadas relevantes fora do histórico, registrando o inventário de contexto.
- [x] 1.2 Auditar localmente todos os consumidores de `chamados.tecnico_id`, `status`, `criado_em`, `origem`, `sla_horas_aplicado` e o novo `atribuido_em` planejado, entregando a matriz de consumidores.
- [x] 1.3 Fazer inventário remoto somente leitura de chamados com `status`, `tecnico_id` e campos novos nulos, sem alterar ou excluir dados, registrando a extração e seus limites.
- [x] 1.4 Registrar snapshot/ponto de recuperação e confirmar no artefato de auditoria que não haverá backfill nem limpeza de chamados legados.
- [x] 1.5 Consultar o Xano Developer MCP sobre `timestamp?`, `db.get`, `db.edit`, `db.transaction`, concorrência e HTTP 409 antes de implementar a assunção, anexando a evidência da sintaxe suportada. A documentação descreve isolamento configurável, mas a sintaxe `isolation = "serializable"` foi rejeitada pelo parser disponível; a forma validada para o plano Free é `db.transaction { stack { ... } }`. `db.direct_query`/Direct Database Access foram descartados por dependerem de política não disponível no plano Free.

## 2. Schema e contratos Xano

- [x] 2.1 Adicionar `atribuido_em` como timestamp opcional em `chamados`, preservando compatibilidade e valores nulos legados, e validar o schema sem backfill.
- [x] 2.2 Criar funções reutilizáveis para autorização exclusiva de Técnico e construção dos DTOs técnicos, sem duplicar regras de autenticação, e cobrir as funções com testes inline.
- [x] 2.3 Implementar `GET /tecnico/chamados` com validação de `visao`, filtro backend para `Novo` e `tecnico_id`, ordenação `id desc` e sem paginação, verificando cada visão com dados controlados.
- [ ] 2.4 Implementar `GET /tecnico/chamados/{chamados_id}` com escopo global do Técnico, formato consolidado, `atribuido_em` e comportamento 404, verificando detalhe autorizado e inexistente.
- [x] 2.5 Implementar `POST /tecnico/chamados/{chamados_id}/assumir` sem payload funcional, derivando `tecnico_id` de `$auth.id` e `atribuido_em` do backend, verificando o DTO atualizado.
- [x] 2.6 Implementar a assunção com `db.get`, validações, `db.edit` e `db.transaction` no plano Free: reler antes da edição, reler após a edição, retornar HTTP 409 para conflito observável e manter idempotência/timestamp do mesmo Técnico. Documentar que simultaneidade exata não possui garantia matemática de um único vencedor no Free.
- [ ] 2.7 Responder HTTP 422 para status nulo/diferente de `Novo`, HTTP 409 para atribuição a outro Técnico e ignorar/rejeitar campos enviados pelo cliente sob autoridade do Xano, cobrindo cada entrada inválida.
- [ ] 2.8 Confirmar 401, 403, 404, 409, 422 e 5xx sem dados protegidos, mutação parcial ou reabertura dos CRUDs genéricos, registrando a matriz HTTP.

## 3. Testes XanoScript e regressão de autorização

- [x] 3.1 Testar Técnico autorizado nas duas visões e confirmar filtro no Xano.
- [ ] 3.2 Testar chamados atribuídos a outro Técnico fora das duas visões principais.
- [ ] 3.3 Testar visão inválida, status nulo, status diferente de `Novo` e chamado inexistente.
- [ ] 3.4 Testar detalhe antes e depois da assunção, chamados manuais, automáticos e legados com nulos preservados.
- [x] 3.5 Testar assunção válida, derivação do usuário autenticado, `status = Novo` e `atribuido_em` definido pelo backend.
- [ ] 3.6 Testar payloads com `tecnico_id`, `status` e `atribuido_em` falsificados sem autoridade.
- [x] 3.7 Testar repetição pelo mesmo Técnico como operação idempotente sem novo timestamp.
- [ ] 3.8 Testar conflito observável entre dois Técnicos com harness/mocks ou teste suportado pelo Xano, comprovando o HTTP 409 quando a atribuição já foi observada; registrar separadamente que uma corrida exatamente simultânea não pode ser declarada como garantia de um único vencedor no plano Free.
- [ ] 3.9 Testar Gerente e Diretoria recebendo 403 e ausência de token recebendo 401.
- [ ] 3.10 Reexecutar testes negativos dos CRUDs genéricos e confirmar que nenhum chamado antigo é alterado.

## 4. Cliente e State Reflex

- [x] 4.1 Adicionar modelos tipados para item técnico, detalhe e respostas de assunção, preservando campos nulos legados.
- [x] 4.2 Adicionar métodos do cliente para as duas visões, detalhe e assunção usando somente `XANO_SERVICE_DESK_BASE_URL` e token backend-only.
- [x] 4.3 Criar State técnico separado da autenticação, com visão selecionada, carregamento, vazio, erro, detalhe e assunção em andamento.
- [x] 4.4 Mapear 401, 403, 404, 409, 422, resposta incompatível, timeout, conexão e 5xx sem expor token ou corpo sensível.

## 5. Jornada Reflex

- [x] 5.1 Transformar `/tecnico` em fila com as visões `Não atribuídos` e `Atribuídos a mim`.
- [x] 5.2 Criar `/tecnico/chamados/{chamado_id}` como detalhe somente leitura, incluindo `atribuido_em` e dados legados não informados.
- [x] 5.3 Exibir `Assumir` somente para chamado `Novo` sem Técnico, sem exigir `atribuido_em` nulo; não exibir controles de tratativa, reatribuição, liberação ou cancelamento.
- [x] 5.4 Após sucesso, atualizar State e refletir o chamado em `Atribuídos a mim` sem alterar o status.
- [x] 5.5 Após 409, informar a concorrência e recarregar lista/detalhe sem sobrescrever dados locais.
- [x] 5.6 Atualizar guards/navegação para Técnico sem alterar a jornada do Gerente ou da Diretoria.

## 6. Verificações e sincronização

- [x] 6.1 Criar testes Python para cliente, DTOs, erros, State, rotas e ausência de ações fora do escopo.
- [x] 6.2 Executar suíte Python completa e compilação Reflex.
- [x] 6.3 Validar todos os XanoScript alterados com o Xano Developer MCP.
- [x] 6.4 Executar `git diff --check` e `openspec validate chamados-fila-atribuicao-tecnica --strict`.
- [x] 6.5 Executar `xano workspace push --dry-run`, apresentar o diff completo e aguardar aprovação humana explícita.
- [x] 6.6 Após aprovação, executar push somente do diff aprovado e validar a jornada técnica sem alterar Simulator, Fiscal, heartbeat ou abertura manual.
- [x] 6.7 Registrar evidências e limitações operacionais; não arquivar sem nova revisão humana.

> Evidência de sincronização: o push real da revisão Free incluiu somente `function/service_desk/assumir_chamado_tecnico.xs`; o dry-run posterior retornou `No changes to push`.
>
> Evidência humana runtime (24/09/2026, confirmação manual da responsável; não observada diretamente pelo agente): autenticação Técnica e `/me` confirmados; as duas visões, detalhe técnico, assunção, atribuição ao usuário autenticado, `atribuido_em` definido pelo backend, status preservado como `Novo`, atualização entre visões, repetição idempotente, encerramento do loading e coerência visual foram confirmados. A confirmação não informou ID do chamado nem status HTTP, portanto esses detalhes não são afirmados aqui.
>
> Evidências remotas anteriores: inventário somente leitura encontrou 17 chamados, IDs 16–32, todos em `Novo` e com `tecnico_id = 0`/`atribuido_em = 0` na extração; origem manual nos IDs 31–32 e nula nos demais. As quatro rotas técnicas retornaram 401 sem token. Não houve backfill, exclusão ou fechamento executado pelo agente. A confirmação humana reporta status `Novo` mantido no chamado usado na assunção.
>
> Limitação de concorrência aceita: a implementação usa apenas recursos do plano Free (`db.get`, validações, `db.edit`, `db.transaction`), sem `db.direct_query` ou recurso pago. Releitura antes/depois e 409 cobrem conflitos observáveis, mas o plano Free não oferece evidência de compare-and-set/isolamento forte que garanta matematicamente um único vencedor em corrida exatamente simultânea. Não foi executada disputa runtime com um segundo Técnico.
>
> Pendências de validação, não de implementação: `2.4` (404 para identificador inexistente); `2.7` e `2.8` (matriz negativa completa de status/campos adulterados e erros); `3.2` (exclusão explícita de chamado de outro Técnico); `3.3` (visão/status inválidos e ID inexistente); `3.4` (matriz de detalhe manual/automático/legado); `3.6` (payloads adulterados); `3.8` (conflito/corrida com segundo Técnico); `3.9` (403 runtime para Gerente/Diretoria; 401 sem token já comprovado); `3.10` (regressão autenticada dos CRUDs genéricos). Esses cenários não foram afirmados como executados. A disputa simultânea permanece não executada por ausência de segunda credencial segura e pela limitação técnica Free já aceita; é uma pendência operacional/documental de validação, não funcionalidade fora da implementação aprovada.
