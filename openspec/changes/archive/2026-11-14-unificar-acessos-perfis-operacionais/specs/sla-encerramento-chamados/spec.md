## MODIFIED Requirements

### Requirement: Consumo de SLA é exposto conforme o perfil
O Xano DEVE (MUST) expor o consumo de SLA somente a partir do cálculo por estados, sem estimar valores, e somente a perfis autorizados : Técnico, Diretoria e Administrador na fila, no detalhe e em indicadores consolidados; Gerente nos chamados autorizados pela Loja histórica e em indicadores gerenciais. O solicitante NÃO DEVE (MUST NOT) receber o consumo de SLA nesta versão. A apresentação DEVE (MUST) distinguir dentro do SLA, próximo do vencimento, vencido, pausado, encerrado e não calculável.

No detalhe de Gerente, Técnico, Diretoria e Administrador, o consumo DEVE (MUST) ficar em um controle compacto de informação ao lado de "SLA aplicado", aberto por clique ou teclado. A página NÃO DEVE (MUST NOT) repetir esses dados em um card separado. O controle DEVE (MUST) apresentar situação, percentual e prazo quando disponíveis, ou motivo quando não calculável, e informar falhas de consulta sem inventar valores.

#### Scenario: Técnico consulta chamado em contagem
- **WHEN** Técnico autenticado consulta chamado com consumo calculável em contagem
- **THEN** recebe percentual consumido, tempo restante e situação derivados do cálculo

#### Scenario: Gerente consulta chamado de outra Loja histórica
- **WHEN** Gerente solicita o consumo de chamado cuja Loja histórica não é a sua
- **THEN** o Xano rejeita a consulta sem expor o consumo

#### Scenario: Solicitante acompanha o próprio chamado
- **WHEN** o solicitante consulta o próprio chamado
- **THEN** a resposta contém o status e não contém campos de SLA

#### Scenario: Consumo não calculável
- **WHEN** o cálculo retorna não calculável
- **THEN** a apresentação informa a indisponibilidade com o motivo, sem percentual nem prazo

#### Scenario: Consumo no detalhe sob demanda
- **WHEN** usuário autorizado abre a informação ao lado de "SLA aplicado"
- **THEN** o Reflex apresenta o consumo já retornado pelo Xano, sem card separado, e permite fechar a informação sem alterar o chamado

#### Scenario: Diretoria consulta SLA no detalhe
- **WHEN** Diretoria autenticada abre um chamado global
- **THEN** recebe o mesmo consumo e controle compacto disponíveis a Técnico e Administrador, inclusive estados de falha e não calculável
