# Validação Xano da rodada de 05 a 07/11/2026

Evidências da branch `explore-monitoramento-xano` (base `06cc763`, sem commit). As rodadas de 05 e 06/11 não publicaram nada nem alteraram o workspace compartilhado `152692`. As publicações autorizadas de 07/11 (Pacotes A e B) estão registradas em [pacote-publicacao.md](./pacote-publicacao.md); as seções de 07/11 abaixo são consultas somente leitura e testes sobre o publicado.

## Ferramenta

Xano Developer MCP `@xano/developer-mcp` 2.2.6 (pacote oficial da Xano), executado localmente por `npx` e acionado por JSON-RPC via stdio. Foram usadas somente ferramentas locais: `xano_validate_xanoscript`, `xano_xanoscript_docs` (documentação 2.7.1) e `xano_cli_docs`. Nenhuma ferramenta do MCP acessa o workspace.

## Resultados

| Etapa | Resultado | Classificação |
|---|---|---|
| Validação MCP dos 14 arquivos da change (7 funções, 5 endpoints novos, 2 GETs genéricos), 1ª rodada | 12 válidos, 2 inválidos: `\|count` dentro de `expect` em `listar_chamados_solicitante.xs`; comentário dentro do bloco `db.query` em `listar_historico_status.xs`. O dry-run anterior tinha aceitado ambos | Erros corrigidos |
| Validação MCP dos 14 arquivos após a correção | 14/14 válidos | Passou |
| Validação MCP de `xano/` completo, incluindo `calcular_consumo_sla_chamado.xs` (change `sla-resolucao-encerramento`) | 121/121 válidos | Passou |
| `calcular_consumo_sla_chamado.xs`, 1ª validação | 3 erros: filtros `num_min` e `num_max` inexistentes no XanoScript; substituídos por condicionais explícitas com a mesma semântica | Erros corrigidos; depois, válido |
| Dry-run seletivo (`xano workspace push --dry-run --no-guids --no-fast`, workspace `152692`, branch `v1`, 14 arquivos) | `+7` funções e `+5` endpoints criados, `~2` endpoints atualizados; sem erros e sem outras diferenças; nenhum arquivo local alterado | Prévia; não é runtime |
| Blocos `test` XanoScript | Escritos e com sintaxe válida | **Não executados**: exigem runtime Xano |
| Testes HTTP ponta a ponta | — | **Não executados**: sem publicação e sem usuários de teste |
| Publicação | — | **Não executada**: sem autorização |

## Task 4.1: leitura de `alteracoes.status`

| Classe | Conteúdo |
|---|---|
| Documentado (MCP 2.7.1) | `json` aceita qualquer estrutura JSON; `get` com padrão (`$obj\|get:"chave":padrão`) é a forma documentada de acesso a propriedade; `is_object` e `is_text` retornam booleano. A documentação não trata curto-circuito de `&&` nem o acesso por ponto a chave ausente |
| Observado (parser do MCP) | A consulta por `chamados_id` e `tipo_evento == "alteracao_chamado"`, a ordenação composta e a leitura em etapas (`is_object` → `get:"status":null` → `get:"anterior"` e `get:"resultante"`) foram aceitas. Comentários dentro de `db.query` e de `test`, filtros dentro de `expect` e índices `[n]` dentro de `expect` são rejeitados |
| Inferido | Sem acesso por ponto a chave ausente e sem condição que dependa de curto-circuito, a projeção não depende dos dois comportamentos não documentados |
| Desconhecido | O valor efetivamente retornado pelo runtime para registros reais de `alteracoes` e o resultado dos blocos `test` no Xano |

Decorrência: a forma prevista no design D3 é suportada pela sintaxe e pela documentação, então não há motivo para parar a change. Para não depender do que é desconhecido, `listar_historico_status` passou a ler `alteracoes.status` com `get` e padrão nulo, com o mesmo critério de transição válida. O comportamento no runtime continua pendente (task 6.2).

## Prova E0.3: ambiente isolado

| Candidato | Verificação | Resultado |
|---|---|---|
| `xano sandbox` | Documentação do CLI pelo MCP: disponível somente em planos pagos; o plano Free (`build`) não pode criá-lo | Não atende à restrição de plano |
| `xano ephemeral` | `ephemeral create` cria o tenant **dentro de um workspace**; `xano workspace list` (leitura) mostra somente `152692`, o compartilhado; `ephemeral list -w 152692`: nenhum tenant | Violaria "não alterar o workspace compartilhado" |

Nenhum ambiente foi criado. E0.3 permanece **bloqueada por ambiente**: rejeição e encerramento automático não foram implementados (DT-1).

## Tasks 2.2 e 2.3 (2026-11-07)

Somente leitura no workspace `152692`, branch `v1`: nenhum push, nenhum registro criado ou alterado.

### Testes nativos XanoScript (unit tests, incluídos no Free)

Executados com `xano unit_test run <id> -w 152692 -b v1` sobre funções publicadas confirmadas como somente leitura (sem `db.add`, `db.edit`, `db.patch`, `db.del` ou `api.request`). Os testes usam mocks: validam a lógica de autorização e projeção, não os dados reais nem as cláusulas `where` substituídas pelo mock.

