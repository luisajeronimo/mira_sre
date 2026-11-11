# Pacote da prova E0.3 (atomicidade de `db.transaction`)

Situação: **Bloqueada no runtime por restrição de plano Free no Xano; limitação aceita por decisão humana.** Nenhum arquivo daqui pertence ao MIRA nem fica em `xano/`, para não entrar por engano em `xano workspace push` do produto. O push remoto foi tentado após autorização de `datasource = "live"`, mas a API do Xano rejeitou com `Error: Push failed (400): Multidoc import failed: Please upgrade to access workflow tests.` Em conformidade com as restrições de `openspec/config.yaml` (vedação a upgrade pago), a decisão humana de 2026-11-08 registrou o bloqueio de ambiente e aceitou formalmente a limitação funcional para prosseguir com a sprint.

## Conteúdo

| Arquivo | Papel |
|---|---|
| `table/e03_prova.xs` | Tabela exclusiva com índice único em `rotulo`; somente dados fictícios |
| `function/e03/executar_cenario.xs` | Cenários de escrita seguida de falha |
| `function/e03/falhar.xs` | Função que sempre lança erro (cenário `function.run`) |
| `workflow_test/e03_rollback.xs` | Executa os cenários e lê a tabela depois de cada falha, com `datasource = "live"` explícito (clonagem isolada) |

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
| Validação estática MCP | **4/4 válidos, 0 warnings** (Developer MCP, 2026-11-08); cobre sintaxe e estrutura |
| Teste local | `tests/test_prova_e03_pacote.py`: **5/5 passaram** com `.venv/bin/python -m pytest`; cobertura da matriz e isolamento |
| Teste com mock | Não se aplica: mock não exercita o banco nem o rollback |
| Teste de runtime / persistência e rollback | **Bloqueado por restrição de ambiente/plano** (`workflow_test` indisponível no plano Free do Xano); **limitação aceita por decisão humana** em 2026-11-08 |
| Publicação | Não se aplica; o pacote nunca deve ir ao workspace compartilhado |

## Histórico de bloqueio e deliberação

- Em 2026-11-08, autorizou-se a execução no `datasource = "live"`.
- Durante a tentativa de push para o workspace `152692`, a API do Xano retornou `400 Multidoc import failed: Please upgrade to access workflow tests`.
- Seguindo `openspec/config.yaml`, o projeto utiliza exclusivamente o plano Free e não realiza upgrade de plano.
- O usuário deliberou explicitamente por registrar o bloqueio e aceitar a limitação funcional, liberando o avanço das demais entregas da Sprint 3.

## Execução (somente após criar e verificar o datasource de teste)

1. Confirmar workspace `152692`, branch `v1`, datasource `mira_e03` vazio e datasource ativo inalterado.
2. Seguir backup, validação e dry-run seletivo de [plano-execucao-rollback.md](./plano-execucao-rollback.md), depois publicar somente os quatro recursos temporários.
3. `xano workflow_test list -w 152692 -b v1`, depois `xano workflow_test run <id> -w 152692 -o json`.
4. Registrar a saída completa. Cada execução exige tabela de prova vazia, porque os marcadores são únicos; não repetir sem verificar e reiniciar exclusivamente os dados fictícios da prova.
5. Critério: zero efeito parcial em todos os cenários de 1 a 6 e controle igual a 1. Se o controle falhar, o resultado é inválido. Resultado positivo não libera a rejeição nem o encerramento automaticamente: o relatório precisa de aprovação humana (DT-1).
