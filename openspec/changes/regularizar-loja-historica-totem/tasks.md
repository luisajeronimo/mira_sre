# Tasks

## 1. Decisões e gates

- [x] 1.1 Revisão humana da proposta e aprovação do Apply (somente repositório; sem push). Aprovado pela responsável pelo projeto em 2026-11-07.
- [ ] 1.2 Decidir DL-1 a DL-5 ou registrar que permanecem abertas sem bloquear a regularização documental.
- [x] 1.3 Regra fixada pela solicitação de 2026-11-07: chamados legados sem evidência histórica não recebem vínculo retroativo automático e não há fallback para a Loja atual.

## 2. Regularização dos documentos XanoScript (cópia fiel do publicado)

- [x] 2.1 `xano workspace pull` somente leitura para diretório temporário; registrar data, hora e quantidade de documentos. Feito em 2026-11-07 19:58: 142 documentos, sem registros; idêntico ao `pull` da proposta.
- [x] 2.2 Copiar para `xano/` somente os documentos do design D2 (tabela, campo `identificacao`, 4 funções novas, 7 funções atualizadas, endpoints de heartbeat, listas, `gerente/ativos-historicos` e `administracao/totens*`), sem reescrever lógica. Evidência: diff de cada arquivo contra o `pull`, limitado a formatação. Feito: 12 criados e 10 atualizados; único ajuste foi esvaziar linhas somente com espaços (21 arquivos). Rotas `administracao/totens*` em `xano/api/mira_administracao/`, como as demais rotas do grupo MIRA Auth no repositório.
- [x] 2.3 Preservar alterações locais em andamento nos mesmos arquivos (por exemplo, `obter_chamado_solicitante.xs` já reconciliado) e registrar qualquer conflito para decisão humana. Nenhum dos 10 arquivos atualizados tinha alteração local; `obter_chamado_solicitante.xs` (fora da cópia) preservado. Comparação linha a linha confirmou que a lógica do repositório está contida no publicado; diferenças semânticas registradas no design.
- [x] 2.4 Validar todos os documentos com o Xano Developer MCP. Evidência: contagem de válidos. 132/132 válidos (`xano_validate_xanoscript`).
- [x] 2.5 Dry-run completo somente leitura: nenhuma diferença nos documentos do escopo e nenhum `DROP_FIELD`; diferenças restantes listadas e justificadas (escopo excluído e DE-8). Resultado no design ("Resultado do Apply local"), inclusive a assimetria de ida e volta de `obter_detalhe_ativo_monitoramento`.

## 3. Testes

Cenários (spec `vinculo-historico-totem-loja` e deltas):

| # | Cenário | Teste local (contrato) | Teste nativo XanoScript (mocks) | HTTP real |
|---|---|---|---|---|
| T1 | Totem com vínculo anterior ao chamado | resolvedor ordena por `efetivado_em` desc e filtra `<= instante` | `resolver_loja_totem_no_instante`: "na fronteira da transferência" | Exige dados: autorização de dados de teste |
| T2 | Totem transferido depois da abertura | idem | "depois da transferência" | Idem |
| T3 | Totem sem vínculo histórico | resolvedor devolve `null`; ausência de fallback para `lojas_id` atual | "antes do primeiro vínculo" | Possível hoje: chamados 49–87 com Gerente 13 → 403 |
| T4 | Chamado novo com criação de marco | `abrir_chamado_manual` e `verificar-falhas` gravam `marco` só sem vínculo e com `criado_em` | testes publicados de `abrir_chamado_manual` | Não executar: cria registros |
| T5 | Gerente consulta chamado da própria Loja | autorizador compara Loja resolvida e Loja do Gerente | `obter_chamado_gerente_autorizado`: "autoriza chamado da loja" | Exige vínculo existente: hoje inexistente |
| T6 | Gerente acessa chamado de outra Loja | idem | "rejeita chamado de outra loja" | Possível hoje (403) |

- [x] 3.1 Testes de contrato locais para T1–T6 sobre os documentos copiados, incluindo teste estático de ausência de fallback para a Loja atual e de ausência de backfill. `tests/test_loja_historica_xanoscript.py`: 16 passaram; mutações (resolução com `>=`, autorizador pela Loja atual, marco retroativo) detectadas. Testes existentes que dependiam do texto anterior foram ajustados para comparação insensível a espaços ou para a regra publicada.
- [x] 3.2 Executar no Xano somente os testes nativos de funções **somente leitura** (resolvedor, autorizador, listas e detalhes), após confirmar a ausência de `db.add`, `db.edit`, `db.patch` e `db.del`. Testes de `abrir_chamado_manual`, `transferir_totem` e rotas de Totem não são executados sem autorização (funções com escrita). 36/36 PASS: resolvedor (3), `listar_chamados_gerente` (2), `listar_chamados_tecnico` (11; 1 repetido após falha de rede local), `obter_chamado_tecnico` (7), `obter_detalhe_ativo_monitoramento` (3), `obter_chamado_gerente` (6), `obter_chamado_gerente_autorizado` (4). `obter_loja_historica_fato` e `listar_ativos_historicos_gerente` não têm testes publicados.
- [x] 3.3 HTTP somente leitura para T3 e T6 com as contas de teste; T1, T2, T4 e T5 registrados como não executados até haver dados autorizados. Executado em 2026-11-07: Gerente 403 em detalhe, comentários e histórico de chamados sem Loja histórica e em id inexistente (3 passaram). Como todos os chamados estão sem vínculo, T6 com vínculo real em outra Loja não se distingue de T3. T1, T2, T4 e T5: NÃO EXECUTADOS.
- [x] 3.4 Suíte completa, `openspec validate --strict` e `git diff --check`. 623 passaram e 21 pulados (E2E sem variáveis); OpenSpec 18/18; `git diff --check` sem problemas.

## 4. Documentação

- [ ] 4.1 `docs/domain-model.md`: registrar Totem com histórico de vínculos (seções 3 e 5), Loja histórica do chamado, marco, não retroatividade e consequência para chamados legados. A alteração feita na branch foi descartada na integração por decisão humana; permanece a versão de `main`.
- [ ] 4.2 `docs/project-overview.md` e `README.md`: registrar regra publicada e estado dos dados (sem vínculos em 2026-11-07). As alterações feitas na branch foram descartadas na integração por decisão humana; permanecem as versões de `main`.
- [ ] 4.3 Registrar a change própria para as divergências excluídas (rotas administrativas, Loja "Ativa", `telemetria_equipamentos POST`, `gerente/chamados POST`). **Pendente:** listadas na proposal (Fora do escopo). Progresso em 2026-11-08: Loja "Ativa", `telemetria_equipamentos POST` e `gerente/chamados POST` passaram a ter change própria ([reconciliar-contratos-publicados](../reconciliar-contratos-publicados/proposal.md)); as rotas administrativas que existem somente no publicado continuam sem change.

## 5. Encerramento

- [ ] 5.1 Revisão independente e consolidação das specs, considerando a ordem de arquivamento com `acompanhamento-solicitante-historico-status`.
