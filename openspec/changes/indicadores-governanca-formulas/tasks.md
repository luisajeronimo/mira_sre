# Tasks

## 1. Decisões (responsável pelo projeto)

- [ ] 1.1 Decidir DI-1 a DI-5 (marcos e agregação de disponibilidade, MTTD e MTTR).
- [x] 1.2 DS-1 aprovada: SLA em tempo corrido.
- [ ] 1.2a Decidir DS-2 (base do cumprimento de SLA).
- [ ] 1.3 Decidir DR-1 a DR-3 (janela, agrupamento e chamados da recorrência).
- [ ] 1.4 Confirmar a data inicial confiável do histórico de disponibilidade (DI-3).

## 2. Consolidação documental

- [ ] 2.1 Registrar as decisões no design e transformar em requisitos MUST da capability `indicadores-operacionais` as fórmulas aprovadas. Evidência: `openspec validate indicadores-governanca-formulas --strict`.
- [ ] 2.2 Atualizar `docs/domain-model.md` §13 com os marcos aprovados, sem antecipar apresentação dos dashboards.

## 3. Validação das fórmulas (sem dashboard)

- [ ] 3.1 Converter os exemplos sintéticos e cenários do design em casos de teste de referência (entrada e resultado esperado). Evidência: tabela de casos revisada.
- [ ] 3.2 Com autorização de consulta somente leitura ao Xano, executar as fórmulas sobre dados reais e registrar inconsistências encontradas. Sem autorização, registrar como não executado.

> Classificação de 2026-11-07: (a) **implementável com as decisões vigentes**: consumo de SLA `C`, `U` e faixas (DS-1 e domínio §12), implementado localmente como função interna em `sla-resolucao-encerramento` (task 2.1, sem execução no runtime); (b) **dependente de decisão**: cumprimento de SLA (DS-2), disponibilidade (DI-1, DI-3, DI-5), MTTD (DI-2), MTTR (DI-1, DI-4) e recorrência (DR-1 a DR-3), não implementados; (c) **fontes disponíveis**: as tabelas do design (Context); (d) **qualidade dos dados**: histórico de status só existe desde o Save operacional, a data confiável do histórico de disponibilidade é desconhecida (DI-3), e nenhum cálculo foi feito sobre dados reais (3.2 não executada). Numerador, denominador, filtros, período e dados ausentes de cada indicador estão no design.

## 4. Fora desta change

- [ ] 4.1 Dashboards e consultas de indicadores: change própria após a aprovação de 1.1–1.3.
