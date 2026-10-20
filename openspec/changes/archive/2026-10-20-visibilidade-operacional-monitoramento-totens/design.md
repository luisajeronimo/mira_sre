# Design

## Context

Ver [proposal.md](proposal.md) e o delta da capability `monitoramento-disponibilidade-totens`. Hoje `GET /monitoramento/ativos` retorna somente identificação, tipo e `status_atual`; a página Reflex usa esses campos para os três totais e uma lista simples. Os fatos necessários já existem em `ativos_referencia`, `telemetria_equipamentos`, `historico_disponibilidade_totens` e `chamados`.

O Xano continua sendo a autoridade do estado e das transições; o Fiscal pode não estar em execução. A solução é apenas de leitura e deve caber no plano Free: funções, endpoints autenticados e consultas simples às tabelas atuais.

## Goals / Non-Goals

**Goals:**

- Tornar os fatos persistidos de um Totem legíveis na jornada operacional, sem criar estado derivado no Reflex.
- Oferecer uma listagem de baixo custo de leitura e um único detalhe sob demanda, com limites explícitos de 10 registros por coleção.
- Tornar a origem dos dados clara: transições são decisões persistidas do Xano; incidentes são chamados automáticos de heartbeat efetivamente registrados.

**Non-Goals:**

- Não alterar schemas, índices, dados existentes, o endpoint genérico de telemetria, Fiscal, Simulator ou a regra de 15 minutos/300 segundos.
- Não consultar ou representar execução do Fiscal, nem usar ausência de dados para inferir indisponibilidade.
- Não introduzir dashboard executivo, agregações, gráficos, paginação, filtros, métricas persistidas ou indicadores derivados.

## Decisions

### Dois contratos de leitura, com a autorização já consolidada

Será evoluído o contrato atual `GET /monitoramento/ativos` e criado somente `GET /monitoramento/ativos/{ativos_referencia_id}`. Ambos reutilizam a exigência de perfil de monitoramento existente no Xano antes das leituras; não reutilizam nem alteram o endpoint genérico de telemetria.

O primeiro evita carregar históricos para todos os Totens e responde:

```text
{items: [{
  id, nome_ativo, tipo, loja: {id, nome} | null, status_atual,
  ultima_telemetria_em: timestamp | null,
  ultima_transicao_disponibilidade_em: timestamp | null
}]}
```

O segundo valida a existência do Totem e responde:

```text
{
  totem: {id, nome_ativo, tipo, loja: {id, nome} | null, status_atual},
  ultima_telemetria: {id, evento_timestamp, uso_cpu, uso_memoria, temperatura, status_rede} | null,
  telemetrias: [{id, evento_timestamp, uso_cpu, uso_memoria, temperatura, status_rede}],
  transicoes_disponibilidade: [{id, status, detectado_em, heartbeat_limite_minutos}],
  incidentes_automaticos: [{id, titulo, status, prioridade, criado_em, ultima_atualizacao_em, categoria: {id, nome}}]
}
```

As consultas de detalhe filtram pelo Totem e usam, respectivamente, `evento_timestamp`, `detectado_em` e `criado_em` em ordem decrescente, com `limit 10`. A última telemetria é a primeira da coleção ordenada, devolvida também como atalho. Incidentes são filtrados por Totem, `origem = automatico`, `criador_sistema = bot_fiscalizacao` e a categoria `Totem Offline / Sem Heartbeat`; não há `chamado_id` em uma transição, portanto os dois conjuntos não serão ligados entre si.

Alternativa considerada: uma única resposta com todos os históricos de todos os Totens. Foi descartada por trazer dados desnecessários e tornar a demonstração menos simples. A alternativa de criar endpoint genérico de telemetria foi descartada porque sua autorização não é o contrato consolidado do monitoramento.

### Dados lidos diretamente, sem nova persistência

O resumo obtém a última telemetria e a última transição somente para apresentação. O detalhe lê as tabelas existentes sem escrita, job, backfill, log de polling ou métrica calculada. `status_atual` é sempre lido de `ativos_referencia`; o frontend apenas conta e apresenta esse valor.

Consultas simples e limitadas são compatíveis com os recursos já usados no Xano Free. Não há dependência de agregação paga, worker, cron ou serviço adicional.

### Master-detail desktop com componentes existentes

Após os cards de total, Online e Offline, a página terá um grid desktop: à esquerda, a lista/tabela de Totens com os cinco campos do resumo; à direita, o painel do item selecionado. A seleção chama somente o contrato de detalhe e mantém `/monitoramento`. O painel reutiliza cards, badges, textos, callouts, spinner e links já presentes no Reflex; cada incidente aponta para `/chamados/{id}`.

O painel organiza: cabeçalho do Totem e Loja, estado persistido, última telemetria, histórico de telemetrias, eventos de disponibilidade e incidentes automáticos. Cada seção vazia usa callout textual. Enquanto nenhum Totem tiver sido selecionado, o painel mostra orientação neutra para seleção, sem dados de exemplo. Erros de listagem e de detalhe usam a mensagem real já tratada pelo cliente, sem limpar ou inventar o último dado válido.

CPU e memória são apresentados como os valores numéricos recebidos com o sufixo `%`; temperatura usa o sufixo `°C`; e cada `heartbeat_limite_minutos` usa o sufixo textual `minutos`. São apenas sufixos de apresentação: não há conversão, arredondamento, cálculo ou regra de precisão. `status_rede` é apresentado como valor recebido. Não haverá semáforo de saúde, limiar, classificação ou ação sugerida.

Alternativa considerada: drawer, nova rota ou interface móvel para o detalhe. Foi descartada porque o MIRA é desktop e o requisito aprova o painel na mesma página.

### Linguagem de evidência operacional

A UI nomeia a coleção como “Eventos de disponibilidade registrados” e a descreve como fatos de transição persistidos pelo Xano. Os chamados aparecem como “Incidentes automáticos de heartbeat”. Não são usadas frases como “Fiscal ativo”, “última execução”, “fiscalização atrasada” ou “esta transição gerou este chamado”. Assim, um período sem execução do Fiscal não recebe interpretação visual.

## Risks / Trade-offs

- [Dados históricos ausentes por Fiscal desligado] → exibir somente `null` e coleções vazias; não inferir estado nem preencher lacunas.
- [Relacionamento Loja ausente em registro legado] → contrato retorna `loja: null` e a interface informa ausência de Loja, sem fabricar identificação.
- [Sem vínculo direto entre transição e chamado] → manter as seções independentes e não criar correlação visual causal.
- [Consultas extras para o resumo por Totem] → limitar o detalhe a seleção sob demanda e manter o conjunto de dados acadêmico; se o volume crescer, uma nova change deve avaliar otimização sem mudar o contrato atual.

## Migration Plan

1. Aplicar primeiro as funções e os dois contratos de leitura no Xano, preservando a resposta encapsulada em `items` da listagem.
2. Atualizar os DTOs, cliente, estado e página Reflex para os campos adicionais e seleção do detalhe.
3. Validar os contratos com dados existentes e as coleções vazias; não há migração, alteração de tabela ou backfill.
4. Em rollback, restaurar a página e a função de listagem anteriores e remover apenas o novo contrato de detalhe, sem tocar em telemetria, histórico ou chamados persistidos.

## Open Questions

Nenhuma. Os valores numéricos preservam o valor recebido e usam apenas os sufixos de apresentação aprovados (`%`, `°C` e `minutos`), sem conversão, arredondamento ou indicador derivado; os limites e as ordens foram aprovados para esta change.
