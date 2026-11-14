# Evidências da Sprint 5 — 14/11/2026

## Escopo aprovado e entregue

A responsável autorizou Explore, Propose e Apply, desconsiderando a seção de
dependências e mantendo o escopo acadêmico. No Explore, aprovou expressamente
as regras de base, filtros, Pareto, predecessor após transferência e publicação
seletiva. Os quatro artefatos foram criados e validados antes da implementação.
Archive não foi solicitado.

Foram implementados Top 5 Lojas, Pareto por Categoria e recorrência na aba
**Causas e recorrência** da página executiva existente. Os cálculos ocorrem no
Xano sobre chamados e vínculos persistidos. A interface mostra período, filtros
efetivos, numerador, denominador, detalhamentos por Loja/Totem e exclusões.
As regras estão publicadas em `docs/indicadores-causas-recorrencia.md` e na
própria aba. Não houve nova tabela, escrita de agregado, backfill ou alteração
de dados para testar; as alterações locais prévias foram preservadas.

## Validação local

| Verificação | Estado | Evidência |
| --- | --- | --- |
| Suíte Python | Passou | `make check`: 718 testes passaram, 41 pulados. Os pulados não são registrados como aprovação. |
| Contrato, cliente e State novos | Passou | 27 testes em `tests/test_indicadores_causas.py`; os três módulos executivos somam 61 testes aprovados na revisão independente. |
| Compilação Reflex | Passou | `make check` concluiu a compilação em 3,157 s após os ajustes finais da interface. |
| XanoScript | Passou | Developer MCP: cinco arquivos válidos; as três funções corrigidas foram revalidadas, sem erro ou aviso. Revisão independente também validou pelo MCP. |
| OpenSpec | Passou | `openspec validate dashboard-causas-recorrencia --strict`. |
| Diff | Passou | `git diff --check`. |
| Detector de UI | Passou no alcance estático | Impeccable detect retornou `[]` para `pages.py` e `paineis_causas.py`. Não substitui inspeção renderizada. |
| Página renderizada | Bloqueado por ferramenta | Playwright não conectou ao Chrome; CUA confirmou `The browser access host is unavailable`. Não há aprovação visual ou screenshot. |

Os testes Python cobrem contrato estrito, contagens, filtros combinados,
separação entre vazio e taxa zero, falhas sem resultado antigo, sessão expirada,
negação de acesso e incompatibilidade entre filtros pedidos e recebidos.

## Publicação e validação no Xano

Workspace **152692**, publicação seletiva de cinco documentos: três funções
`indicadores/*causas_recorrencia` e os GETs
`/indicadores/causas-recorrencia` e `/indicadores/causas-recorrencia/filtros`.
O dry-run inicial mostrou somente três funções e dois endpoints novos; foi
apresentado à responsável antes do push já autorizado. Cada atualização
posterior teve nova validação MCP, dry-run revisado e escopo seletivo.
Não foram usados `--force`, remoções, sincronização integral, importação de
registros ou variáveis de ambiente.

A rodada nativa inicial identificou problemas de caminhos numéricos no mapa de
grupos e instabilidade do desempate ao encadear sorts. Foram corrigidos com
chaves prefixadas e comparação explícita de volume/ID sobre os pequenos grupos
de Loja e Categoria. O corte de 80% usa contagens inteiras antes do
arredondamento. A revisão confirmou o custo proporcional ao escopo acadêmico.

