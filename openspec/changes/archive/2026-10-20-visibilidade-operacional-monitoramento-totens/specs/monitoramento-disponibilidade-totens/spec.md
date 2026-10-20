# Spec Delta

## ADDED Requirements

### Requirement: Listagem de monitoramento expõe resumo operacional persistido

`GET /monitoramento/ativos` DEVE (MUST) retornar, para cada Totem, identificação, Loja, estado `online` ou `offline` persistido no Xano, `evento_timestamp` da última telemetria e `detectado_em` da última transição, admitindo `null` para os dois últimos quando o fato não existir. Os totais de `/monitoramento` DEVEM (MUST) continuar derivados somente desse estado persistido.

#### Scenario: Listagem com resumo de Totens

- **WHEN** um perfil já autorizado ao monitoramento consulta a listagem
- **THEN** cada Totem retornado contém sua Loja, estado persistido, data/hora da última telemetria e data/hora da última transição disponíveis

#### Scenario: Totem sem fatos históricos

- **WHEN** um Totem ainda não possui telemetria ou transição registrada
- **THEN** a listagem o mantém com seu estado persistido e informa a ausência dos respectivos timestamps sem fabricar dados

### Requirement: Detalhe operacional consulta fatos recentes do Totem

O sistema DEVE (MUST) fornecer `GET /monitoramento/ativos/{ativos_referencia_id}` como único contrato adicional de leitura. Para o Totem solicitado, DEVE (MUST) retornar identificação, Loja, estado persistido, última telemetria e até 10 telemetrias, 10 transições e 10 incidentes automáticos de heartbeat, em ordem decrescente de `evento_timestamp`, `detectado_em` e `criado_em`, respectivamente.

#### Scenario: Detalhe com telemetria, transições e incidentes

- **WHEN** um Totem possui registros nos três históricos
- **THEN** o detalhe retorna os valores reais de CPU, memória, temperatura, rede e timestamps da última telemetria, além de cada coleção limitada e ordenada pelo timestamp correspondente

#### Scenario: Detalhe sem telemetria, transição ou incidente

- **WHEN** o Totem não possui uma ou mais das coleções consultadas
- **THEN** o detalhe retorna `null` para a última telemetria ausente e coleções vazias para os históricos ausentes, sem criar eventos substitutos

#### Scenario: Incidente exibível é o incidente automático de heartbeat

- **WHEN** existem chamados de naturezas diferentes relacionados ao Totem
- **THEN** o detalhe retorna somente aqueles com origem automática, criador `bot_fiscalizacao` e categoria de heartbeat, sem associá-los causalmente a uma transição individual

#### Scenario: Totem inexistente

- **WHEN** o identificador do Totem não existe
- **THEN** o contrato retorna o erro de não encontrado sem retornar detalhe parcial

### Requirement: Página de monitoramento apresenta evolução operacional por Totem

A rota `/monitoramento` DEVE (MUST) apresentar, em desktop, listagem e painel de detalhe na mesma página. A listagem DEVE (MUST) mostrar identificação, Loja, estado persistido e os dois timestamps do resumo; a seleção DEVE (MUST) mostrar a última telemetria, seus valores recebidos, os três históricos e link ao detalhe de cada incidente. Eventos de disponibilidade e incidentes DEVEM (MUST) permanecer em seções independentes.

#### Scenario: Seleção de Totem na mesma rota

- **WHEN** a pessoa seleciona um Totem da listagem carregada
- **THEN** a página consulta e apresenta o detalhe desse Totem sem criar nova rota

#### Scenario: Valores de telemetria usam apenas sufixos de apresentação aprovados

- **WHEN** a última telemetria está disponível
- **THEN** a página apresenta CPU e memória com `%`, temperatura com `°C`, o estado de rede recebido e cada limite de heartbeat como `X minutos`, sem conversão, arredondamento, cálculo, regra de precisão, classificação de saúde ou recomendação

#### Scenario: Estados vazios do detalhe

- **WHEN** a coleção de telemetrias, transições ou incidentes está vazia
- **THEN** a seção correspondente informa somente que não há registros e não exibe valores ou eventos inventados

#### Scenario: Erro real de consulta

- **WHEN** uma consulta de listagem ou detalhe falha
- **THEN** a página informa o erro sem substituir o resultado por dados simulados

### Requirement: Visão operacional não monitora a execução do Fiscal nem cria dashboard executivo

A interface DEVE (MUST) mostrar somente fatos persistidos no Xano e NÃO DEVE (MUST NOT) calcular disponibilidade pelo relógio do frontend. Ela NÃO DEVE (MUST NOT) exibir execução, frequência, saúde, logs, alertas, agendamento ou heartbeat do Fiscal, nem percentual, duração, MTTD, MTTR, SLA, médias, tendência, recorrência, consolidação por Loja/rede ou gráfico executivo.

#### Scenario: Fiscal permaneceu desligado

- **WHEN** não há novos fatos persistidos porque o Fiscal não foi executado por um período
- **THEN** a página mantém a apresentação do último estado e dos registros existentes sem indicar falha ou inatividade do Fiscal

## MODIFIED Requirements

### Requirement: Dados temporais permitem consumo futuro sem dashboard

Eventos de disponibilidade, telemetria de referência e `chamados.criado_em` DEVEM (MUST) permitir futuramente relacionar detecção, recuperação, duração, número e recorrência por Totem ou Loja, percentual histórico de disponibilidade, último heartbeat e criação de incidente. A capacidade NÃO DEVE (MUST NOT) persistir duração, percentual, MTTD, MTTR, médias ou agregados, nem implementar dashboard executivo nesta change.

#### Scenario: Dados de uma indisponibilidade completa

- **WHEN** Totem passa de Online para Offline e depois retorna Online
- **THEN** existem fatos persistidos que permitem relacionar última telemetria, detecção, recuperação e chamado criado quando aplicável
