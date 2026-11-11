# Tasks

> Encerramento do Apply por decisão humana em 11/11/2026: a task 2.1 foi fechada com dispensa da matriz de testes restante. O `[x]` registra a decisão, não aprovação dos cenários não executados.

## 1. Decisões e gates

- [x] 1.1 DR2-0 aprovada: rejeição na Sprint 3, condicionada à segurança.
- [x] 1.2 DR2-1 aprovada: somente o Gerente da própria Loja rejeita; domínio atualizado.
- [x] 1.3 DR2-2 aprovada: `Solução Rejeitada` permanece canônico; Save inalterado.
- [x] 1.4 DT-1 aprovada: prova E0.3 obrigatória antes das escritas.
- [x] 1.5 K-B aprovada: histórico exibido após validação (em `acompanhamento-solicitante-historico-status`).
- [x] 1.6 Autorização específica obtida em 2026-11-08 para datasource próprio de teste no workspace `152692`, branch `v1`, e revisão do gate DT-1. O Free admite até três datasources conforme a documentação oficial; os registros são separados, mas schema e recursos publicados são compartilhados. Evidência e restrições: [prova-e03/plano-execucao-rollback.md](./prova-e03/plano-execucao-rollback.md).
- [x] 1.7 Execução no runtime da prova E0.3: **Bloqueada por restrição de ambiente/plano** (`workflow_test` requer upgrade pago na API do Xano). Conforme `openspec/config.yaml` e deliberação humana em 2026-11-08, a limitação funcional foi formalmente aceita para prosseguir sem recurso pago, validada estaticamente via MCP (4/4) e localmente via pytest (5/5).
- [x] 1.8 Obter aprovação formal do Apply (deliberada pelo usuário em 2026-11-08 para avançar na Sprint 3).

## 2. Xano

- [x] 2.1 Manter função e endpoint de rejeição publicados com a ordem de validação do design D1. A responsável dispensou em 11/11/2026 completar a matriz nativa de Gerente da Loja, outra Loja, sem Loja, Técnico, Diretoria, Administrador, troca pendente, inexistente, justificativa vazia, estados não elegíveis e versão divergente. Os testes nativos e HTTP já registrados passaram nos cenários executados; **a matriz integral e ausência de escrita em todos os erros não foram comprovadas**.
- [x] 2.2 Somente após 1.7: implementar as escritas do design D2. Evidência: no chamado 97, POST real autorizado mudou `Resolvido` para `Solução Rejeitada`, criou comentário público do Gerente e evento `alteracao_chamado` com o par de status; o histórico do Gerente e do solicitante projetou a transição. Campos funcionais alheios à rejeição permaneceram iguais no detalhe posterior.
- [x] 2.3 Confirmar que Save, filas, filtros, preferências, deduplicação e enum permanecem inalterados. Evidência: diff restrito aos arquivos da Sprint 3 e suíte existente sem regressões; a função de rejeição usa o status canônico sem modificar o Save.
- [x] 2.4 Validar no MCP, executar dry-run seletivo e publicar somente com aprovação. Função e endpoint publicados, correções posteriores revalidadas no MCP e republicadas; dry-run seletivo posterior limpo. Registro em [docs/sprint3-validacao-publicacao-2026-11-10.md](../../../docs/sprint3-validacao-publicacao-2026-11-10.md).

> Atualização de 2.1 (10/11/2026): sete testes nativos da função cobrem sucesso, justificativa vazia, `Novo`, `Encerrado`, `Cancelado`, versão obsoleta e conflito durante a transação; o helper de autorização cobre Loja própria, outra Loja, ausência de Loja e inexistente. Em HTTP real, a rejeição do 97 retornou `422` para espaços, `409` para versão obsoleta e `200` válida; Técnico, Administrador, Diretoria e anônimo foram negados sem mutação. A task segue aberta porque a matriz de testes XanoScript especificada ainda não cobre explicitamente troca pendente e todos os perfis diretamente na função.

## 3. Reflex

- [x] 3.1 Cliente e DTO da rejeição com classificação 401/403/404/409/422/5xx e mensagem própria para conflito. Evidência: `tests/test_frontend_sprint3.py` (payload mínimo, confirmação e seis classes de erro).
- [x] 3.2 Ação e estados no detalhe do Gerente (design D4). Evidência: `tests/test_frontend_sprint3.py` (justificativa vazia, sucesso, conflito com recarga e ausência da ação fora de `Resolvido`); compilação Reflex com K-B ligado e desligado.

## 4. Validação

- [x] 4.1 Suíte completa, `reflex compile --dry`, `openspec validate rejeicao-solucao-gerente --strict` e `git diff --check`, com classificação dos resultados. Em 2026-11-08: pytest **passou** (652 passaram, 26 E2E pulados), compilação Reflex **passou** com K-B desligado e ligado, OpenSpec strict **passou**, diff check **passou**.
- [x] 4.2 Testes HTTP fim a fim com usuários de teste autorizados. **Passou** em 10/11/2026: quatro perfis E2E, rejeição real do chamado 97 (`422`, `409`, `200`), confirmação de comentário e histórico e negação de outros perfis. Ver [registro de validação](../../../docs/sprint3-validacao-publicacao-2026-11-10.md).