| Verificação | Estado | Evidência |
| --- | --- | --- |
| Testes nativos finais | Passou | 35 testes da versão publicada passaram, sem falhas: 17 do resumo, 12 da consulta e 6 do catálogo. Incluem janela exata/fora de 30 dias, simultaneidade, transferência, empates, Pareto exato/cruzamento de 80%, exclusões, vazio, autorização, entradas inválidas e Totem sem nome. |
| Catálogo persistido | Passou | Execução real pelo CLI/Meta API com usuário Diretoria existente: 5 Lojas, 16 Totens e 12 Categorias; contrato Python válido. Tempo Xano: 0,10 s. |
| Agregados persistidos | Passou | Consulta real publicada, sem mocks, dos últimos 30 dias: 10 elegíveis, 3 recorrentes, taxa 30%, 5 Lojas no ranking e 6 Categorias. Contrato Python válido; tempo Xano: 0,41 s. |
| Filtros com dados persistidos | Passou | Loja: 5 elegíveis/3 recorrentes; Totem: 5/3; Categoria: 4/3; combinação dos três: 4/3. Filtros retornados e contrato Python conferidos. Tempos Xano medidos: 0,08–0,81 s; amostra acadêmica, sem extrapolação de capacidade. |
| HTTP anônimo | Passou | Os dois GETs responderam 401 sem sessão. |
| HTTP com sessão da Diretoria | Bloqueado por credencial | Não há `MIRA_E2E_EMAIL_DIRETORIA` e `MIRA_E2E_SENHA`. Os dois testes novos em `tests/test_e2e_indicadores_causas.py` ficaram pulados. Execução via CLI não é registrada como teste HTTP autenticado. |
| Dry-run final | Passou | Os cinco documentos retornaram `No changes to push` após a última publicação. |

As consultas persistidas foram executadas com a credencial administrativa já
configurada no CLI e a identidade de uma Diretoria existente, passando pela
função de autorização publicada. Não se criou sessão alternativa, usuário,
senha ou dado de teste. Tokens, hashes e dados pessoais não integram as
evidências.

## Revisão independente

Revisão read-only pelo papel MIRA Reviewer: confirmou arquitetura, autorização,
fórmula de recorrência, vínculo histórico e preservação do escopo. Os ajustes
de identificação de Totem sem nome, semântica de lista e texto do Pareto vazio
foram aplicados e conferidos. Após conferir 35/35 testes nativos, os recortes
persistidos, dry-run e tarefas, o Reviewer emitiu **aprovado**, com disposition
**ship no alcance de código e validações conferidas**, sem achados materiais
pendentes. A revisão executou independentemente 61 testes Python dos três
módulos executivos. Não declarou aprovação visual nem substituiu HTTP com
sessão por execução no CLI.

## Fechamento do Apply

`openspec instructions apply --change dashboard-causas-recorrencia --json`
retornou **all_done**, com **6 tarefas concluídas e nenhuma restante**.
As verificações bloqueadas estão discriminadas acima. O Archive permanece
fora do escopo autorizado nesta sessão.

## Simplificação dos textos após a entrega

A pedido da responsável, os textos junto aos indicadores foram encurtados e
as regras completas, com as contagens de exclusão, passaram para a seção
**Como os indicadores são calculados**, recolhida por padrão e acessível por
teclado. Período, recortes, bases e aviso de ausência de Loja histórica
continuam visíveis. `make reflex_check` passou em 5,731 s;
`git diff --check` passou e o detector estático de UI retornou `[]`.
A inspeção renderizada permanece sem aprovação, conforme o bloqueio registrado.

## Atualização posterior de acesso

A responsável substituiu a restrição inicial à Diretoria pela autorização de
Técnico, Diretoria e Administrador. Os artefatos ativos foram reconciliados.
A validação e publicação desta atualização são registradas em
`../2026-11-14-unificar-acessos-perfis-operacionais/evidencias.md`; as evidências acima
preservam a execução e a matriz que existiam na entrega inicial.

## Encerramento autorizado

Em 14/11/2026, a responsável solicitou Archive, commit e push das duas changes.
Também determinou que `docs/` contenha somente `domain-model.md` e
`project-overview.md`. O guia adicional de indicadores foi removido; as regras
passam a ser consultadas em `openspec/specs/dashboard-causas-recorrencia/spec.md`.
As evidências anteriores preservam o estado da entrega na data de sua execução.

Antes do Archive, os deltas foram consolidados e comparados com todas as
capacidades afetadas, preservando os demais requisitos e os Purposes existentes.
A validação strict das specs consolidadas passou: **22/22**, sem falhas.
