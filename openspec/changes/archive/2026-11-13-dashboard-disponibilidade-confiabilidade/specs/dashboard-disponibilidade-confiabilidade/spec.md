# Spec Delta

## Purpose

Permitir que a Diretoria acompanhe a disponibilidade da rede e compare a evolução dos tempos de detecção e recuperação com recortes históricos verificáveis.

## ADDED Requirements

### Requirement: Consulta executiva exige Diretoria autenticada
O dashboard e seus contratos de leitura DEVEM (MUST) atender somente à Diretoria com sessão válida e troca de senha concluída. A autorização DEVE (MUST) ser aplicada pelo Xano em cada consulta; a rota protegida e a ocultação visual não concedem acesso.

#### Scenario: Diretoria consulta a rede
- **WHEN** usuário da Diretoria autenticado abre Indicadores ou consulta diretamente seus contratos
- **THEN** recebe dados globais correspondentes aos filtros válidos

#### Scenario: Outros perfis tentam consulta direta
- **WHEN** Gerente, Técnico ou Administrador chama o contrato de indicadores ou abre sua rota
- **THEN** o Xano responde 403 sem dados, e o Reflex não renderiza o dashboard

#### Scenario: Sessão inválida ou troca pendente
- **WHEN** a sessão é ausente, expirada ou possui troca obrigatória pendente
- **THEN** nenhuma métrica é retornada e a interface segue a proteção de sessão vigente

### Requirement: Filtros executivos definem período e escopo histórico
A consulta DEVE (MUST) aceitar período `[t0, t1)` e recortes opcionais por Loja e Totem. Os cortes civis DEVEM (MUST) ser interpretados em `America/Sao_Paulo`, comparados em UTC, e a Loja DEVE (MUST) ser a comprovada no instante de cada fato ou trecho, conforme `indicadores-operacionais`.

#### Scenario: Recorte por Loja e Totem
- **WHEN** a Diretoria aplica Loja e Totem em um período válido
- **THEN** recebe somente os fatos e trechos daquele Totem atribuíveis historicamente à Loja no intervalo, sem usar a Loja atual como substituta

#### Scenario: Totem transferido
- **WHEN** um Totem foi transferido entre Lojas durante o período
- **THEN** o recorte de cada Loja recebe apenas seus trechos comprovados e a visão da rede conserva os fatos do Totem

#### Scenario: Intervalo ou identificador inválido
- **WHEN** `t0 >= t1`, `t1` está no futuro fora da seleção Hoje ou um identificador informado é inválido
- **THEN** o Xano rejeita a entrada sem calcular ou retornar indicadores

#### Scenario: Catálogo de filtros
- **WHEN** a Diretoria abre os filtros
- **THEN** pode identificar Lojas e Totens elegíveis ao recorte histórico, inclusive Totem hoje transferido, sem depender de permissão de uma única Loja

### Requirement: Período inicial e evolução diária são explícitos
Sem seleção do usuário, a página DEVE (MUST) consultar os 30 dias civis que terminam no dia atual, com `t1` no instante da consulta, e representar MTTD e MTTR em pontos por dia civil. O período e a granularidade aplicados DEVEM (MUST) estar visíveis.

#### Scenario: Primeira abertura durante o dia
- **WHEN** a Diretoria abre Indicadores sem filtros prévios
- **THEN** a série contém até 30 datas, incluindo um último dia parcial até `t1`, e a interface informa o período efetivo

#### Scenario: Período selecionado
- **WHEN** a Diretoria aplica outro período válido
- **THEN** totais e série são recalculados para esse período, sem misturar valores da consulta anterior

