# Proposal

## Why

A Diretoria já consegue acompanhar disponibilidade e confiabilidade dos Totens, mas ainda não dispõe da visão executiva de chamados e SLA prevista para a Sprint 4. As regras de consumo e classificação do SLA existem nas specs consolidadas; faltam contratos agregados e apresentação gerencial.

## What Changes

- Acrescentar à página de Indicadores da Diretoria a volumetria dos chamados **abertos no período**, agrupados pelo **status atual no instante da consulta**.
- Mostrar no Termômetro de SLA tanto a conformidade dos chamados que entram no estado de parada vigente no período quanto o risco atual dos chamados em estados que ainda consomem SLA, inclusive os abertos antes do período. Identificar claramente que o risco é um retrato da consulta e que a conformidade usa o período selecionado.
- Permitir recortes por Loja histórica comprovada e Categoria, além do período para volumetria e conformidade. A decisão humana desta change retira Prioridade dos recortes exigidos para o indicador de cumprimento de SLA.
- Calcular agregados no Xano a partir de chamados, transições e da função de consumo de SLA já aprovada, com autorização exclusiva da Diretoria, contagens de elegibilidade e de dados não calculáveis e testes com conjunto conhecido.
- Manter fora do escopo causas, recorrência, Top 5 Lojas, exportação, materialização de agregados e alterações no fluxo de tratativa ou nos dados históricos.

## Capabilities

### New Capabilities

- `dashboard-operacao-sla`: consulta executiva de volumetria por status, conformidade e risco de SLA, com filtros, autorização e apresentação.

### Modified Capabilities

- `indicadores-operacionais`: alterar o recorte obrigatório do cumprimento de SLA para Loja e Categoria, removendo Prioridade por decisão humana explícita.

## Impact

- **Reflex:** novos painéis na rota de Indicadores da Diretoria, State e cliente HTTP tipado; os indicadores existentes de disponibilidade, MTTD e MTTR permanecem separados.
- **Xano:** contratos de leitura agregada e catálogo de filtros, reutilizando fatos persistidos e `service_desk/calcular_consumo_sla_chamado`; nenhuma nova tabela ou agregação persistida.
- **Dependências:** `indicadores-operacionais`, `sla-encerramento-chamados`, `vinculo-historico-totem-loja`, autorização de perfis e a página da change `dashboard-disponibilidade-confiabilidade`. As referências de planejamento “4”, “6”, “7” e “D4” não são usadas como substitutas dessas dependências verificáveis.
- **Decisões da responsável:** volume por abertura no período e status atual; conformidade e risco no mesmo painel; risco de todos os chamados em contagem no instante da consulta; filtros de Loja e Categoria, sem Prioridade.
