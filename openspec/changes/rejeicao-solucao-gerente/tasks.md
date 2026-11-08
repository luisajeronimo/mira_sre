# Tasks

## 1. Decisões e gates

- [x] 1.1 DR2-0 aprovada: rejeição na Sprint 3, condicionada à segurança.
- [x] 1.2 DR2-1 aprovada: somente o Gerente da própria Loja rejeita; domínio atualizado.
- [x] 1.3 DR2-2 aprovada: `Solução Rejeitada` permanece canônico; Save inalterado.
- [x] 1.4 DT-1 aprovada: prova E0.3 obrigatória antes das escritas.
- [x] 1.5 K-B aprovada: histórico exibido após validação (em `acompanhamento-solicitante-historico-status`).
- [ ] 1.6 Obter autorização específica de ambiente Xano isolado para a prova E0.3 (nenhum autorizado; único workspace registrado é o compartilhado `152692`). Investigação de 2026-11-05 ([validacao-xano-2026-11.md](../acompanhamento-solicitante-historico-status/validacao-xano-2026-11.md)): `xano sandbox` exige plano pago; `xano ephemeral` cria tenant dentro do workspace compartilhado `152692`, o único da conta. Nenhum ambiente criado; segue bloqueada por ambiente. Rejeição não implementada (DT-1). Pacote de prova preparado em 2026-11-07: [prova-e03/](../rejeicao-solucao-gerente/prova-e03/README.md) (tabela, funções e teste de workflow com a matriz `db.add`, `db.patch`, `function.run`, duas escritas e tipos de erro; concorrência não coberta). Validação estática MCP: 4/4; teste local de coerência: `tests/test_prova_e03_pacote.py`. **Não executado:** runtime, persistência e rollback continuam sem prova. A documentação de testes de workflow cita clonagem do datasource (`datasource = "live"`) e datasources nomeados, sem confirmar a disponibilidade no Free; usar isso exige enviar o pacote a um workspace, o que depende de autorização.
- [ ] 1.7 Executar a prova E0.3 conforme o plano de `acompanhamento-solicitante-historico-status/design.md` D6 e obter aprovação do relatório.
- [ ] 1.8 Obter aprovação formal do Apply.

## 2. Xano

- [ ] 2.1 Criar função e endpoint de rejeição com a ordem de validação do design D1. Evidência: testes XanoScript de Gerente da Loja, outra Loja, sem Loja, Técnico, Diretoria, Administrador, troca pendente, inexistente, justificativa vazia, status `Novo`, `Encerrado` e `Cancelado`, e `ultima_atualizacao_em` divergente, todos sem escrita nos casos de erro.
- [ ] 2.2 Somente após 1.7: implementar as escritas do design D2. Evidência: sucesso com status, comentário público do Gerente, `alteracao_chamado` com o par de status e campos funcionais preservados; projeção do histórico (H-1) contendo a transição.
- [ ] 2.3 Confirmar que Save, filas, filtros, preferências, deduplicação e enum permanecem inalterados. Evidência: diff e suíte existente.
- [ ] 2.4 Validar no MCP, executar dry-run seletivo e publicar somente com aprovação.

## 3. Reflex

- [ ] 3.1 Cliente e DTO da rejeição com classificação 401/403/404/409/422/5xx e mensagem própria para conflito. Evidência: testes de cliente.
- [ ] 3.2 Ação e estados no detalhe do Gerente (design D4). Evidência: testes de State e página, incluindo ausência da ação fora de `Resolvido`.

## 4. Validação

- [ ] 4.1 Suíte completa, `reflex compile --dry`, `openspec validate rejeicao-solucao-gerente --strict` e `git diff --check`, com classificação dos resultados.
- [ ] 4.2 Testes HTTP fim a fim com usuários de teste autorizados; sem autorização, registrar como não executado.