### Requirement: Atalhos de período consultam ao clique
A página DEVE (MUST) destacar os atalhos “Últimos 30 dias” e “Hoje” no cabeçalho. “Últimos 30 dias” DEVE (MUST) consultar desde o início do dia local 29 dias antes do atual até o instante do clique; “Hoje” DEVE (MUST) selecionar o dia civil inteiro, de 00h até 23h59 locais, representado pelo intervalo semiaberto até o próximo 00h. O Xano DEVE (MUST) aceitar esse limite futuro somente para a seleção explícita Hoje e DEVE (MUST) usar no cálculo apenas fatos e tempo observáveis até o instante da consulta. A troca de atalho DEVE (MUST) preservar os recortes selecionados de Loja e Totem, marcar visual e semanticamente o período ativo e substituir os resultados somente pela nova consulta. A página DEVE (MUST) continuar permitindo a seleção personalizada de datas. Os atalhos NÃO DEVEM (MUST NOT) prometer atualização automática.

#### Scenario: Diretoria consulta Hoje
- **WHEN** a Diretoria seleciona “Hoje” às 14h no fuso `America/Sao_Paulo`
- **THEN** o período selecionado começa às 00h do mesmo dia e termina no próximo 00h exclusivo, mantendo Loja e Totem selecionados; os indicadores não presumem dados das horas futuras

#### Scenario: Diretoria volta aos últimos 30 dias
- **WHEN** a Diretoria seleciona “Últimos 30 dias” após consultar Hoje ou um período personalizado
- **THEN** o período começa às 00h locais 29 dias antes da data atual, termina no instante do clique e o atalho correspondente aparece ativo

#### Scenario: Período personalizado
- **WHEN** a Diretoria edita as datas e aplica o período
- **THEN** nenhum dos atalhos rápidos aparece ativo e os resultados usam as datas informadas

### Requirement: Hoje mostra disponibilidade da rede por hora
Somente quando o atalho Hoje estiver ativo, o Xano DEVE (MUST) devolver 24 posições horárias ordenadas do dia civil selecionado, com início e fim de cada hora, percentual de disponibilidade ponderado pelo tempo observado, durações observável e indisponível e contagem de Totens com histórico necessário inválido. A hora em andamento DEVE (MUST) usar apenas o trecho até o instante da consulta; horas futuras DEVEM (MUST) ter percentual indisponível, sem estimativa. Horas sem tempo observável ou afetadas por histórico necessário inválido DEVEM (MUST) ter percentual indisponível e contagens explícitas. Os recortes de Loja histórica e Totem DEVEM (MUST) valer também para cada hora.

O Reflex DEVE (MUST) mostrar essa série horária de disponibilidade no gráfico de Hoje, com hora e percentual legíveis. MTTD e MTTR permanecem como médias do dia nos cards e não formam a curva horária. Para “Últimos 30 dias” e período personalizado, o contrato e o gráfico DEVEM (MUST) manter a série diária de MTTD e MTTR, sem exigir série horária.

#### Scenario: Consulta durante a tarde
- **WHEN** Hoje é consultado às 14h30 e há observação válida em parte da hora das 14h
- **THEN** a resposta contém as 24 horas, a posição das 14h usa somente 14h00–14h30 e as posições de 15h a 23h não exibem percentual

#### Scenario: Loja e Totem recortados
- **WHEN** a Diretoria seleciona Loja e Totem antes de consultar Hoje
- **THEN** cada posição horária usa somente tempo observável e indisponível daquele Totem comprovado historicamente na Loja durante a hora

#### Scenario: Hora sem observação ou com histórico inválido
- **WHEN** uma hora não tem tempo observável ou um Totem incluído possui histórico necessário inválido nessa hora
- **THEN** o percentual dessa hora é indisponível, com durações e contagem de inválidos informadas sem presumir disponibilidade

#### Scenario: Período personalizado de um dia
- **WHEN** a Diretoria aplica manualmente um período de um único dia
- **THEN** a consulta mantém a série diária de MTTD e MTTR e não recebe a série horária exclusiva do atalho Hoje

### Requirement: Disponibilidade geral segue tempo observado aprovado
O resultado de disponibilidade DEVE (MUST) usar os marcos, o corte histórico e a fórmula ponderada por tempo observado de `indicadores-operacionais`. O contrato DEVE (MUST) informar tempos observável e indisponível, quantidade de Totens incluídos, sem observação e afetados por histórico inválido.

