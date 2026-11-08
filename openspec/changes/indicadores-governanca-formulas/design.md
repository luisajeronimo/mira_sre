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

Notação: período de análise `P = [t0, t1)`; `|I|` é a duração de um intervalo; datas de corte do período no fuso `America/Sao_Paulo` (o mesmo usado pelos filtros do Reflex); todos os timestamps em milissegundos UTC como persistidos.

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

| Marco | Opção A (recomendada) | Opção B |
|---|---|---|
| Início `a_k` | `evento_timestamp` da telemetria referenciada pelo evento `offline_k` (última prova de funcionamento) | `detectado_em` do evento `offline_k` |
| Fim `b_k` | `evento_timestamp` da telemetria referenciada pelo evento `online_k` (primeira prova de retorno) | `detectado_em` do evento `online_k` |

A opção A mede a indisponibilidade estimada pela telemetria e é independente da cadência do Fiscal; a B mede a indisponibilidade reconhecida pelo sistema e subestima o início em pelo menos 15 minutos. Os mesmos marcos DEVEM ser usados em I1 e I3 (decisão **DI-1**).

**Período observável** `O_i = [max(t0, h0, f_i), t1)`, onde `f_i` é a primeira telemetria do Totem e `h0` é o início confiável do histórico de disponibilidade (implantação de `2026-10-04-monitoramento-heartbeat-incidentes-automaticos`; data exata de publicação a confirmar — decisão **DI-3**). Totem sem telemetria não tem período observável e é excluído.

**Fórmula:**

```
Indisp_i = Σ_k | [a_k, b_k) ∩ O_i |          (intervalo aberto: b_k = min(t1, agora))
Disp_i   = 1 − Indisp_i / |O_i|               (em %, duas casas)
Disp_Loja ou Disp_rede = 1 − Σ_i Indisp_i / Σ_i |O_i|   (ponderada por tempo — decisão DI-5)
```

Numerador: tempo indisponível; denominador: tempo observável. Unidade: percentual. Filtros: período, Loja, Totem.

**Estado no início do período:** determinado pelo último evento anterior a `t0`; se o primeiro evento em `P` for `online`, o Totem estava indisponível desde `t0`.

**Dados ausentes ou inconsistentes** (excluídos do cálculo e contados no resultado como inconsistências, nunca preenchidos):

- telemetria referenciada inexistente ou sem `evento_timestamp` (opção A);
- dois eventos consecutivos do mesmo estado;
- `b_k < a_k`.

**Exemplo (dados sintéticos):** `P` = 20/10 00:00–21/10 00:00 (1.440 min). Totem T1: `offline` com telemetria de 10:00 e `detectado_em` 10:18; `online` com telemetria de 11:02 e `detectado_em` 11:05. Opção A: 62 min → `Disp = 1 − 62/1440 = 95,69%`. Opção B: 47 min → `96,74%`. Totem T2 (mesmo período): telemetria 14:00 / detecção 14:20; retorno 14:40 / 14:45. Opção A: 40 min → `97,22%`. Rede ponderada (A): `1 − 102/2880 = 96,46%`.

**Cenários de teste:** sem eventos (100%); indisponibilidade cruzando `t0` ou `t1`; intervalo aberto até `agora`; Totem criado no meio do período; Totem sem telemetria (excluído); eventos inconsistentes (excluídos e contados); opções A e B com os mesmos dados.

## I2. MTTD — Mean Time to Detect

**Finalidade:** tempo entre o início identificável da indisponibilidade e sua detecção pelo MIRA.

| Opção | Fórmula por evento `offline_k` | Leitura |
|---|---|---|
| A (recomendada) | `D_k = detectado_em(offline_k) − evento_timestamp(telemetria_referencia(offline_k))` | Tempo total até o sistema reconhecer a falha; por construção `D_k > 15 min` |
| B | `D_k = detectado_em(offline_k) − (evento_timestamp + heartbeat_limite_minutos)` | Somente a latência da verificação após vencido o limite (0–5 min com Fiscal a 300 s) |

Decisão **DI-2**. `MTTD = média dos D_k` dos eventos `offline` com `detectado_em ∈ P`. Unidade: minutos. Filtros: período, Loja, Totem. Eventos sem telemetria de referência válida são excluídos e contados.

