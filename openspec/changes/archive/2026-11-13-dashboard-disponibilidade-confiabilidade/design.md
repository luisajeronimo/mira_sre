# Design

## Context

Ver `proposal.md` e os deltas desta change. `indicadores-operacionais` já aprova fórmulas, marcos, fuso, corte histórico e falha fechada da disponibilidade; `monitoramento-disponibilidade-totens` e `vinculo-historico-totem-loja` preservam os fatos necessários. Hoje `/inicio` da Diretoria usa a jornada global de chamados; não há dashboard nem endpoint de indicadores. A sidebar enumera explicitamente os destinos por perfil. A referência `docs/design/references/diretoria-dashboard.png` orienta apenas composição visual, não dados nem outras métricas.

## Goals / Non-Goals

**Goals:** consulta reproduzível e autorizada; uma única definição dos cálculos no Xano; série diária e totais coerentes; resposta explícita para ausência e inconsistência; verificação por casos sintéticos conhecidos e, quando possível, dados reais.

**Non-Goals:** materialização de métricas, novo agendador, cálculo no Reflex, métricas de chamados, exportação, mudança de dados históricos ou da detecção pelo Fiscal.

## Decisions

### D1. Contratos dedicados e autorização no Xano

Criar `GET /indicadores/disponibilidade-confiabilidade` para agregados e série e `GET /indicadores/disponibilidade-confiabilidade/filtros` para catálogos mínimos de Loja e Totem, ambos no grupo autenticado do Service Desk. Usar a identidade de `auth` e a autorização central exigindo Diretoria sem troca pendente, antes de ler fatos. IDs e período chegam como filtros, nunca como autorização. Uma consulta direta de outro perfil recebe 403. Isso evita reutilizar GETs genéricos que expõem fatos brutos ou conceder acesso por mera visibilidade da rota.

### D2. Agregação sob demanda e resposta pequena

O Xano busca os Totens pertinentes, sua primeira telemetria, transições necessárias antes e dentro de `[t0,t1)`, telemetrias referenciadas e vínculos históricos que intersectam o período. Índices compostos por Totem e timestamp auxiliam as leituras da primeira telemetria e dos eventos ordenados. Ordena por Totem e instante, valida pares, intersecta intervalos com o período observável e reparte apenas o tempo comprovado por Loja. Usa acumuladores de soma e contagem para totais e dias, sem média de percentuais ou de médias diárias. O retorno contém valores finais, denominadores, contagens de exclusão/inconsistência, período efetivo, filtros efetivos e até um ponto por dia. Não retorna eventos brutos ao Reflex e não grava percentuais, durações ou médias. A alternativa de pré-calcular em tabela ou no frontend exigiria nova persistência ou deslocaria a regra de negócio.

### D3. Marcos e atribuição temporal

- Disponibilidade: `a = evento_timestamp` da telemetria do Offline e `b = evento_timestamp` da telemetria do Online; aberto termina em `t1`. O início observável de cada Totem é `max(t0, primeira_telemetria, 05/10/2026 00:00 America/Sao_Paulo)`. O numerador e denominador seguem `indicadores-operacionais`, inclusive invalidação do agregado por histórico necessário inválido.
- MTTD: evento Offline entra pelo dia de `detectado_em`; diferença entre detecção e telemetria referenciada, sem descontar 15 minutos.
- MTTR: par entra pelo dia do `evento_timestamp` de retorno Online; diferença entre os timestamps das telemetrias dos eventos Offline e Online. Pares abertos ficam em contagem separada.
- A Loja de MTTD é a comprovada em `detectado_em`; a de MTTR, na recuperação. A disponibilidade de Loja reparte tanto tempo observado quanto indisponível nos segmentos de vínculo comprovado. A rede não depende de Loja comprovada. Nenhum trecho sem prova de Loja é imputado à Loja atual.
- Se o evento Online não tem `evento_timestamp` da telemetria referenciada, ele fica fora da média de MTTR. A inconsistência usa `detectado_em` somente para inclusão no período, ponto diário e Loja comprovada nesse instante. Transferência posterior não desloca a contagem; `detectado_em` não substitui o marco de recuperação.

### D4. Período e série aprovados

O recorte inicial usa o início do dia local 29 dias antes da data atual como `t0` e o instante da consulta como `t1`: 30 datas civis, com a última parcial. Cada ponto diário usa a interseção de seu dia local com `[t0,t1)`, inclusive em dias de mudança de horário, e médias próprias por eventos elegíveis do dia. Ao alterar o período, a página refaz a consulta e descarta resposta tardia de filtros anteriores. Não interpolar lacunas. A responsável pelo projeto confirmou esta decisão em 12/11/2026.

Os atalhos “Últimos 30 dias” e “Hoje” ficam em controle segmentado no cabeçalho, como na referência visual. “Últimos 30 dias” calcula `t1` no clique. “Hoje” usa 00h locais como `t0` e o próximo 00h exclusivo como `t1`, cobrindo até 23h59 do dia selecionado. O instante efetivamente observável é capturado uma vez na consulta; ele limita totais e a hora em andamento, enquanto as horas futuras permanecem sem valor. Datas personalizadas permanecem em controle secundário. A seleção ativa é explícita e não há polling ou promessa de tempo real.

