# Proposal

## Why

Cartão da Sprint 3 "Governança / Indicadores" (estado informado: decisão necessária). Os dashboards previstos (`docs/project-overview.md` §6.10) dependem de fórmulas verificáveis de disponibilidade, MTTD, MTTR, SLA e recorrência. Hoje o domínio define somente conceitos e dados mínimos (`docs/domain-model.md` §12–§13), e `monitoramento-disponibilidade-totens` exige que os fatos persistidos permitam esses cálculos futuramente, sem persistir agregados. Nenhum indicador está implementado.

Esta change fecha as fórmulas e os recortes **antes** de qualquer dashboard. Ela não implementa telas, consultas nem agregações.

## What Changes

- Nova capability `indicadores-operacionais` com as regras já sustentadas pelo domínio e pelas specs: cálculo somente a partir de fatos persistidos; MTTR como recuperação do Totem; Categoria como referência de causa e recorrência; faixas do termômetro de SLA; indicadores distintos não combinados; tratamento explícito de dados ausentes ou inconsistentes.
- Design com fórmula completa, marcos temporais, recortes, exemplos sintéticos e cenários de teste de cada indicador, com alternativas onde a decisão é de negócio.
- Registro das decisões que exigem aprovação da responsável pelo projeto.

## Capabilities

### New Capabilities

- `indicadores-operacionais`: definição verificável dos indicadores de disponibilidade, MTTD, MTTR, SLA e recorrência.

### Modified Capabilities

Nenhuma.

## Classificação das decisões

| Tema | Sustentado por specs/domínio | Consolidável tecnicamente | Exige aprovação |
|---|---|---|---|
| Fonte dos dados | `historico_disponibilidade_totens`, `telemetria_equipamentos.evento_timestamp`, `chamados`, Categoria (`monitoramento-disponibilidade-totens`) | Uso de `alteracao_chamado.alteracoes.status` como linha do tempo de status (mesma base de H-1) | — |
| MTTR | Recuperação do Totem, não encerramento do chamado (domínio §13) | Somente indisponibilidades encerradas | Marcos de início e fim (DI-1); atribuição ao período (DI-4) |
| MTTD | Tempo entre o início identificável e a detecção (domínio §13) | — | Marco inicial (DI-2) |
| Disponibilidade | Proporção do período observado em que o Totem esteve operacional | Ponderação por tempo; recorte por Loja e rede | Marcos (DI-1); início do período observável (DI-3); agregação (DI-5) |
| SLA | Regras de contagem e faixas (domínio §12); tempo corrido (DS-1, aprovada em 2026-11-04) | Fórmula por estados a partir da linha do tempo de status | Base do percentual de cumprimento (DS-2) |
| Recorrência | Categoria como referência; segmentação por Totem, Loja e período (domínio §13) | — | Janela (DR-1); unidade de agrupamento (DR-2); status e classificação incluídos (DR-3) |

Detalhes, alternativas e consequências estão em [design.md](./design.md).

As decisões de 2026-11-04 (DR2-0, DT-1, DR2-1, DR2-2, K-B, DE-1, DE-2, DE-3) não aprovam fórmulas desta change; somente DS-1 se aplica aqui. As fórmulas permanecem em proposta até a decisão de DI-1 a DI-5, DS-2 e DR-1 a DR-3.

## Impact

- Documentação e especificação apenas. Nenhum código, schema, endpoint ou dado é alterado.
- Os dashboards e consultas de indicadores dependem desta change aprovada e de change própria de implementação.
- O indicador de SLA depende da definição de consumo de SLA em `sla-resolucao-encerramento`.

## Fora do escopo

- Dashboards, consultas, agregações persistidas, cache de indicadores.
- MTBF, volumetria e Top 5 Lojas (não solicitados neste cartão; dados mínimos já constam no domínio).
- Calendário de dias úteis ou feriados.
