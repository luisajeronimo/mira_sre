# Validação somente leitura com dados reais — 2026-11-08

## Fonte e execução

Foi consultado o workspace Xano `152692`, branch `v1`, com `xano workspace pull --records`, sem escrita. O cálculo amostral foi feito localmente sobre os registros recebidos. Nenhum dado pessoal, mensagem ou credencial é reproduzido aqui. Período: de `2026-10-05 00:00 America/Sao_Paulo` até `2026-11-08 22:00 UTC`, com fim exclusivo. A publicação de indicadores e o teste de endpoints não foram executados por esta change.

## Resultados

| Indicador | Resultado da consulta | Classificação |
|---|---|---|
| Disponibilidade | 148 transições para 16 Totens. Em 81 transições, a telemetria referenciada não está mais presente; há 28 pares consecutivos do mesmo estado, afetando 13 Totens. | **Não calculável com confiança** para a rede neste retrato. Os intervalos afetados não podem ser tratados como tempo Online por exclusão apenas do numerador. Nenhum percentual agregado foi aprovado. |
| MTTD | 56 eventos Offline detectados no período; 40 com referência válida e duração não negativa; 16 sem telemetria referenciada. Média dos 40 válidos: **6.556,78 min**. | Cálculo amostral passou; 16 exclusões precisam constar no resultado. O valor alto decorre dos timestamps persistidos e não foi corrigido por inferência. |
| MTTR | 5 pares Offline → Online com marcos válidos e recuperação no período; média **2.840,55 min**. | Cálculo amostral passou apenas para os pares válidos; outras sequências não podem ser completadas por inferência. |
| Cumprimento de SLA | 1 chamado Resolvido com transição auditável, consumo de **1,72 h** contra SLA de **2 h**: **1/1 = 100%**. | Cálculo amostral passou; não exercita rejeição, cancelamento ou múltiplas resoluções. |
| Recorrência | 5 Incidentes não cancelados com Totem e Categoria no período; nenhum tem predecessor elegível nos 30 dias anteriores: **0/5 = 0%**. | Cálculo amostral passou; casos positivos continuam cobertos apenas pelos exemplos sintéticos. |

## Pendência de qualidade dos dados

A fórmula de disponibilidade está definida para históricos consistentes. Neste retrato, simplesmente ignorar um intervalo Offline com referência ausente e manter todo o seu tempo no denominador produziria disponibilidade artificialmente alta. A responsável aprovou que qualquer Totem incluído com histórico necessário inválido deixa indisponível o agregado da Loja ou rede do recorte; não se publica percentual parcial. Entre as 83 transições detectadas no período, 16 têm referência de telemetria ausente. A causa da ausência das referências ainda precisa ser investigada antes da implementação da consulta. Não houve limpeza nem alteração de registros.

As médias e percentuais acima são uma conferência local de fórmulas sobre amostras elegíveis; não representam endpoint publicado ou aprovação da qualidade da série histórica.
