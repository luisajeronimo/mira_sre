# Design

## Context

Fatos persistidos disponíveis em `06cc763` (fonte: `xano/table/*.xs` e specs consolidadas):

| Fato | Origem | Campos usados |
|---|---|---|
| Transição de disponibilidade | `historico_disponibilidade_totens` | `ativos_referencia_id`, `status` (`online`/`offline`), `detectado_em`, `telemetria_referencia_id`, `heartbeat_limite_minutos` |
| Telemetria | `telemetria_equipamentos` | `ativos_referencia_id`, `evento_timestamp` |
| Totem e Loja | `ativos_referencia`, `lojas` | `lojas_id` |
| Chamado | `chamados` | `criado_em`, `status`, `sla_horas_aplicado`, `categorias_servico_id`, `ativos_referencia_id`, `origem` |
| Categoria | `categorias_servico` | `nome`, `tipo_itil` (`Incidente`/`Requisição`), `sla_horas` |
| Transição de status | `interacoes_chamado` com `tipo_evento = alteracao_chamado` | `alteracoes.status = {anterior, resultante}`, `criado_em` (desde a implantação do Save operacional) |

Não existem campos `resolvido_em`, `encerrado_em`, duração, percentual ou agregados persistidos, e nenhum deve ser criado por esta change. O evento `offline` referencia a última telemetria anterior à indisponibilidade; o evento `online` referencia a telemetria que fundamentou a recuperação. `detectado_em` é o instante da decisão do Xano, acionada pelo Fiscal a cada 300 segundos; o limite de heartbeat é 15 minutos.

Notação: período de análise informado pelo consumidor `P = [t0, t1)`, com `t0 < t1` e fim não posterior ao instante da consulta; `|I|` é a duração de um intervalo. As datas de corte são interpretadas em `America/Sao_Paulo` (o mesmo fuso dos filtros do Reflex) e comparadas como timestamps UTC em milissegundos. Esta change não escolhe um período padrão para dashboards futuros. Filtros permitidos: disponibilidade, MTTD e MTTR por período, Loja e Totem; SLA por período, Loja, Categoria e Prioridade; recorrência por período, Loja, Totem e Categoria. Recortes por Loja usam a Loja histórica comprovada do fato, conforme `monitoramento-disponibilidade-totens`, sem inferência pela Loja atual do Totem.

## Goals / Non-Goals

**Goals:** fórmulas completas, marcos, recortes, tratamento de dados ausentes, exemplos e cenários de teste suficientes para implementação e validação.

**Non-Goals:** dashboards, consultas, persistência de indicadores, calendário de dias úteis.

## Tipos de tempo

- **Tempo corrido:** diferença simples entre dois timestamps.
- **Tempo útil:** tempo corrido restrito a um calendário de expediente. O domínio não define expediente, feriados nem calendário; nenhum indicador o utiliza sem decisão DS-1.
- **Tempo de SLA:** tempo corrido somado somente nos estados que contam SLA (domínio §12); definido em `sla-resolucao-encerramento`.

## I1. Disponibilidade

**Finalidade:** proporção do período observado em que o Totem esteve operacional.

**Intervalos de indisponibilidade** do Totem `i`: cada par `offline_k → online_k` consecutivo em `historico_disponibilidade_totens`.

| Marco | Opção A (aprovada) | Opção B (rejeitada) |
|---|---|---|
| Início `a_k` | `evento_timestamp` da telemetria referenciada pelo evento `offline_k` (última prova de funcionamento) | `detectado_em` do evento `offline_k` |
| Fim `b_k` | `evento_timestamp` da telemetria referenciada pelo evento `online_k` (primeira prova de retorno) | `detectado_em` do evento `online_k` |

A opção A mede a indisponibilidade estimada pela telemetria e é independente da cadência do Fiscal; a B mede a indisponibilidade reconhecida pelo sistema e subestima o início em pelo menos 15 minutos. Os mesmos marcos são usados em I1 e I3 (**DI-1 aprovada**).

**Período observável** `O_i = [max(t0, h0, f_i), t1)`, onde `f_i` é a primeira telemetria do Totem e `h0 = 05/10/2026 00:00 America/Sao_Paulo` (`2026-10-05T03:00:00Z`, `1791169200000` ms) é o corte conservador aprovado após a implantação verificada em 04/10 (**DI-3 aprovada**). Totem sem telemetria ou com `O_i` vazio não tem período observável e é excluído.

**Fórmula:**

```
Indisp_i = Σ_k | [a_k, b_k) ∩ O_i |          (intervalo aberto: b_k = min(t1, agora))
Disp_i   = 1 − Indisp_i / |O_i|               (em %, duas casas)
Disp_Loja ou Disp_rede = 1 − Σ_i Indisp_i / Σ_i |O_i|   (ponderada por tempo — DI-5 aprovada)
```

