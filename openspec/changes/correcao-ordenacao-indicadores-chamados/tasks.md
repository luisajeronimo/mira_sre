# Tasks

## 1. Ordenação técnica no Xano

- [x] 1.1 Ajustar somente o caminho `responsavel` de `service_desk/listar_chamados_tecnico` para ordenar toda a coleção pelo texto exibido `tecnico_nome` ou `Não atribuído`, normalizado e desempatar por id em ASC/DESC; verificar os testes inline com nomes em ordem inversa aos ids, empate de nome e não atribuído.
- [x] 1.2 Atualizar `tests/test_fila_tecnica_xanoscript.py` para proteger a ordenação determinística pelo texto exibido, os empates, a posição alfabética de `Não atribuído` e a não regressão de `aberto_por`; verificar com `pytest -q tests/test_fila_tecnica_xanoscript.py`.

## 2. Indicadores nas tabelas Reflex

- [x] 2.1 Ajustar somente os helpers de cabeçalho em `app/chamados/tecnico/pages.py` e `app/chamados/gerente/pages.py` para exibir uma única seta da direção ativa e nenhuma nas colunas inativas, sem renderizar `ASC`/`DESC`; verificar que os handlers de ordenação atuais permanecem conectados.
- [x] 2.2 Atualizar asserções focadas de UI/State para as duas tabelas, incluindo Técnico, Diretoria e Administrador pela fila compartilhada; verificar com os dois testes de cabeçalho ordenável em `tests/test_technical_state.py` e `tests/test_gerente_lista_state.py`.

## 3. Validação e publicação controlada

- [x] 3.1 Validar o XanoScript da função alterada, executar os testes focados e `reflex compile --dry`; verificar que não há mudança em contratos, persistência ou em `Aberto por`.
- [x] 3.2 Executar `git diff --check` e `openspec validate correcao-ordenacao-indicadores-chamados --strict`; verificar saída sem erros.
- [x] 3.3 Mediante autorização humana específica, executar dry-run Xano e publicar somente `service_desk/listar_chamados_tecnico`; executar novo dry-run e confirmar ausência de recursos pendentes ou não autorizados.