**Exemplo (sintético, opção A):** T1 `10:18 − 10:00 = 18 min`; T2 `14:20 − 14:00 = 20 min`; `MTTD = 19 min`. Opção B: 3 e 5 min; `MTTD = 4 min`.

**Cenários de teste:** um evento; vários eventos; evento sem telemetria de referência; período sem eventos (indicador indisponível, não zero).

## I3. MTTR — Mean Time to Repair/Recover

**Finalidade (sustentada pelo domínio §13):** tempo médio de recuperação do Totem; não é tempo de encerramento do chamado.

`R_k = b_k − a_k` com os marcos de DI-1, somente para indisponibilidades com evento `online` (encerradas). Atribuição ao período (decisão **DI-4**): por `b_k ∈ P` (recomendada: recuperações concluídas no período) ou por `a_k ∈ P`. `MTTR = média dos R_k`. Unidade: minutos. Indisponibilidades abertas não entram na média e são informadas em contagem própria.

**Exemplo (sintético, opção A):** `(62 + 40) / 2 = 51 min`. Opção B: `(47 + 25) / 2 = 36 min`.

**Cenários de teste:** recuperação dentro do período; indisponibilidade aberta (fora da média); indisponibilidade iniciada antes de `t0` e encerrada em `P`; chamado ainda aberto após recuperação (não afeta MTTR).

## I4. SLA

Base: tempo de SLA consumido `C_c(t)` definido em `sla-resolucao-encerramento` (soma do tempo nos estados que contam SLA, desde `criado_em`, a partir da linha do tempo de status). `S_c = sla_horas_aplicado` do chamado.

- **Consumo percentual:** `U_c(t) = C_c(t) / S_c`.
- **Faixas (sustentadas pelo domínio §12):** `U < 70%` normal; `70% ≤ U ≤ 90%` risco; `90% < U ≤ 100%` crítico; `U > 100%` violado.
- **Cumprimento no período:** `Cumpr = |{c ∈ B : C_c(t_fim_c) ≤ S_c}| / |B|`, onde `t_fim_c` é a entrada no estado de parada vigente (`Resolvido` ou `Encerrado`) e `B` é o conjunto de chamados cujo `t_fim_c ∈ P`. Inclusão de `Cancelado` e de reaberturas posteriores: decisão **DS-2** (recomendado: excluir `Cancelado`; chamado rejeitado depois do período é recalculado na próxima resolução).
- **Tempo:** corrido (DS-1 aprovada).
- Unidade: horas e percentual. Filtros: período, Loja, Categoria, Prioridade.
- **Não calculável:** chamado sem `criado_em` ou `sla_horas_aplicado`, ou cuja linha do tempo de status não reconstrói o status atual (ver `sla-resolucao-encerramento`); excluído e contado.

**Exemplo (sintético):** `S = 4 h`, criado 08:00 em `Novo`; 08:30 → `Em Atendimento`; 10:00 → `Resolvido`; 13:00 → `Solução Rejeitada`; 14:00 → `Em Atendimento`; 15:00 → `Resolvido`. `C = 2 h (08:00–10:00) + 2 h (13:00–15:00) = 4 h`; o período 10:00–13:00 em `Resolvido` não conta; `U = 100%` (crítico, cumprido). Se a segunda resolução fosse às 15:30, `C = 4,5 h`, `U = 112,5%` (violado).

**Cenários de teste:** sem pausas; uma pausa e rejeição; múltiplas pausas; `Encerrado` direto pelo Save; `Cancelado`; troca de Categoria (novo `S`, mesma referência inicial); chamado não calculável; limites exatos de 70%, 90% e 100%.

## I5. Recorrência

**Finalidade:** repetição de chamados da mesma Categoria (referência de causa, domínio §8 e §13). Título, descrição ou outro campo NÃO substituem a Categoria.

Chamado `c` é **recorrente** se existe `c'` com a mesma Categoria e a mesma unidade de agrupamento `G` (decisão **DR-2**: Totem, recomendado, ou Loja) e `criado_em(c') ∈ [criado_em(c) − J, criado_em(c))`.