Numerador: tempo indisponível; denominador: tempo observável. Unidade: percentual. Filtros: período, Loja, Totem. Para o recorte por Loja, intervalos que cruzam uma transferência são divididos no instante da transferência, atribuindo a cada Loja somente seu trecho comprovado; trechos sem vínculo histórico demonstrável não entram na agregação da Loja e são contados como indeterminados. A agregação da rede conserva esses trechos por Totem, pois não depende de Loja.

**Estado no início do período:** determinado pelo último evento anterior a `t0`; se o primeiro evento em `P` for `online`, o Totem estava indisponível desde `t0`.

**Dados ausentes ou inconsistentes** (contados no resultado, nunca preenchidos por inferência):

- telemetria referenciada inexistente ou sem `evento_timestamp` (opção A);
- dois eventos consecutivos do mesmo estado;
- `b_k < a_k`.

**Regra de confiabilidade aprovada em 2026-11-08:** se qualquer Totem incluído no recorte tiver evento necessário para determinar seu estado ou intervalo em `O_i` com uma das inconsistências acima, a disponibilidade desse Totem é indisponível. Nesse caso, a disponibilidade agregada da Loja ou rede que o contém também é indisponível, com a quantidade de Totens afetados informada. Eventos antigos sem efeito sobre `O_i` não invalidam o período. Totens sem período observável continuam excluídos e contados conforme a regra anterior. Não se remove apenas o intervalo inválido do numerador mantendo seu tempo no denominador, pois isso o transformaria indevidamente em tempo Online.

**Exemplo (dados sintéticos):** `P` = 20/10 00:00–21/10 00:00 (1.440 min). Totem T1: `offline` com telemetria de 10:00 e `detectado_em` 10:18; `online` com telemetria de 11:02 e `detectado_em` 11:05. Opção A: 62 min → `Disp = 1 − 62/1440 = 95,69%`. Opção B: 47 min → `96,74%`. Totem T2 (mesmo período): telemetria 14:00 / detecção 14:20; retorno 14:40 / 14:45. Opção A: 40 min → `97,22%`. Rede ponderada (A): `1 − 102/2880 = 96,46%`.

**Cenários de teste:** sem eventos (100% quando o estado inicial é comprovado como Online); indisponibilidade cruzando `t0` ou `t1`; intervalo aberto até `agora`; Totem criado no meio do período; Totem sem telemetria (excluído); evento necessário inconsistente (Totem e agregado indisponíveis, com contagem); opções A e B com os mesmos dados.

## I2. MTTD — Mean Time to Detect

**Finalidade:** tempo entre o início identificável da indisponibilidade e sua detecção pelo MIRA.

| Opção | Fórmula por evento `offline_k` | Leitura |
|---|---|---|
| A (aprovada) | `D_k = detectado_em(offline_k) − evento_timestamp(telemetria_referencia(offline_k))` | Tempo total até o sistema reconhecer a falha; por construção `D_k > 15 min` |
| B | `D_k = detectado_em(offline_k) − (evento_timestamp + heartbeat_limite_minutos)` | Somente a latência da verificação após vencido o limite (0–5 min com Fiscal a 300 s) |

**DI-2 aprovada:** `MTTD = média dos D_k` dos eventos `offline` com `detectado_em ∈ P`. Unidade: minutos. Filtros: período, Loja histórica no instante de `detectado_em`, Totem. Eventos sem telemetria de referência válida ou com `D_k < 0` são excluídos e contados. Sem evento elegível, o indicador é indisponível, não zero.

**Exemplo (sintético, opção A):** T1 `10:18 − 10:00 = 18 min`; T2 `14:20 − 14:00 = 20 min`; `MTTD = 19 min`. Opção B: 3 e 5 min; `MTTD = 4 min`.

**Cenários de teste:** um evento; vários eventos; evento sem telemetria de referência; período sem eventos (indicador indisponível, não zero).

## I3. MTTR — Mean Time to Repair/Recover

**Finalidade (sustentada pelo domínio §13):** tempo médio de recuperação do Totem; não é tempo de encerramento do chamado.

`R_k = b_k − a_k` com os marcos de DI-1, somente para indisponibilidades com evento `online` (encerradas). **DI-4 aprovada:** a recuperação entra no período quando `b_k ∈ P`. `MTTR = média dos R_k`. Unidade: minutos. Filtros: período, Loja histórica da recuperação e Totem. Indisponibilidades abertas não entram na média e são informadas em contagem própria. Sem recuperação elegível, o indicador é indisponível, não zero.

**Exemplo (sintético, opção A):** `(62 + 40) / 2 = 51 min`. Opção B: `(47 + 25) / 2 = 36 min`.

