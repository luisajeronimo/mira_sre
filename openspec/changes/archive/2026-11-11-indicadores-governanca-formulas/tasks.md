# Tasks

> Encerramento do Apply por decisão humana em 11/11/2026: a task 4.1 foi fechada como decisão de escopo. A conclusão deste checklist cobre fórmulas e documentação; não afirma implementação de consultas ou dashboards.

## 1. Decisões (responsável pelo projeto)

- [x] 1.1 DI-1 a DI-5 aprovadas em 2026-11-08: marcos de telemetria, MTTD desde a última telemetria, corte histórico em 05/10/2026 00:00 `America/Sao_Paulo`, MTTR no período da recuperação e agregação ponderada pelo tempo observado. Evidência: `design.md` e delta spec.
- [x] 1.2 DS-1 aprovada: SLA em tempo corrido.
- [x] 1.2a DS-2 aprovada em 2026-11-08: excluir Cancelados da base do cumprimento de SLA. Evidência: `design.md` e delta spec.
- [x] 1.3 DR-1 a DR-3 aprovadas em 2026-11-08: janela de 30 dias corridos, mesmo Totem e Categoria, somente Incidentes não cancelados. Evidência: `design.md` e delta spec.
- [x] 1.4 DI-3: corte conservador aprovado em 05/10/2026 00:00 `America/Sao_Paulo`, após a evidência de publicação e runtime em 04/10/2026 na change arquivada `2026-10-04-monitoramento-heartbeat-incidentes-automaticos`. Sem inferência de histórico anterior.
- [x] 1.5 Em 2026-11-08, aprovada a regra de que histórico necessário inválido de qualquer Totem incluído torna indisponível a disponibilidade do Totem e o agregado da Loja ou rede, informando quantos Totens foram afetados. Evidência: `design.md`, delta spec e `docs/domain-model.md`.

## 2. Consolidação documental

- [x] 2.1 Decisões e fórmulas aprovadas registradas em `design.md` e nos requisitos MUST de `indicadores-operacionais`. Evidência: `openspec validate indicadores-governanca-formulas --strict` passou em 2026-11-08.
- [x] 2.2 `docs/domain-model.md` §13 atualizado com os marcos aprovados, sem antecipar a apresentação dos dashboards; corrigida também a deriva do SLA aplicado na troca de Categoria frente à spec consolidada `tratativa-operacional-chamados`.

## 3. Validação das fórmulas (sem dashboard)

- [x] 3.1 Casos sintéticos de referência com entradas e resultados esperados registrados em `design.md` e conferidos por cálculo independente: T1 95,69%, rede 96,46%, corte 95,83%, MTTD 19 min, MTTR 51 min, SLA 80% e recorrência 66,67%.
- [x] 3.2 Consulta somente leitura e cálculo amostral sobre dados reais executados em 2026-11-08. Evidência: `validacao-dados-reais-2026-11-08.md`. MTTD, MTTR, SLA e recorrência tiveram amostras calculáveis; disponibilidade agregada ficou **não calculável com confiança** por referências ausentes e sequências de estado inconsistentes. Nenhum valor parcial foi aceito como indicador oficial.

> Situação após a validação de 2026-11-08: as decisões de fórmula, recorte e indisponibilidade do agregado diante de histórico inválido estão aprovadas; os indicadores seguem sem consulta ou dashboard. A validação real encontrou 81 referências de telemetria ausentes em 148 transições de disponibilidade e 28 pares consecutivos do mesmo estado. A disponibilidade da rede não recebeu valor oficial. A causa da ausência das referências segue pendente de investigação. A função interna de consumo de SLA da change `sla-resolucao-encerramento` já foi publicada e testada, mas ainda não é exposta por endpoint.

## 4. Fora desta change

- [x] 4.1 Registrar que dashboards e consultas de indicadores permanecem fora desta change e foram dispensados deste Apply pela responsável em 11/11/2026. **Não implementados**; exigem change própria se retomados.