#### Scenario: Dois Totens com observações desiguais
- **WHEN** T1 registra 62 minutos indisponíveis em 1.440 observados e T2 registra 30 em 120
- **THEN** a rede apresenta `100 × (1 − 92/1.560) = 94,10%`, sujeito a duas casas, sem média simples dos percentuais

#### Scenario: Totem sem observação
- **WHEN** um Totem não possui período observável no intervalo
- **THEN** ele não entra no denominador e aparece na contagem de excluídos

#### Scenario: Histórico necessário inválido
- **WHEN** um Totem incluído possui evento necessário inválido
- **THEN** sua disponibilidade e o agregado afetado são indisponíveis, com contagem dos Totens afetados, sem considerar o trecho incerto como Online

#### Scenario: Nenhum tempo observável
- **WHEN** o recorte não contém tempo observável elegível
- **THEN** a disponibilidade é apresentada como indisponível, sem percentual zero ou cem presumido

### Requirement: MTTD e MTTR usam marcos aprovados em totais e série
MTTD e MTTR DEVEM (MUST) ser calculados no Xano conforme `indicadores-operacionais`, em minutos. Cada ponto diário DEVE (MUST) usar seus eventos elegíveis e sua própria média; o total do período DEVE (MUST) usar todos os eventos elegíveis, sem média de médias diárias.

#### Scenario: Detecções conhecidas
- **WHEN** há duas detecções com durações de 18 e 20 minutos no período
- **THEN** o MTTD total é 19 minutos e os eventos entram nos dias de `detectado_em`

#### Scenario: Recuperações conhecidas
- **WHEN** há recuperações com durações de 62 e 40 minutos no período e uma indisponibilidade aberta
- **THEN** o MTTR total é 51 minutos, as recuperações entram nos dias do retorno Online e a aberta consta separadamente

#### Scenario: Dia sem evento elegível
- **WHEN** um dia não contém detecção ou recuperação elegível para uma das médias
- **THEN** o ponto dessa média é indisponível, sem linha interpolada nem valor zero presumido

#### Scenario: Evento inconsistente
- **WHEN** falta marco obrigatório ou uma duração é negativa
- **THEN** o evento não entra na média correspondente e é contado como inconsistente no total e no ponto diário

#### Scenario: Recuperação Online sem timestamp de telemetria
- **WHEN** um evento Online possui `detectado_em` no período, mas a telemetria referenciada não possui `evento_timestamp`
- **THEN** ele não entra na média de MTTR; sua inconsistência é contada no total e no dia civil de `detectado_em`, usando a Loja historicamente comprovada nesse instante para o recorte por Loja, sem usar `detectado_em` como substituto do marco de recuperação

### Requirement: Interface apresenta valores e limitações do resultado
O Reflex DEVE (MUST) exibir disponibilidade, MTTD e MTTR separadamente, com unidades, filtros efetivos e contagens de elegibilidade e inconsistência retornadas pelo Xano. Estados de carregamento, erro e ausência de dados DEVEM (MUST) ser distinguíveis; o frontend NÃO DEVE (MUST NOT) calcular indicadores a partir de eventos brutos.

#### Scenario: Resultado válido
- **WHEN** o Xano retorna indicadores e série válidos
- **THEN** a página mostra percentual de disponibilidade e MTTD/MTTR com unidade explícita e as contagens correspondentes; a conversão de minutos para horas na apresentação não altera os agregados do Xano

#### Scenario: Indicador indisponível
- **WHEN** uma média não tem eventos ou a disponibilidade é invalidada por histórico necessário
- **THEN** a página explica o motivo e preserva as contagens, sem exibir zero como substituto

#### Scenario: Falha na consulta
- **WHEN** a consulta falha após alterar filtros
- **THEN** a página mostra erro e não apresenta valores anteriores como se pertencessem ao novo recorte
