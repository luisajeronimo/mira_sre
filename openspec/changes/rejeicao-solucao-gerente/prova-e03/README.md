# Pacote da prova E0.3 (atomicidade de `db.transaction`)

Situação: **preparado para validação estática; não executado no runtime.** Nenhum arquivo daqui pertence ao MIRA nem fica em `xano/`, para não entrar por engano em `xano workspace push` do produto. A revisão humana de 2026-11-08 autorizou a prova no datasource de teste `mira_e03` do workspace `152692`, branch `v1`; registros separados, schema e recursos compartilhados. O acesso à UI do Xano foi recusado pelo gate automático do navegador nesta sessão, portanto nenhum datasource ou recurso remoto foi criado.

## Conteúdo

| Arquivo | Papel |
|---|---|
| `table/e03_prova.xs` | Tabela exclusiva com índice único em `rotulo`; somente dados fictícios |
| `function/e03/executar_cenario.xs` | Cenários de escrita seguida de falha |
| `function/e03/falhar.xs` | Função que sempre lança erro (cenário `function.run`) |
| `workflow_test/e03_rollback.xs` | Executa os cenários e lê a tabela depois de cada falha, com `datasource = "mira_e03"` explícito |

## Matriz

| # | Cenário | Esperado se houver rollback |
|---|---|---|
| 0 | Controle: `db.add` sem transação e `precondition` falso | 1 registro (mostra que o teste detecta persistência) |
| 1 | `db.add` e `precondition` com `error_type = "standard"` | 0 registros |
| 2 | `db.add` e `precondition` com `error_type = "inputerror"` | 0 registros |
| 3 | `db.add` e `throw` | 0 registros |
| 4 | `db.add` e `function.run` de função que lança erro | 0 registros |
| 5 | `db.patch` (de `valor` 0 para 1) e `precondition` | registro com `valor = 0` |
| 6 | Duas escritas; a segunda viola o índice único | 0 registros |
| — | Concorrência | **Não coberta**: o teste de workflow executa em sequência e não há recurso documentado para chamadas paralelas |

## Classificação das evidências

| Categoria | Situação |
|---|---|
| Validação estática MCP | **4/4 válidos, 0 warnings** após a seleção explícita de `mira_e03` (Developer MCP, 2026-11-08); não prova runtime |
| Teste local | `tests/test_prova_e03_pacote.py`: **5/5 passaram** com `.venv/bin/python -m pytest`; cobertura da matriz e seleção de datasource, sem executar XanoScript |
| Teste com mock | Não se aplica: mock não exercita o banco nem o rollback |
| Teste de runtime / persistência e rollback | **Não executado** |
| Publicação | Não se aplica; o pacote nunca deve ir ao workspace compartilhado |

## Por que não foi executado

- Os testes de workflow exigem tabela, funções e teste publicados no `v1`. A autorização para isso foi dada em 2026-11-08, com seleção obrigatória do datasource `mira_e03` e preservação do ativo.
- A revisão automática do navegador recusou acesso a `app.xano.com` nesta sessão, impedindo a criação e verificação do datasource. Nenhum push foi feito.
- O [plano de execução e rollback](./plano-execucao-rollback.md) contém backup, seleção explícita, dry-run, critérios de prova e normalização.

## Execução (somente após criar e verificar o datasource de teste)

1. Confirmar workspace `152692`, branch `v1`, datasource `mira_e03` vazio e datasource ativo inalterado.
2. Seguir backup, validação e dry-run seletivo de [plano-execucao-rollback.md](./plano-execucao-rollback.md), depois publicar somente os quatro recursos temporários.
3. `xano workflow_test list -w 152692 -b v1`, depois `xano workflow_test run <id> -w 152692 -o json`.
4. Registrar a saída completa. Cada execução exige tabela de prova vazia, porque os marcadores são únicos; não repetir sem verificar e reiniciar exclusivamente os dados fictícios da prova.
5. Critério: zero efeito parcial em todos os cenários de 1 a 6 e controle igual a 1. Se o controle falhar, o resultado é inválido. Resultado positivo não libera a rejeição nem o encerramento automaticamente: o relatório precisa de aprovação humana (DT-1).