- `J`: janela (decisão **DR-1**; exemplos: 7 ou 30 dias corridos).
- Conjunto base `N`: chamados com `criado_em ∈ P` e Categoria e Totem preenchidos; inclusão de `Cancelado` e de `Requisição` (decisão **DR-3**; recomendado: somente `Incidente`, excluindo `Cancelado`).
- `Taxa = |recorrentes ∈ N| / |N|`; complementarmente, contagem de recorrências por Categoria (Pareto).
- Chamados sem Categoria ou Totem: excluídos e contados.

**Exemplo (sintético):** T1, Categoria "Totem Offline / Sem Heartbeat", chamados em 01/10, 05/10 e 20/10. `J = 7` dias: só 05/10 é recorrente → `1/3 = 33,3%`. `J = 30` dias: 05/10 e 20/10 → `2/3 = 66,7%`.

**Cenários de teste:** chamado exatamente no limite da janela; Categorias diferentes no mesmo Totem (não recorrentes); mesmo Totem em Lojas diferentes após transferência do Totem (agrupamento por Totem); chamado cancelado conforme DR-3.

## Decisões

**Aprovada (2026-11-04):** DS-1 — SLA em tempo corrido. Tempo útil não é usado por nenhum indicador.

**Pendentes** (exemplos com dados sintéticos; nenhum valor vem de dados reais):

| ID | Pergunta | Alternativas | Exemplo numérico | Impacto |
|---|---|---|---|---|
| DI-1 | Marcos de início e fim da indisponibilidade | A: telemetria → telemetria (recomendada); B: detecção → detecção | T1 do exemplo I1: A = 62 min (Disp 95,69%); B = 47 min (Disp 96,74%) | Disponibilidade e MTTR |
| DI-2 | Marco inicial do MTTD | A: última telemetria (recomendada); B: última telemetria + 15 min | Exemplo I2: A = 19 min; B = 4 min | MTTD inclui ou exclui o limite de heartbeat |
| DI-3 | Data inicial confiável do histórico de disponibilidade | Data de publicação da change `2026-10-04-monitoramento-heartbeat-incidentes-automaticos` (a informar) | Período de 01/10 a 31/10 com histórico válido a partir de 05/10: o denominador começa em 05/10 | Períodos anteriores ficam fora do cálculo |
| DI-4 | Atribuição do MTTR ao período | Pela recuperação (recomendada); pelo início | Indisponibilidade de 31/10 23:50 a 01/11 00:20 (30 min): entra em novembro (fim) ou em outubro (início) | Indisponibilidades que cruzam períodos |
| DI-5 | Agregação por Loja e rede | Ponderada por tempo (recomendada); média simples dos Totens | T1: 62 min em 1.440 min (95,69%); T3, observado só 120 min com 30 min indisponível (75,00%). Ponderada: 1 − 92/1.560 = 94,10%; média simples: 85,35% | Totens com períodos observáveis diferentes |
| DS-2 | Base do cumprimento de SLA | Excluir `Cancelado` (recomendada); incluir | 10 resolvidos (8 dentro do SLA) e 2 cancelados (1 dentro): excluindo = 8/10 = 80%; incluindo = 9/12 = 75% | Percentual de cumprimento |
| DR-1 | Janela de recorrência | 7 dias; 30 dias; outra | Exemplo I5: 7 dias = 33,3%; 30 dias = 66,7% | Taxa de recorrência |
| DR-2 | Unidade de agrupamento | Totem (recomendada); Loja | T1 em 01/10 e T4 (mesma Loja, mesma Categoria) em 03/10, janela 7 dias: por Totem = 0/2 = 0%; por Loja = 1/2 = 50% | Sensibilidade do indicador |
| DR-3 | Chamados incluídos | Somente `Incidente`, sem `Cancelado` (recomendada); todos | Exemplo I5 com o chamado de 05/10 cancelado, janela 7 dias: excluindo = 0/2 = 0%; incluindo = 1/3 = 33,3% | Recorrência de requisições e de chamados cancelados |

## Risks / Trade-offs

- [Histórico de status começa no Save operacional] → SLA de chamados com transições anteriores fica não calculável e é contado separadamente.
- [Cadência do Fiscal] → a opção B de DI-1 e DI-2 depende do intervalo de 300 s; a opção A não depende.
- [Exemplos sintéticos] → nenhum número desta change foi obtido de dados reais; a validação com dados reais exige consulta autorizada ao Xano.
