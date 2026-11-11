# Spec Delta

## Purpose

Definir fórmulas, recortes e tratamento de dados inconsistentes dos indicadores operacionais, sem antecipar consultas ou dashboards.

## ADDED Requirements

### Requirement: Indicadores derivam somente de fatos persistidos
Os indicadores de disponibilidade, MTTD, MTTR, SLA e recorrência DEVEM (MUST) ser calculados exclusivamente a partir de fatos persistidos no Xano: eventos de `historico_disponibilidade_totens`, `evento_timestamp` da telemetria referenciada, `chamados`, Categoria e transições de status registradas em `alteracao_chamado`. O sistema NÃO DEVE (MUST NOT) inventar, estimar ou completar timestamps ausentes, nem persistir durações, percentuais, médias ou agregados sem change aprovada.

#### Scenario: Marco ausente
- **WHEN** um evento necessário ao cálculo não possui o timestamp exigido pela fórmula
- **THEN** o registro é excluído do cálculo e contado como inconsistência no resultado, sem valor substituto

#### Scenario: Período sem dados
- **WHEN** não há eventos elegíveis no período para um indicador de média
- **THEN** o indicador é apresentado como indisponível, e não como zero

### Requirement: MTTR mede a recuperação do Totem
O MTTR DEVE (MUST) medir o tempo médio entre o início e o fim de indisponibilidades encerradas do Totem, conforme os marcos aprovados para disponibilidade, e NÃO DEVE (MUST NOT) usar abertura, resolução ou encerramento de chamado. Indisponibilidades ainda abertas NÃO DEVEM (MUST NOT) entrar na média.

#### Scenario: Chamado aberto após recuperação
- **WHEN** o Totem volta a Online e o chamado correspondente continua aberto
- **THEN** a indisponibilidade entra no MTTR e o status do chamado não altera o valor

#### Scenario: Indisponibilidade aberta
- **WHEN** o Totem continua Offline no fim do período
- **THEN** a indisponibilidade não entra na média e é informada em contagem própria

### Requirement: Categoria é a referência de causa e recorrência
A análise de causas e de recorrência DEVE (MUST) agrupar chamados pela Categoria. Título, descrição ou outro campo NÃO DEVEM (MUST NOT) substituir a Categoria sem decisão aprovada.

#### Scenario: Mesma descrição em Categorias diferentes
- **WHEN** dois chamados do mesmo Totem possuem descrições iguais e Categorias diferentes
- **THEN** eles não são considerados recorrência entre si

### Requirement: Faixas do termômetro de SLA
O consumo percentual de SLA DEVE (MUST) ser classificado como normal abaixo de 70%, risco de 70% a 90% inclusive, crítico acima de 90% até 100% inclusive, e violado acima de 100%.

#### Scenario: Limites exatos
- **WHEN** o consumo é exatamente 70%, 90% ou 100%
- **THEN** a classificação é, respectivamente, risco, risco e crítico

### Requirement: Período e recortes dos indicadores são explícitos
Cada indicador DEVE (MUST) receber um período de análise `[t0, t1)`, com cortes interpretados em `America/Sao_Paulo` e comparação dos fatos por timestamp UTC. Disponibilidade, MTTD e MTTR DEVEM (MUST) permitir recortes por Loja e Totem; cumprimento de SLA, por Loja, Categoria e Prioridade; recorrência, por Loja, Totem e Categoria. O recorte de Loja para fatos históricos DEVE (MUST) usar a Loja comprovada no instante do fato, sem substituí-la pela Loja atual do Totem. A escolha de período padrão ou apresentação em dashboard pertence a change própria.

#### Scenario: Fato anterior à transferência
- **WHEN** um Totem possui fato de monitoramento antes de ser transferido para outra Loja
- **THEN** o recorte da Loja de destino não inclui esse fato, mesmo que ela seja a Loja atual do Totem

#### Scenario: Período vazio de média
- **WHEN** o recorte não contém evento elegível para MTTD ou MTTR
- **THEN** o indicador é indisponível, e não zero

### Requirement: Disponibilidade usa tempo observado e marcos de telemetria
Para cada Totem, o período observável DEVE (MUST) começar no maior dentre `t0`, a primeira telemetria e `05/10/2026 00:00 America/Sao_Paulo`, e terminar em `t1`. Cada indisponibilidade DEVE (MUST) começar no `evento_timestamp` da telemetria referenciada pelo evento `offline` e terminar no `evento_timestamp` da telemetria referenciada pelo evento `online`, limitada ao período observável. O percentual do Totem DEVE (MUST) ser `100 × (1 − tempo_indisponível / tempo_observável)`. Loja e rede DEVEM (MUST) somar tempos indisponíveis e observáveis dos Totens antes da divisão, sem média simples de percentuais. Totem sem período observável DEVE (MUST) ser excluído e contado.

Se um evento necessário para determinar o estado ou intervalo do Totem no período observável tiver telemetria de referência ausente ou inválida, estado repetido em eventos consecutivos ou marco final anterior ao inicial, a disponibilidade do Totem DEVE (MUST) ser indisponível. A disponibilidade agregada da Loja ou rede DEVE (MUST) ser indisponível se qualquer Totem incluído no recorte estiver nessa condição. O resultado DEVE (MUST) informar a quantidade de Totens afetados; NÃO DEVE (MUST NOT) tratar o trecho inválido como tempo Online.

#### Scenario: Totens observados por durações diferentes
- **WHEN** T1 tem 62 minutos indisponíveis em 1.440 observados e T2 tem 30 em 120
- **THEN** a disponibilidade agregada é `100 × (1 − 92/1.560) = 94,10%`, sujeita ao arredondamento de duas casas

