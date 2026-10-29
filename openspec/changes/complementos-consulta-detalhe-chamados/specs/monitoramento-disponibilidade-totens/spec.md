# Spec Delta

## MODIFIED Requirements

### Requirement: Página de monitoramento apresenta evolução operacional por Totem
A rota `/monitoramento` DEVE (MUST) apresentar, em desktop, listagem e painel de detalhe na mesma página. A listagem DEVE (MUST) mostrar identificação, Loja, estado persistido e os dois timestamps do resumo; a seleção DEVE (MUST) mostrar a última telemetria, seus valores recebidos, os três históricos e link ao detalhe de cada incidente. Eventos de disponibilidade e incidentes DEVEM (MUST) permanecer em seções independentes. Um identificador de Totem válido na URL DEVE (MUST) restaurar a seleção após recarga, sem criar rota nova.

#### Scenario: Seleção de Totem na mesma rota
- **WHEN** a pessoa seleciona um Totem da listagem carregada
- **THEN** a página consulta e apresenta o detalhe desse Totem sem criar nova rota

#### Scenario: Seleção restaurada pela URL
- **WHEN** perfil autorizado abre ou recarrega `/monitoramento` com identificador de Totem válido
- **THEN** a página mantém a URL, carrega a listagem e abre automaticamente o detalhe daquele Totem

#### Scenario: Identificador inválido ou inacessível
- **WHEN** a URL informa identificador de Totem inválido ou não autorizado
- **THEN** a página mantém a listagem autorizada e informa o erro de detalhe sem fabricar seleção

#### Scenario: Rota base sem seleção
- **WHEN** perfil autorizado abre `/monitoramento` sem identificador de Totem
- **THEN** a página mantém a listagem autorizada e seu estado inicial sem
  consultar nem informar erro de detalhe

#### Scenario: Valores de telemetria usam apenas sufixos de apresentação aprovados
- **WHEN** a última telemetria está disponível
- **THEN** a página apresenta CPU e memória com `%`, temperatura com `°C`, o estado de rede recebido e cada limite de heartbeat como `X minutos`, sem conversão, arredondamento, cálculo, regra de precisão, classificação de saúde ou recomendação

#### Scenario: Estados vazios do detalhe
- **WHEN** a coleção de telemetrias, transições ou incidentes está vazia
- **THEN** a seção correspondente informa somente que não há registros e não exibe valores ou eventos inventados

#### Scenario: Erro real de consulta
- **WHEN** uma consulta de listagem ou detalhe falha
- **THEN** a página informa o erro sem substituir o resultado por dados simulados
