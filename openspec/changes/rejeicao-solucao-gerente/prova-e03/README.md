# Pacote da prova E0.3 (atomicidade de `db.transaction`)

Situação: **preparado e validado estaticamente; não executado.** Nenhum arquivo daqui pertence ao MIRA nem fica em `xano/`, para não entrar por engano em `xano workspace push`.

## Conteúdo

| Arquivo | Papel |
|---|---|
| `table/e03_prova.xs` | Tabela exclusiva com índice único em `rotulo`; somente dados fictícios |
| `function/e03/executar_cenario.xs` | Cenários de escrita seguida de falha |
| `function/e03/falhar.xs` | Função que sempre lança erro (cenário `function.run`) |
| `workflow_test/e03_rollback.xs` | Executa os cenários e lê a tabela depois de cada falha |

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
| Validação estática MCP | 4/4 arquivos válidos (`xano_validate_xanoscript`, MCP 2.2.6) |
| Teste local | `tests/test_prova_e03_pacote.py`: cobertura da matriz e isolamento do pacote; não executa XanoScript |
| Teste com mock | Não se aplica: mock não exercita o banco nem o rollback |
| Teste de runtime / persistência e rollback | **Não executado** |
| Publicação | Não se aplica; o pacote nunca deve ir ao workspace compartilhado |

## Por que não foi executado

- Os testes de workflow e unitários rodam no runtime de um workspace: tabela, funções e teste precisam ser enviados antes. O único workspace da conta é o compartilhado `152692`, cuja alteração não está autorizada.
- `xano sandbox` exige plano pago. `xano ephemeral` cria tenant dentro do workspace compartilhado.
- A documentação (MCP, `workflow-tests`) informa que `datasource = "live"` clona o datasource antes de cada execução, e que datasources nomeados são aceitos. Ela não informa a disponibilidade no plano Free nem o que acontece com as escritas quando `datasource` é omitido. Usar isso como isolamento exige confirmação oficial e autorização para enviar o pacote.

## Execução (somente após autorização de ambiente isolado)

1. Confirmar que o destino não é `152692` nem contém dados reais.
2. `xano workspace push --dry-run -d openspec/changes/rejeicao-solucao-gerente/prova-e03 -w <isolado>`; revisar o dry-run e depois executar o push.
3. `xano workflow_test list -w <isolado>`, depois `xano workflow_test run <id> -w <isolado>`.
4. Registrar a saída completa. Cada execução exige tabela vazia, porque os marcadores são únicos.
5. Critério: zero efeito parcial em todos os cenários de 1 a 6 e controle igual a 1. Se o controle falhar, o resultado é inválido. Resultado positivo não libera a rejeição nem o encerramento automaticamente: o relatório precisa de aprovação humana (DT-1).