**Cenários de teste:** recuperação dentro do período; indisponibilidade aberta (fora da média); indisponibilidade iniciada antes de `t0` e encerrada em `P`; chamado ainda aberto após recuperação (não afeta MTTR).

## I4. SLA

Base: tempo de SLA consumido `C_c(t)` definido em `sla-resolucao-encerramento` (soma do tempo nos estados que contam SLA, desde `criado_em`, a partir da linha do tempo de status). `S_c = sla_horas_aplicado` do chamado.

- **Consumo percentual:** `U_c(t) = C_c(t) / S_c`.
- **Faixas (sustentadas pelo domínio §12):** `U < 70%` normal; `70% ≤ U ≤ 90%` risco; `90% < U ≤ 100%` crítico; `U > 100%` violado.
- **Cumprimento no período:** `Cumpr = |{c ∈ B : C_c(t_fim_c) ≤ S_c}| / |B|`, onde `t_fim_c` é a entrada no estado de parada vigente (`Resolvido` ou `Encerrado`) e `B` é o conjunto de chamados cujo `t_fim_c ∈ P`, excluindo `Cancelado` (**DS-2 aprovada**). Chamado rejeitado depois do período é recalculado na próxima resolução, sem duplicar o chamado no mesmo recorte.
- **Tempo:** corrido (DS-1 aprovada).
- Unidade: horas e percentual. Filtros: período, Loja, Categoria, Prioridade.
- **Não calculável:** chamado sem `criado_em` ou `sla_horas_aplicado`, ou cuja linha do tempo de status não reconstrói o status atual (ver `sla-resolucao-encerramento`); excluído e contado.

**Exemplo (sintético):** `S = 4 h`, criado 08:00 em `Novo`; 08:30 → `Em Atendimento`; 10:00 → `Resolvido`; 13:00 → `Solução Rejeitada`; 14:00 → `Em Atendimento`; 15:00 → `Resolvido`. `C = 2 h (08:00–10:00) + 2 h (13:00–15:00) = 4 h`; o período 10:00–13:00 em `Resolvido` não conta; `U = 100%` (crítico, cumprido). Se a segunda resolução fosse às 15:30, `C = 4,5 h`, `U = 112,5%` (violado).

**Cenários de teste:** sem pausas; uma pausa e rejeição; múltiplas pausas; `Encerrado` direto pelo Save; `Cancelado`; troca de Categoria (novo `S`, mesma referência inicial); chamado não calculável; limites exatos de 70%, 90% e 100%.

## I5. Recorrência

**Finalidade:** repetição de chamados da mesma Categoria (referência de causa, domínio §8 e §13). Título, descrição ou outro campo NÃO substituem a Categoria.

Chamado `c` é **recorrente** se existe chamado elegível `c'` com a mesma Categoria e o mesmo Totem (**DR-2 aprovada**) e `criado_em(c') ∈ [criado_em(c) − J, criado_em(c))`.

- `J = 30` dias corridos (**DR-1 aprovada**).
- Conjunto base `N`: chamados com `criado_em ∈ P`, Categoria e Totem preenchidos, classificação `Incidente` e status diferente de `Cancelado` (**DR-3 aprovada**). O predecessor `c'` obedece aos mesmos critérios de classificação, status e dados mínimos, mas pode ter sido criado antes de `t0`.
- `Taxa = |recorrentes ∈ N| / |N|`; complementarmente, contagem de recorrências por Categoria (Pareto).
- Chamados sem Categoria ou Totem: excluídos e contados. Filtros: período, Loja histórica na abertura, Totem e Categoria. A transferência de Loja não altera o agrupamento por Totem; sem Loja histórica, o chamado não entra no recorte de Loja, mas continua elegível nos recortes por Totem ou rede.

**Exemplo (sintético):** T1, Categoria "Totem Offline / Sem Heartbeat", chamados em 01/10, 05/10 e 20/10. `J = 7` dias: só 05/10 é recorrente → `1/3 = 33,3%`. `J = 30` dias: 05/10 e 20/10 → `2/3 = 66,7%`.

**Cenários de teste:** chamado exatamente no limite da janela; Categorias diferentes no mesmo Totem (não recorrentes); mesmo Totem em Lojas diferentes após transferência do Totem (agrupamento por Totem); chamado cancelado conforme DR-3.

## Decisões

**Aprovada (2026-11-04):** DS-1 — SLA em tempo corrido. Tempo útil não é usado por nenhum indicador.

**Aprovadas em 2026-11-08 pela responsável pelo projeto** (exemplos com dados sintéticos; nenhum valor vem de dados reais):