#### Scenario: Indisponibilidade cruza o período
- **WHEN** um intervalo Offline começa antes de `t0` ou termina depois de `t1`
- **THEN** apenas sua interseção com o período observável entra no numerador

#### Scenario: Transferência durante a indisponibilidade
- **WHEN** um Totem é transferido entre duas Lojas durante um intervalo Offline
- **THEN** cada Loja recebe somente o trecho com vínculo histórico comprovado; a rede conserva o intervalo do Totem

#### Scenario: Histórico inválido em um Totem da rede
- **WHEN** um Totem incluído no recorte tem um evento necessário ao cálculo cujo ID de telemetria referenciada não existe mais
- **THEN** a disponibilidade do Totem e o agregado da rede são indisponíveis, e o Totem é contado como afetado

### Requirement: MTTD mede da última telemetria à detecção
O MTTD DEVE (MUST) ser a média, em minutos, de `detectado_em(offline) − evento_timestamp(telemetria_referencia)`, para eventos `offline` cujo `detectado_em` esteja no período. O limite de heartbeat NÃO DEVE (MUST NOT) ser subtraído. Evento sem telemetria de referência válida, sem timestamp ou com duração negativa DEVE (MUST) ser excluído e contado como inconsistente.

#### Scenario: Duas detecções válidas
- **WHEN** os intervalos até a detecção são 18 e 20 minutos
- **THEN** o MTTD é 19 minutos

### Requirement: MTTR mede recuperações concluídas no período
O MTTR DEVE (MUST) ser a média, em minutos, de `evento_timestamp(online) − evento_timestamp(offline)` dos pares consecutivos válidos cujo marco de recuperação `online` pertença ao período. Indisponibilidades abertas NÃO DEVEM (MUST NOT) entrar na média e DEVEM (MUST) aparecer em contagem própria. O estado do chamado NÃO DEVE (MUST NOT) alterar o MTTR.

#### Scenario: Recuperação após mudança de mês
- **WHEN** um Totem fica Offline em 31/10 e volta a Online em 01/11
- **THEN** a duração entra no MTTR do período de novembro

### Requirement: Cumprimento de SLA exclui chamados cancelados
O consumo individual DEVE (MUST) usar a linha do tempo de status e `sla_horas_aplicado` vigente definidos em `sla-resolucao-encerramento`, sem somar o período em `Resolvido` nem reiniciar na troca de Categoria. O cumprimento no período DEVE (MUST) dividir a quantidade de chamados elegíveis com consumo até o SLA pela quantidade de chamados elegíveis que entram no estado de parada vigente (`Resolvido` ou `Encerrado`) no período. Chamados `Cancelado` e não calculáveis DEVEM (MUST) ser excluídos e contados separadamente. Após rejeição, o chamado DEVE (MUST) ser reavaliado na próxima resolução, com o saldo anterior preservado.

#### Scenario: Cancelados fora da base
- **WHEN** 8 de 10 chamados resolvidos cumprem o SLA e há 2 cancelados
- **THEN** o cumprimento é `8/10 = 80%`, sem incluir os cancelados no numerador ou denominador

#### Scenario: Rejeição retoma o consumo
- **WHEN** um chamado consumiu 2 horas antes de `Resolvido`, passou 3 horas nesse estado e consumiu mais 2 horas após a rejeição
- **THEN** o consumo usado no cumprimento da próxima resolução é 4 horas

### Requirement: Recorrência usa Categoria e Totem em 30 dias
Um chamado elegível criado no período DEVE (MUST) ser recorrente quando existir outro chamado elegível do mesmo Totem e da mesma Categoria criado nos 30 dias corridos anteriores, incluindo o limite de 30 dias e excluindo o mesmo instante. Somente chamados classificados como `Incidente`, com status diferente de `Cancelado` e com Totem e Categoria preenchidos DEVEM (MUST) participar da base e da busca de predecessor. O predecessor PODE (MAY) anteceder `t0`. A taxa DEVE (MUST) ser a quantidade de chamados recorrentes dividida pela quantidade de chamados elegíveis criados no período; ausências de Totem ou Categoria DEVEM (MUST) ser contadas à parte.

#### Scenario: Mesmo Totem e Categoria dentro da janela
- **WHEN** o mesmo Totem tem Incidentes não cancelados da mesma Categoria em 01/10, 05/10 e 20/10
- **THEN** os de 05/10 e 20/10 são recorrentes, e a taxa no período que contém os três é `2/3 = 66,67%`

#### Scenario: Mesma Loja, Totens diferentes
- **WHEN** dois Incidentes da mesma Categoria ocorrem em Totens diferentes da mesma Loja
- **THEN** um não torna o outro recorrente

#### Scenario: Chamado cancelado ou Requisição
- **WHEN** um chamado é `Cancelado` ou sua Categoria é `Requisição`
- **THEN** ele não entra no numerador, no denominador nem como predecessor de recorrência

### Requirement: Indicadores distintos não são combinados
Disponibilidade, MTTD, MTTR, SLA e recorrência DEVEM (MUST) ser calculados e apresentados separadamente. Nenhum indicador DEVE (MUST NOT) combinar tempo de disponibilidade do Totem com tempo de SLA do chamado na mesma fórmula.

#### Scenario: Chamado e indisponibilidade simultâneos
- **WHEN** um chamado de heartbeat está aberto durante a indisponibilidade do Totem
- **THEN** a disponibilidade usa somente os eventos de disponibilidade e o SLA usa somente a linha do tempo do chamado
