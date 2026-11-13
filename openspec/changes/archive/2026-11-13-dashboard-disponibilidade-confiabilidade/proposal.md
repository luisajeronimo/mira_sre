# Proposal

## Why

A Diretoria ainda não dispõe de uma visão executiva da disponibilidade da rede e dos tempos de detecção e recuperação. As fórmulas e os marcos históricos foram aprovados em `indicadores-operacionais`, mas ainda não há consulta agregada nem apresentação desses resultados.

## What Changes

- Criar uma página protegida de Indicadores para a Diretoria com disponibilidade geral e evolução comparável de MTTD e MTTR, com filtros de período, Loja e Totem.
- Destacar os atalhos de período “Últimos 30 dias” e “Hoje” no cabeçalho, preservando a seleção personalizada de datas e os recortes de Loja e Totem.
- Para “Hoje”, consultar o dia civil inteiro (00h até 23h59) e apresentar a disponibilidade da rede por hora; horas futuras ficam sem dado, e o agregado considera apenas o tempo já observado. MTTD e MTTR permanecem como médias do período nos cards. Para os demais períodos, preservar a série diária de MTTD e MTTR.
- Oferecer contratos Xano dedicados que validem o perfil e os filtros, calculem os indicadores a partir dos fatos persistidos e retornem valores, contagens e motivos de indisponibilidade suficientes para interpretação.
- Aplicar as fórmulas, o fuso, os recortes históricos e o tratamento de inconsistências já aprovados, incluindo a ponderação por tempo observado e a separação de indisponibilidades abertas.
- Incluir o destino Indicadores na navegação da Diretoria e apresentar estados de carregamento, vazio, erro e dados inconsistentes sem cálculo de métricas no Reflex.
- Limitar esta entrega a disponibilidade, MTTD e MTTR. Volumetria, SLA, causas, recorrência e exportação permanecem em entregas próprias.

## Capabilities

### New Capabilities

- `dashboard-disponibilidade-confiabilidade`: consulta executiva autorizada, filtros, série temporal e apresentação de disponibilidade, MTTD e MTTR.

### Modified Capabilities

- `navegacao-lateral-perfis`: acrescentar o destino Indicadores somente à matriz da Diretoria e seu estado ativo.

## Impact

- **Reflex:** nova página e State, rota protegida, cliente HTTP tipado e item de navegação.
- **Xano:** novos contratos autenticados e funções de agregação sobre telemetria, transições de disponibilidade, histórico de vínculos Totem–Loja e catálogos de filtros; sem persistir indicadores derivados.
- **Dependências técnicas verificadas:** `monitoramento-disponibilidade-totens`, `vinculo-historico-totem-loja`, `indicadores-operacionais` e autorização de perfis existentes. Por decisão humana de 12/11/2026, as referências de planejamento “2” e “D4” foram desconsideradas.
- **Decisão de apresentação aprovada em 12/11/2026:** acesso somente da Diretoria e período inicial de 30 dias civis, incluindo o dia atual, em pontos diários.
- **Decisão de período aprovada em 12/11/2026 e refinada posteriormente:** “Últimos 30 dias” consulta até o clique; “Hoje” seleciona o dia civil completo, com 24 posições horárias e dados disponíveis somente até a consulta. Ambos consultam ao clique, sem atualização automática.

## Planejamento informado

- **Área e perfil:** Indicadores, Diretoria.
- **Prioridade e sprint:** alta, Sprint 4.
- **Prazo:** início em 09/11/2026 e entrega prevista em 22/11/2026.
