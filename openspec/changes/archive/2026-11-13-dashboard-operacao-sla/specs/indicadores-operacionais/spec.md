# Spec Delta

## MODIFIED Requirements

### Requirement: Período e recortes dos indicadores são explícitos
Cada indicador de período DEVE (MUST) receber um intervalo `[t0, t1)`, com cortes interpretados em `America/Sao_Paulo` e comparação dos fatos por timestamp UTC. Disponibilidade, MTTD e MTTR DEVEM (MUST) permitir recortes por Loja e Totem; cumprimento de SLA, por Loja e Categoria; recorrência, por Loja, Totem e Categoria. O risco atual de SLA DEVE (MUST) usar o instante da consulta como retrato, com recortes por Loja e Categoria, independentemente do período selecionado. O recorte de Loja para fatos históricos DEVE (MUST) usar a Loja comprovada no instante do fato, sem substituí-la pela Loja atual do Totem. A escolha de período padrão ou apresentação em dashboard pertence a change própria.

#### Scenario: Fato anterior à transferência
- **WHEN** um Totem possui fato de monitoramento antes de ser transferido para outra Loja
- **THEN** o recorte da Loja de destino não inclui esse fato, mesmo que ela seja a Loja atual do Totem

#### Scenario: Período vazio de média
- **WHEN** o recorte não contém evento elegível para MTTD ou MTTR
- **THEN** o indicador é indisponível, e não zero

#### Scenario: Recorte de SLA sem Prioridade
- **WHEN** a Diretoria aplica Loja e Categoria aos indicadores de SLA
- **THEN** o cumprimento e o risco respeitam esses recortes sem exigir seleção por Prioridade

#### Scenario: Risco atual independente do período
- **WHEN** a Diretoria seleciona Hoje e um chamado antigo permanece em contagem de SLA
- **THEN** o risco atual usa o consumo no instante da consulta, não exclui o chamado apenas por sua data de abertura
