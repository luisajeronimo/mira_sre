## Purpose

Permitir a retomada contínua de telemetria simulada por controle persistido no Xano, preservando a fiscalização e a disponibilidade baseadas em fatos.

## ADDED Requirements

### Requirement: Controle de envio é independente da disponibilidade
O Xano DEVE (MUST) distinguir Totem não gerenciado pela simulação, gerenciado com envio silenciado e gerenciado com envio ativo. Alterar esse controle NÃO DEVE (MUST NOT) alterar disponibilidade, criar telemetria, registrar transição ou modificar chamado. O controle DEVE (MUST) persistir entre ciclos e reinícios.

#### Scenario: Envio é autorizado para Totem Offline
- **WHEN** uma retomada válida altera o controle de silenciado para ativo
- **THEN** o Totem continua com o estado persistido anterior até uma verificação normal do Xano registrar sua recuperação
- **AND** nenhum chamado é resolvido, cancelado ou encerrado pela autorização do envio

#### Scenario: Processo é reiniciado
- **WHEN** o Simulator reinicia depois de uma retomada confirmada
- **THEN** consulta novamente o controle persistido e mantém o envio autorizado sem reaplicar o silêncio inicial da configuração

### Requirement: Inicialização de controles é explícita e preserva fatos
A preparação dos controles DEVE (MUST) apresentar os IDs participantes e os valores propostos antes de escrever. DEVE (MUST) inicializar somente controles ausentes dos IDs revisados, preservando controles existentes e todos os fatos operacionais. A configuração inicial de silêncio NÃO DEVE (MUST NOT) sobrescrever uma retomada posterior.

#### Scenario: Totens participantes ainda não têm controle
- **WHEN** o plano de preparação aprovado contém os participantes e o Totem inicialmente silenciado
- **THEN** são inicializados somente os controles ausentes: silenciado para esse Totem e ativo para os demais participantes
- **AND** não são alterados estado de disponibilidade, telemetrias, chamados ou vínculos históricos

#### Scenario: Preparação repetida após retomada
- **WHEN** a preparação encontra um controle já inicializado
- **THEN** preserva o valor persistido e informa o resultado sem revertê-lo ao valor original do ambiente

### Requirement: Retomada exige identidade operacional autorizada
O Xano DEVE (MUST) autorizar a retomada somente para Técnico, Diretoria e Administrador com sessão válida e primeiro acesso concluído, antes de consultar o alvo. Gerente, perfil não oficial, sessão pendente e chaves técnicas NÃO DEVEM (MUST NOT) autorizar essa operação humana.

#### Scenario: Perfis operacionais confirmam a retomada
- **WHEN** Técnico, Diretoria ou Administrador com sessão concluída solicita uma retomada elegível
- **THEN** o Xano aplica a mesma operação para qualquer um dos três perfis

#### Scenario: Identidade não permite retomada
- **WHEN** Gerente, perfil não oficial ou usuário com troca obrigatória pendente solicita a retomada
- **THEN** o Xano nega a operação sem ler dados operacionais do alvo nem alterar controles

#### Scenario: Sessão inválida ou chave técnica isolada
- **WHEN** a requisição não possui uma sessão humana válida, ainda que apresente uma chave de automação
- **THEN** o Xano responde como não autenticado e não altera nenhum Totem

### Requirement: Retomada valida o alvo e é repetível
A retomada DEVE (MUST) atuar somente no Totem solicitado, gerenciado, silenciado e Offline. Alvo inexistente DEVE (MUST) resultar em não encontrado; alvo não gerenciado ou silenciado fora de Offline, em estado incompatível. Para um controle já ativo, a repetição DEVE (MUST) confirmar a autorização existente sem nova alteração, mesmo após a recuperação.

#### Scenario: Totem gerenciado e silenciado está Offline
- **WHEN** uma identidade autorizada confirma sua retomada
- **THEN** somente seu controle passa para ativo e a resposta confirma autorização de envio contínuo

#### Scenario: Requisição repetida
- **WHEN** o controle do Totem solicitado já está ativo
- **THEN** a resposta informa que o envio já está autorizado, sem novos fatos ou alterações de chamado e sem exigir que ele ainda esteja Offline

#### Scenario: Alvo inexistente ou não gerenciado
- **WHEN** o alvo não existe ou não possui controle de simulação
- **THEN** a resposta distingue não encontrado de estado incompatível e não inicializa automaticamente um controle

#### Scenario: Totem deixou de estar Offline antes da confirmação
- **WHEN** o alvo continua silenciado, mas seu estado persistido já não é Offline
- **THEN** a retomada é rejeitada como estado incompatível e a interface pode recarregar o estado confirmado

### Requirement: Simulator consulta o controle de forma agrupada
Em cada ciclo, o Simulator DEVE (MUST) consultar uma vez os controles de seus IDs participantes antes de enviar amostras. Somente participantes presentes com controle ativo DEVEM (MUST) enviar telemetria. Controle silenciado, ausente ou não gerenciado NÃO DEVE (MUST NOT) ser convertido em autorização local.

#### Scenario: Ciclo com controles distintos
- **WHEN** a consulta válida contém participantes ativos, silenciados e não gerenciados
- **THEN** somente os ativos geram POSTs e os demais permanecem sem envio nesse ciclo

#### Scenario: Retomada ocorreu após a consulta do ciclo
- **WHEN** o controle muda para ativo depois da consulta agrupada já realizada
- **THEN** a autorização é observada na consulta do próximo ciclo, sem promessa de envio imediato

### Requirement: Falha na leitura do controle não autoriza envio
Se a consulta de controle falhar ou sua resposta não puder ser validada, o Simulator NÃO DEVE (MUST NOT) enviar amostras nesse ciclo, reutilizar controles antigos ou usar configuração local como autorização alternativa. DEVE (MUST) registrar diagnóstico sem segredo e repetir a consulta no próximo ciclo normal.

#### Scenario: Consulta indisponível
- **WHEN** a leitura sofre timeout, erro HTTP ou formato incompatível
- **THEN** não há POST de telemetria nesse ciclo e a próxima tentativa respeita o agendamento existente

#### Scenario: Leitura volta a funcionar
- **WHEN** o ciclo seguinte obtém controles válidos
- **THEN** o Simulator volta a enviar continuamente para os participantes ativos, sem reinício manual obrigatório

### Requirement: Recuperação continua pertencendo ao Xano e ao Fiscal
O Simulator DEVE (MUST) gerar amostras atuais e continuar os envios nos ciclos seguintes enquanto o controle permitir. NÃO DEVE (MUST NOT) classificar disponibilidade ou chamar fiscalização adicional. O Fiscal normal DEVE (MUST) continuar como disparador da avaliação que registra Online e sua transição, sem tratar chamados.

#### Scenario: Primeira amostra após a retomada
- **WHEN** o Simulator envia telemetria recente para um Totem Offline
- **THEN** a amostra é persistida e a recuperação depende da verificação normal do Fiscal, que preserva o chamado

#### Scenario: Envio ou fiscalização falhou
- **WHEN** uma requisição ou serviço necessário está indisponível
- **THEN** a autorização de envio não é apresentada como comprovação de que o Totem já está Online
