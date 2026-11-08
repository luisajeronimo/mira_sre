# Proposal

## Why

Cartão da Sprint 3 "Governança / Indicadores". Os dashboards previstos (`docs/project-overview.md` §6.10) dependem de fórmulas verificáveis de disponibilidade, MTTD, MTTR, SLA e recorrência. O domínio define conceitos e dados mínimos (`docs/domain-model.md` §12–§13), e `monitoramento-disponibilidade-totens` exige que os fatos persistidos permitam esses cálculos futuramente, sem persistir agregados. Nenhum indicador está implementado.

Esta change fecha as fórmulas e os recortes **antes** de qualquer dashboard. Ela não implementa telas, consultas nem agregações.

## What Changes

- Nova capability `indicadores-operacionais` com as regras já sustentadas pelo domínio e pelas specs: cálculo somente a partir de fatos persistidos; MTTR como recuperação do Totem; Categoria como referência de causa e recorrência; faixas do termômetro de SLA; indicadores distintos não combinados; tratamento explícito de dados ausentes ou inconsistentes.
- Design com fórmula completa, marcos temporais, recortes, exemplos sintéticos e cenários de teste de cada indicador, com alternativas onde a decisão é de negócio.
- Registro das decisões aprovadas pela responsável pelo projeto em 2026-11-08: DI-1 a DI-5, DS-2, DR-1 a DR-3 e indisponibilidade do agregado quando qualquer Totem incluído tem histórico necessário inválido; DS-1 já estava aprovada.

## Capabilities

### New Capabilities

- `indicadores-operacionais`: definição verificável dos indicadores de disponibilidade, MTTD, MTTR, SLA e recorrência.

### Modified Capabilities

Nenhuma.

## Classificação das decisões

| Tema | Sustentado por specs/domínio | Consolidável tecnicamente | Decisão aprovada em 2026-11-08 |
|---|---|---|---|
| Fonte dos dados | `historico_disponibilidade_totens`, `telemetria_equipamentos.evento_timestamp`, `chamados`, Categoria (`monitoramento-disponibilidade-totens`) | Uso de `alteracao_chamado.alteracoes.status` como linha do tempo de status (mesma base de H-1) | — |
| MTTR | Recuperação do Totem, não encerramento do chamado (domínio §13) | Somente indisponibilidades encerradas | Telemetria no início e retorno (DI-1); período da recuperação (DI-4) |
| MTTD | Tempo entre o início identificável e a detecção (domínio §13) | — | Última telemetria como marco inicial (DI-2) |
| Disponibilidade | Proporção do período observado em que o Totem esteve operacional | Recorte por Loja histórica e rede | Marcos de telemetria (DI-1); corte em 05/10/2026 00:00 (DI-3); ponderação por tempo (DI-5) |
| SLA | Regras de contagem e faixas (domínio §12); tempo corrido (DS-1, aprovada em 2026-11-04) | Fórmula por estados a partir da linha do tempo de status | Excluir `Cancelado` do cumprimento (DS-2) |
| Recorrência | Categoria como referência; segmentação por Totem, Loja e período (domínio §13) | — | 30 dias (DR-1); Totem (DR-2); Incidentes não cancelados (DR-3) |

Detalhes, alternativas e consequências estão em [design.md](./design.md).

As decisões de 2026-11-04 (DR2-0, DT-1, DR2-1, DR2-2, K-B, DE-1, DE-2, DE-3) não aprovavam fórmulas desta change; somente DS-1 se aplicava aqui. Em 2026-11-08, a responsável aprovou os marcos por telemetria para disponibilidade e MTTR, MTTD desde a última telemetria, MTTR no período da recuperação, agregação ponderada pelo tempo observado, exclusão de Cancelados do cumprimento de SLA e recorrência em 30 dias por Totem e Categoria para Incidentes não cancelados. O início confiável do histórico de disponibilidade foi fixado em 05/10/2026 às 00:00 em `America/Sao_Paulo`, após a implantação comprovada em 04/10/2026.

## Impact

- Documentação e especificação apenas. Nenhum código, schema, endpoint ou dado é alterado.
- Os dashboards e consultas de indicadores dependem desta change aprovada e de change própria de implementação.
- O indicador de SLA depende da definição de consumo de SLA em `sla-resolucao-encerramento`.

## Fora do escopo

- Dashboards, consultas, agregações persistidas, cache de indicadores.
- MTBF, volumetria e Top 5 Lojas (não solicitados neste cartão; dados mínimos já constam no domínio).
- Calendário de dias úteis ou feriados.
