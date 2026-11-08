# Tasks

## 1. Decisões e gates

- [x] 1.1 DR2-0 aprovada: rejeição na Sprint 3, condicionada à segurança.
- [x] 1.2 DR2-1 aprovada: somente o Gerente da própria Loja rejeita; domínio atualizado.
- [x] 1.3 DR2-2 aprovada: `Solução Rejeitada` permanece canônico; Save inalterado.
- [x] 1.4 DT-1 aprovada: prova E0.3 obrigatória antes das escritas.
- [x] 1.5 K-B aprovada: histórico exibido após validação (em `acompanhamento-solicitante-historico-status`).
- [x] 1.6 Autorização específica obtida em 2026-11-08 para datasource próprio de teste no workspace `152692`, branch `v1`, e revisão do gate DT-1. O Free admite até três datasources conforme a documentação oficial; os registros são separados, mas schema e recursos publicados são compartilhados. Evidência e restrições: [prova-e03/plano-execucao-rollback.md](./prova-e03/plano-execucao-rollback.md).
- [ ] 1.7 Criar o datasource de teste sem torná-lo ativo, executar a prova E0.3 conforme o design D6 de `acompanhamento-solicitante-historico-status` e obter aprovação do relatório antes das escritas de rejeição. **Não executado:** runtime, persistência e rollback ainda sem prova; o acesso à UI `app.xano.com` foi recusado pelo gate automático de navegador em 2026-11-08, e nenhum recurso remoto foi alterado.
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