| Função | Testes | Resultado |
|---|---|---|
| `autorizacao/exigir_perfil` | 7 (inclui bloqueio de Gerente, Técnico e Diretoria) | 7 PASS |
| `autorizacao/exigir_escopo_loja` | 7 (inclui "nega outra loja ao gerente" e "isola lojas entre gerentes") | 7 PASS |
| `service_desk/obter_chamado_gerente` | 6 (inclui "rejeita chamado de outra loja" e "rejeita chamado inexistente") | 6 PASS |
| `service_desk/obter_chamado_gerente_autorizado` | 4 ("autoriza chamado da loja", "rejeita gerente sem loja"; os outros 2 compartilham id com os de `obter_chamado_gerente`) | 4 execuções PASS |
| `service_desk/listar_comentarios_publicos_gerente` | 2 ("lista publico em ordem desc", "lista sem interacao legado") | 2 PASS |

Total: 26 execuções e 24 testes distintos, todos PASS. Os GETs genéricos não têm blocos `test`; adicioná-los exigiria nova publicação.

### Runtime HTTP (`tests/test_e2e_isolamento_interacoes_gerente.py`)

Contas de teste da responsável (Técnico, Gerente, Diretoria e Administrador); credenciais só em variáveis de ambiente do processo. O teste respeita o limite do Free (pausa de 2,5 s e espera em 429): na primeira execução, o limite compartilhado do workspace devolveu 429 já no segundo login.

| Teste | Resultado |
|---|---|
| 2.2: Gerente, interação inexistente | 403, PASSOU |
| 2.2: Técnico preservado (detalhe 200, inexistente 404) | PASSOU |
| 2.2: Gerente, comentário público, comentário interno e evento operacional da própria Loja | PULADO (não executado): sem chamados na Loja do Gerente de teste |
| 2.3 (a)(b): comentários públicos da própria Loja, igualdade com os públicos da base, DTO, ordem e ausência de restritos | PULADO (não executado): mesmo motivo |
| 2.3 (b): Gerente na lista genérica | 403, PASSOU |
| 2.3 (c): Gerente no detalhe, nos comentários e na interação genérica de chamado de outra Loja | 403/403/403, PASSOU |
| 2.3 (d): Técnico com resultado dos genéricos | PASSOU |
| 2.3 (d): Diretoria e Administrador (genérico 403, comentários do Gerente 403, fila global 200) | PASSOU (2) |

Resumo: 7 passaram, 4 pulados. Sem as variáveis `MIRA_E2E_*`, o módulo é ignorado na suíte local.

Diagnóstico dos dados (somente contagens): a lista do Gerente de teste tem 0 chamados; a fila global tem 22 chamados (18 sem Loja resolvida no DTO); as 28 interações estão em 13 chamados, 19 em chamados de outra Loja e 9 em chamados fora da fila global; composição: 14 comentários públicos, 1 comentário não público e 13 eventos operacionais.

Observação de regra: as funções publicadas de lista, detalhe e autorização do Gerente usam a Loja **histórica** do Totem (`resolver_loja_totem_no_instante`); o repositório usa a Loja atual. A spec fala em "relação persistida chamado, Totem e Loja", sem distinguir os dois casos. Os testes usam o comportamento publicado e não decidem a regra.

## Avisos do Language Server do VS Code (07/11/2026)

| Arquivo | Aviso anterior | Causa | Correção | Depois |
|---|---|---|---|---|
| `listar_chamados_solicitante.xs` | 6× `Unknown table "ativo"` / `"categoria"` | O `dbReferenceScanner` do `@xano/xanoscript-language-server` 12.27.0 trata todo `$db.<nome>` como tabela, só pela análise léxica, e não conhece as chaves de `join` | Chaves do `join` renomeadas para os nomes reais (`ativos_referencia`, `categorias_servico`), como no exemplo oficial (`post: {table: "post"}`); campos `ativo_id`, `ativo_nome`, `categoria_id` e `categoria_nome` preservados | 0 referências desconhecidas no scanner oficial |
| `listar_historico_status.xs` | 4× `Unknown table "autor"` | Idem | Chave do `join` renomeada para `usuarios`; `autor_id`, `autor_nome` e `autor_role` preservados; `join` continua `left` (usuário inexistente ou `usuarios_id` nulo continuam tratados) | 0 no scanner; VS Code sem avisos |
| `listar_comentarios_publicos_solicitante.xs` | Mesmo padrão (`autor`), encontrado pelo scanner | Idem | Chave renomeada para `usuarios`; DTO e filtro iguais aos do Gerente | 0 |
| `obter_chamado_solicitante.xs` | Mesmo padrão (`ativo`, `loja`, `categoria`, `solicitante`, `tecnico`) | Idem | `ativos_referencia`, `lojas`, `categorias_servico` renomeados. **Remanescentes:** `solicitante` e `tecnico`, dois joins na mesma tabela `usuarios`, que exigem chaves distintas | 2 avisos remanescentes: limitação do Language Server |

Evidências: (a) **validação estática MCP**: os 4 arquivos válidos individualmente e `xano/` com 121/121 válidos; (b) scanner oficial executado localmente (`lexDocument` e `scanDbReferences` do pacote 12.27.0): funções publicadas e em produção, como `listar_chamados_gerente.xs` e `listar_comentarios_publicos_gerente.xs`, geram os mesmos avisos com aliases distintos, o que confirma que o aviso não indica erro de runtime; (c) **teste local**: `test_referencias_db_usam_tabelas_reais_salvo_joins_duplos_em_usuarios`. A equivalência de comportamento das duas formas de chave de join no **runtime** não foi testada (sem runtime).
