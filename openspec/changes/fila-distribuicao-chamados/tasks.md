# Tasks

## 1. Dados e histórico

- [x] 1.1 Estender `interacoes_chamado` com tipo de evento e Técnico anterior/novo opcionais, preservando registros existentes; validar schema aditivo e leitura de comentários legados sem backfill.
- [x] 1.2 Alinhar `docs/domain-model.md` com a regra de que somente Técnico pode ser responsável, mantendo a gestão de atribuição por Diretoria e Administrador e a relação `Chamado → 0..1 Técnico responsável`.

## 2. Xano: APIs e regras

- [ ] 2.1 Corrigir listagem e detalhe para consulta global por Técnico, Diretoria e Administrador com o DTO canônico; aplicar os filtros explícitos da lista do Gerente (número, status, Totem e período), oferecer somente os escopos `Todos` e `Atribuídos a mim` para Técnico e validar no Xano live lista, busca, detalhe e timeline legada.
- [x] 2.2 Evoluir o comando existente de assunção para assumir, atribuir, reatribuir e liberar, validando perfil, Técnico alvo e estados terminais; persistir responsável, timestamps e evento na mesma transação e validar idempotência, conflitos e status inalterado nos testes Xano.

## 3. Reflex

- [ ] 3.1 Adaptar proteção de rota, página, State e service para os três perfis autorizados, uma tabela global no padrão do Gerente, filtros confirmados somente após sucesso, pesquisa no backend, responsável atual e escopo rápido `Atribuídos a mim` exclusivo de Técnico; separar 401, 403 e falhas funcionais sem falso erro de identidade.
- [ ] 3.2 Adaptar o detalhe ao DTO canônico e à timeline cronológica, selecionando Técnico e ações de atribuição conforme perfil e estado; validar contra payload real que não há `undefined`, que interações legadas continuam legíveis e que `Encerrado` e `Cancelado` não oferecem ações.

## 4. Validação integrada

- [ ] 4.1 Validar o fluxo real de consulta global, filtros, pesquisa, detalhe, timeline, assunção, atribuição, reatribuição e liberação no Xano live, incluindo evento junto à alteração do responsável; executar validação OpenSpec estrita e revisar `git diff --check`. Testes unitários mockados não são evidência suficiente desta task.
