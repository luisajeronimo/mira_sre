# Tasks

## 1. Diagnóstico

- [x] 1.1 Confirmar que `lista-operacional-chamados-gerente` está arquivada e
  criar esta change sem alterar o Archive anterior.
- [x] 1.2 Mapear State, cliente HTTP, `/me`, `/gerente/chamados` e
  `/gerente/ativos`; registrar que 429 não foi comprovado e que os logs locais
  mostram falha de websocket/servidor Reflex.

## 2. Estabilidade do ciclo de consulta

- [x] 2.1 Classificar 429 separadamente, sem expor corpo, token ou credencial,
  preservando `Retry-After` numérico quando presente.
- [x] 2.2 Impedir consultas concorrentes equivalentes e coalescer a intenção
  posterior sem retry agressivo.
- [x] 2.3 Não repetir o catálogo de ativos a cada sort/filtro e manter itens
  retornados quando uma consulta secundária falhar.
- [x] 2.4 Encerrar loading em sucesso, erro, redirect e exceção; preservar
  sessão confirmada para falhas que não sejam 401.

## 3. Testes

- [x] 3.1 Cobrir 429 sanitizado e `Retry-After`.
- [x] 3.2 Cobrir recuperação após falha transitória em nova consulta.
- [x] 3.3 Cobrir múltiplas ordenações, filtros/limpezas, exclusão mútua e
  reuso do catálogo de ativos.
- [x] 3.4 Revalidar o contrato de ordenação já consolidado sem alterá-lo.

## 4. Validação e encerramento

- [x] 4.1 Executar suíte, compile Reflex, OpenSpec strict e diff check.
  - `233` testes passaram; Reflex compile, OpenSpec strict global/change e
    `git diff --check` passaram.
- [x] 4.2 Revisão read-only da estabilidade e da preservação da sessão.
  - Revisão técnica do diff e dos testes confirmou 429 transitório, 401
    exclusivo para logout, loading em `finally`, coalescência e reuso do
    catálogo; não houve mudança Xano.
- [x] 4.3 Reconciliar evidências, publicar somente se houver recurso Xano
  legítimo e preparar Archive desta change.
  - `xano workspace push --dry-run` retornou `No changes to push`; a change
    não possui recurso remoto a publicar.