| ID | Pergunta | Alternativas | Exemplo numérico | Impacto |
|---|---|---|---|---|
| DI-1 | Marcos de início e fim da indisponibilidade | Telemetria → telemetria | T1 do exemplo I1: 62 min (Disp 95,69%); detecção → detecção daria 47 min (96,74%) | Disponibilidade e MTTR |
| DI-2 | Marco inicial do MTTD | Última telemetria | Exemplo I2: 19 min; descontar o limite de heartbeat daria 4 min | MTTD inclui o limite de heartbeat |
| DI-3 | Data inicial confiável do histórico de disponibilidade | 05/10/2026 00:00 `America/Sao_Paulo` | Período de 01/10 a 31/10: o denominador começa em 05/10 | Períodos anteriores ficam fora do cálculo |
| DI-4 | Atribuição do MTTR ao período | Pela recuperação | Indisponibilidade de 31/10 23:50 a 01/11 00:20 entra em novembro | Indisponibilidades que cruzam períodos |
| DI-5 | Agregação por Loja e rede | Ponderada por tempo observado | T1: 62 min em 1.440 min; T3: 30 min em 120 min. Rede: `1 − 92/1.560 = 94,10%` | Totens com períodos observáveis diferentes |
| DS-2 | Base do cumprimento de SLA | Excluir `Cancelado` | 10 resolvidos (8 no prazo) e 2 cancelados: 8/10 = 80% | Percentual de cumprimento |
| DR-1 | Janela de recorrência | 30 dias corridos | Exemplo I5: 2/3 = 66,7%; em 7 dias seria 1/3 = 33,3% | Taxa de recorrência |
| DR-2 | Unidade de agrupamento | Mesmo Totem e mesma Categoria | Chamados de dois Totens da mesma Loja não se tornam recorrentes entre si | Sensibilidade do indicador |
| DR-3 | Chamados incluídos | Somente `Incidente`, sem `Cancelado` | Requisições e Cancelados ficam fora do numerador, denominador e busca de predecessor | Recorrência de requisições e de chamados cancelados |

## Casos de referência para validação

Os valores abaixo são sintéticos e foram conferidos contra as fórmulas acima. Datas sem fuso explícito são interpretadas em `America/Sao_Paulo`; resultados percentuais usam duas casas. Eles definem entradas e saídas esperadas para a futura implementação, sem substituir o teste sobre dados reais.

| Indicador e caso | Entrada relevante | Resultado esperado |
|---|---|---|
| Disponibilidade de T1 | `P` de 20/10 00:00 a 21/10 00:00; `offline` referenciado às 10:00; `online` referenciado às 11:02; observação integral | 62 min indisponíveis em 1.440 min; **95,69%** |
| Disponibilidade da rede | T1 acima; T2 com 40 min indisponíveis e 1.440 min observados no mesmo período | `(1 − 102/2.880) × 100` = **96,46%**; média ponderada |
| Corte histórico DI-3 | `P` de 01/10 00:00 a 06/10 00:00; primeira telemetria em 03/10; 60 min Offline em 05/10 | Período observável começa em 05/10 00:00; 60/1.440 min; **95,83%** |
| MTTD | Dois eventos `offline` detectados dentro de `P`: última telemetria às 10:00 e 14:00; detecção às 10:18 e 14:20 | `(18 + 20)/2` = **19 min**, sem subtrair o limite de heartbeat |
| MTTR | Dois pares fechados com 62 e 40 min; `online` dentro de `P`; outro par ainda Offline | `(62 + 40)/2` = **51 min**; 1 indisponibilidade aberta informada fora da média |
| Cumprimento de SLA | 10 chamados resolvidos no período, 8 com `C ≤ S`; 2 Cancelados | **80%**; base 10, excluídos 2 Cancelados |
| Consumo após rejeição | Chamado de SLA 4 h: 08:00 Novo, 10:00 Resolvido, 13:00 Solução Rejeitada, 15:00 Resolvido | `C = 4 h`, `U = 100%`, faixa **crítico**; 3 h em Resolvido não contam |
| Recorrência | Incidentes não cancelados do mesmo Totem e Categoria criados em 01/10, 05/10 e 20/10; `P` contém os três | 05/10 e 20/10 recorrentes; `2/3` = **66,67%** |
| Recorrência entre Totens | Dois Incidentes da mesma Categoria e Loja em Totens distintos, dentro de 30 dias | **0/2 = 0%**; o agrupamento é por Totem |
| Média sem eventos | Nenhuma detecção `offline` ou recuperação `online` elegível em `P` | MTTD e MTTR **indisponíveis**, não zero |

## Risks / Trade-offs

- [Histórico de status começa no Save operacional] → SLA de chamados com transições anteriores fica não calculável e é contado separadamente.
- [Cadência do Fiscal] → a opção B de DI-1 e DI-2 depende do intervalo de 300 s; a opção A não depende.
- [Exemplos sintéticos] → nenhum número desta change foi obtido de dados reais; a validação com dados reais exige consulta autorizada ao Xano.
