# Plano de execução, normalização e rollback da prova E0.3

## Autorização e limite

Em 2026-11-08, a responsável autorizou usar o workspace Xano `152692`, branch `v1`, para a prova E0.3 em um datasource próprio de teste. O plano Free inclui até três datasources ([preços oficiais](https://www.xano.com/pricing)). A [documentação de datasources](https://docs.xano.com/the-database/database-basics/data-sources) confirma que os registros são separados, enquanto o schema é compartilhado. A prova usa apenas dados fictícios, não altera o datasource ativo e não migra registros do datasource real. A autorização não dispensa o relatório e sua aprovação antes das escritas de rejeição ou encerramento automático.

O nome planejado do datasource é `mira_e03`. Se já existir ou se não for possível selecionar esse datasource explicitamente no workflow test, não executar a prova nem apontá-la para o datasource ativo.

## Inventário e preparação antes de qualquer escrita remota

1. Registrar o datasource ativo, os datasources existentes, o branch `v1` e os recursos `e03` já existentes. Conferir que não há colisão de nomes ou GUIDs.
2. Fazer um pull somente leitura do `v1` com registros para diretório local temporário protegido, fora do repositório, sem `--env`; registrar data, quantidade de documentos e checksum do snapshot. Não incluir dados reais em evidências versionadas.
3. Validar os quatro XanoScripts do pacote pelo Xano Developer MCP e executar `tests/test_prova_e03_pacote.py` localmente. O workflow test precisa conter `datasource = "mira_e03"`.
4. Criar `mira_e03` vazio pela interface do Xano, confirmar que o datasource ativo não mudou e que a tabela de prova está vazia. Nenhum dado de produção é copiado.
5. Executar `xano workspace push --dry-run -d openspec/changes/rejeicao-solucao-gerente/prova-e03 -w 152692 -b v1`. Aceitar somente `CREATE` da tabela `e03_prova`, das funções `e03/executar_cenario` e `e03/falhar` e do workflow test `e03_rollback`; zero atualização ou remoção de outros recursos. Revisar o diff completo.

## Prova no runtime

6. Fazer o push parcial do mesmo diretório para `152692`/`v1`, sem `--sync`, `--delete`, `--records`, `--truncate`, `--env` ou `--force`. Executar imediatamente novo dry-run; qualquer diferença não esperada interrompe a prova.
7. Localizar o ID de `e03_rollback` com `xano workflow_test list -w 152692 -b v1`. Confirmar no XanoScript publicado o datasource `mira_e03` e executá-lo uma vez com `xano workflow_test run <id> -w 152692 -o json`. A leitura posterior de cada cenário ocorre no datasource de teste. Não executar `run_all`.
8. Registrar a saída e as contagens: controle fora de transação = 1; cenários de falha dentro de transação = 0 efeitos parciais; `db.patch` preserva o valor anterior. Se o controle falhar, a prova é inválida. Se qualquer cenário deixar efeito parcial, interromper o Apply das escritas e voltar à decisão humana. A prova sequencial não demonstra isolamento sob concorrência.
9. Conferir que o datasource ativo e os registros reais não foram alterados pela prova. Registrar o resultado como **passou**, **falhou** ou **bloqueado**, sem converter análise estática em prova runtime. Submeter o relatório à responsável antes de implementar escritas que dependem de DT-1.

## Normalização e rollback dos recursos de teste

- **Se o push falhar ou o diff fugir do pacote:** parar; comparar o pull remoto com o inventário; não repetir com `--sync` ou `--force`. Recursos que não pertençam ao pacote ficam intocados.
- **Se a prova falhar:** preservar evidência e interromper as escritas de rejeição e encerramento. A função de consumo de SLA, somente leitura, não precisa ser revertida por esse resultado.
- **Se aparecer qualquer escrita no datasource real:** interromper a prova imediatamente, preservar um segundo snapshot somente leitura e identificar os registros afetados por tabela, ID e horário, sem expor dados pessoais no relatório. Comparar cada registro com o snapshot anterior e com as gravações operacionais concorrentes. Preparar compensação seletiva somente para os registros comprovadamente afetados pela prova; submeter o diff e a operação destrutiva ou corretiva à aprovação humana. Não restaurar o workspace inteiro nem sobrescrever alterações legítimas ocorridas depois do backup.
- **Depois da análise do relatório:** propor remoção individual do workflow test, das duas funções e da tabela `e03_prova`, sempre conferindo IDs/GUIDs contra o inventário. A tabela contém apenas dados fictícios do datasource de teste. Não usar `xano workspace push --sync --delete`, não apagar o datasource real nem restaurar o workspace inteiro por cima de mudanças de terceiros. Operações destrutivas só serão executadas após aprovação específica; até lá, os recursos de prova permanecem identificados e sem endpoint público.
- **Datasource:** mantê-lo inativo durante a prova. Depois, a responsável decide se o conserva para testes futuros ou autoriza sua remoção. Se o ativo mudar por engano, interromper a prova e restaurar o valor registrado no inventário antes de nova execução.
- **Verificação final:** pull e dry-run do `v1` sem diferenças não aprovadas; inventário de recursos `e03`; comparação de contagens do datasource real com o snapshot, considerando gravações operacionais concorrentes. Registrar qualquer divergência antes de declarar o ambiente normalizado.

## Histórico de disponibilidade encontrado na validação de indicadores

A consulta somente leitura de 2026-11-08 encontrou 81 referências de telemetria ausentes em 148 transições e 28 pares consecutivos do mesmo estado; 16 referências ausentes ocorrem entre as 83 transições detectadas no período aprovado. A normalização desses fatos **não** integra a prova E0.3. Primeiro, investigar a origem da ausência de telemetrias e das sequências repetidas com evidência de execução e histórico de alterações. Até existir fonte confiável para reconstrução e change aprovada, não fazer backfill, exclusão ou correção de registros; a disponibilidade afetada e seu agregado permanecem indisponíveis, conforme `indicadores-governanca-formulas`.

## Bloqueio atual

Em 2026-11-08, a revisão automática do navegador recusou acesso à origem `https://app.xano.com`; a interface não pôde ser observada para criar o datasource. Nenhum recurso remoto foi alterado nesta tentativa. A prova runtime segue **bloqueada por acesso ao navegador**, mesmo com a autorização de negócio acima.
