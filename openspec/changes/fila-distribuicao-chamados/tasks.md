# Tasks

## 1. Dados e histórico

- [ ] 1.1 Estender `interacoes_chamado` com tipo de evento e Técnico anterior/novo opcionais, preservando registros existentes; validar schema aditivo e leitura de comentários legados sem backfill.
- [ ] 1.2 Alinhar `docs/domain-model.md` com a regra de que somente Técnico pode ser responsável, mantendo a gestão de atribuição por Diretoria e Administrador e a relação `Chamado → 0..1 Técnico responsável`.

## 2. Xano: APIs e regras

- [ ] 2.1 Ampliar listagem e detalhe existentes para consulta global por Técnico, Diretoria e Administrador, pesquisa por número, filtros simples de responsável, roster mínimo de Técnicos e timeline única; validar cenários de autorização, conteúdo, timestamp e ordenação.
- [ ] 2.2 Evoluir o comando existente de assunção para assumir, atribuir, reatribuir e liberar, validando perfil, Técnico alvo e estados terminais; persistir responsável, timestamps e evento na mesma transação e validar idempotência, conflitos e status inalterado nos testes Xano.

## 3. Reflex

- [ ] 3.1 Adaptar proteção de rota, página, State e service existentes para os três perfis autorizados, fila global, pesquisa, filtros e responsável atual; validar estados de carregamento/erro e os testes Reflex relevantes.
- [ ] 3.2 Adaptar o detalhe existente para timeline cronológica, seleção de Técnico e ações de atribuição conforme perfil e estado; validar que `Encerrado` e `Cancelado` não oferecem ações e que nenhuma ação muda status.

## 4. Validação integrada

- [ ] 4.1 Validar o fluxo de consulta, assunção, atribuição, reatribuição e liberação de ponta a ponta, incluindo evento junto à alteração do responsável; executar validação OpenSpec estrita e revisar `git diff --check`.