Para diferenciar Hoje de um período personalizado de um dia, a mesma API aceita o parâmetro opcional `visao=hoje`. O Xano só aceita essa visão quando `t0` e `t1` delimitam o dia civil atual completo em `America/Sao_Paulo`; a exceção a `t1 <= now` vale apenas nessa condição. A resposta preserva os agregados e a série diária existentes e acrescenta, somente na visão Hoje, `disponibilidade_horaria` com `observado_ate` e 24 posições `{inicio, fim, percentual, observado_ms, indisponivel_ms, totens_invalidos}`. O cliente tipado valida a presença e os limites dessa estrutura antes de apresentá-la; outras visões seguem o contrato vigente sem a série horária.

Cada posição horária usa `[inicio, fim)`, com o limite de observação reduzido a `observado_ate` para a hora corrente e nenhum tempo imputado às horas futuras. A agregação pondera soma de tempo indisponível pela soma de tempo observável dos Totens elegíveis; ausência de observação ou histórico necessário inválido torna o percentual nulo. O cálculo reaproveita os fatos já consultados, a lógica de intervalo e o vínculo histórico de Loja, sem nova consulta por hora, persistência ou recurso pago. Medir a latência com dados reais antes da publicação, pois o processamento de até 24 faixas aumenta o trabalho por consulta.

### D5. Rota e apresentação

Adicionar `/indicadores/disponibilidade` como rota canônica da Diretoria e item `Indicadores` na configuração central da sidebar; manter `/inicio` como jornada de chamados. Na página executiva compartilhada, a aba Disponibilidade aparece logo abaixo do breadcrumb e contém apenas seus filtros, painéis, gráfico e listagem; a aba Chamados/SLA é descrita na change própria. State e cliente HTTP validam a estrutura da resposta e formatam valores, mas não derivam métricas. A página mostra disponibilidade em percentual, MTTD/MTTR com unidade explícita, filtros e contagens. Para Hoje, o gráfico apresenta a disponibilidade horária da rede com eixo completo de 00h a 23h e horas futuras sem dado; os cards de MTTD/MTTR continuam referentes ao dia. Para os demais períodos, mantém a curva diária comparativa de MTTD/MTTR com pontos ausentes explícitos. As curvas usam preenchimento suave como na referência visual, com legenda permanente que identifica MTTD e MTTR por nome e significado. O balão de valores fica contido na área do gráfico, sem criar barras de rolagem ao passar o mouse. A listagem diária segue a data mais recente primeiro e separa médias, quantidade de eventos e inconsistências em colunas legíveis, com cabeçalho e linhas no padrão visual da referência; sua altura acompanha o conteúdo, sem rolagem vertical interna. Reutilizar a casca, tokens e padrões do `DESIGN.md`; elementos ilustrativos do PNG como SLA, volumetria e ações de exportação não são implementados por esta change.

## Risks / Trade-offs

- [Consulta sob demanda pode custar caro com histórico crescente] → consultar por período e IDs, evitar consulta por dia ou evento no frontend, medir latência e volume em dados reais e revisar o desenho antes de ampliar escopo se o plano Free não suportar a carga.
- [Primeira telemetria e estado anterior a `t0` exigem leitura histórica] → buscar os marcos anteriores necessários; testar início de período, Totem recém-observado e Offline aberto.
- [Histórico de Loja legado incompleto] → não inferir Loja atual; devolver trechos indeterminados em contagem e preservar a visão da rede conforme a spec vigente.
- [Respostas fora de ordem após mudança de filtros] → associar cada requisição ao snapshot dos filtros e apresentar somente o resultado correspondente.
- [Médias sem evento e disponibilidade inválida] → valores nulos com motivo e contagens explícitas, não zero nem 100 presumidos.

## Migration Plan

Validar XanoScript e testes nativos, revisar `xano workspace push --dry-run`, publicar seletivamente os contratos novos, executar novo dry-run e verificar acesso direto de todos os perfis. Depois integrar o cliente, State, página e navegação Reflex. Como não há alteração de dados persistidos, rollback consiste em retirar a rota e os contratos novos sem reescrever histórico; a remoção remota requer revisão específica antes de execução.

## Decisões humanas

- Em 12/11/2026, a responsável confirmou acesso somente da Diretoria e a evolução diária dos últimos 30 dias civis.
- Em 12/11/2026, a responsável determinou desconsiderar as referências de planejamento “2” e “D4”.
- Em 12/11/2026, a responsável confirmou que a inconsistência de um Online sem timestamp de telemetria pertence ao dia e à Loja historicamente comprovada em `detectado_em`, sem deslocamento após transferência.
- Em 12/11/2026, a responsável confirmou atalhos “Últimos 30 dias” e “Hoje” com consulta ao clique, sem atualização automática.
