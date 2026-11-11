# sla-encerramento-chamados Specification

## Purpose
Definir o cálculo do consumo de SLA por estados persistidos e o encerramento de chamados resolvidos sob comando manual, com autorização e limites de vigência.

## Requirements

### Requirement: Consumo de SLA é calculado por estados a partir de fatos persistidos
O Xano DEVE (MUST) calcular o tempo de SLA consumido de um chamado, em tempo corrido, somando, a partir de `criado_em`, a duração dos períodos em `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança` e `Solução Rejeitada`, obtidos da linha do tempo de status formada pela criação em `Novo` e pelas transições registradas em `alteracao_chamado`. Períodos em `Resolvido` NÃO DEVEM (MUST NOT) ser contabilizados, e a contagem DEVE (MUST) terminar na entrada em `Encerrado` ou `Cancelado`. A saída de `Resolvido` para estado que conta SLA, inclusive `Solução Rejeitada`, DEVE (MUST) retomar a contagem a partir do saldo acumulado. O consumo DEVE (MUST) ser comparado ao `sla_horas_aplicado` vigente do chamado. O sistema NÃO DEVE (MUST NOT) persistir o consumo como dado agregado nem reescrever dados históricos.

#### Scenario: Rejeição retoma o saldo
- **WHEN** o chamado consumiu 2 h até `Resolvido`, ficou 3 h em `Resolvido`, passou a `Solução Rejeitada` e consumiu mais 2 h até nova resolução
- **THEN** o consumo é 4 h e o período em `Resolvido` não é contabilizado

#### Scenario: Múltiplas pausas
- **WHEN** o chamado entra e sai de `Resolvido` mais de uma vez
- **THEN** cada período em `Resolvido` é excluído e os demais são somados

#### Scenario: Estado de espera
- **WHEN** o chamado permanece em `Aguardando Solicitante` ou `Aguardando Mudança`
- **THEN** o período é contabilizado

#### Scenario: Estado final
- **WHEN** o chamado está `Encerrado` ou `Cancelado`
- **THEN** o consumo não aumenta após a entrada nesse estado

### Requirement: Consumo de SLA é exposto conforme o perfil
O Xano DEVE (MUST) expor o consumo de SLA somente a partir do cálculo por estados, sem estimar valores, e somente a perfis autorizados (DE-8): Técnico e Administrador na fila e no detalhe; Gerente nos chamados autorizados pela Loja histórica e em indicadores gerenciais; Diretoria em indicadores consolidados. O solicitante NÃO DEVE (MUST NOT) receber o consumo de SLA nesta versão. A apresentação DEVE (MUST) distinguir dentro do SLA, próximo do vencimento, vencido, pausado, encerrado e não calculável.

No detalhe de Gerente, Técnico e Administrador, o consumo DEVE (MUST) ficar em um controle compacto de informação ao lado de "SLA aplicado", aberto por clique ou teclado. A página NÃO DEVE (MUST NOT) repetir esses dados em um card separado. O controle DEVE (MUST) apresentar situação, percentual e prazo quando disponíveis, ou motivo quando não calculável, e informar falhas de consulta sem inventar valores.

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

### Requirement: Linha do tempo inconsistente torna o SLA não calculável
Quando a linha do tempo de status não começar em `Novo`, possuir transição cujo status anterior difere do resultante da transição precedente, contiver status fora da lista canônica vigente, ou não terminar no status atual do chamado, o Xano DEVE (MUST) classificar o SLA do chamado como não calculável, informando o motivo, e NÃO DEVE (MUST NOT) estimar períodos ou timestamps ausentes.

#### Scenario: Chamado com mudança de status anterior ao Save
- **WHEN** o status atual não é reconstruível pelas transições registradas
- **THEN** o SLA é reportado como não calculável, sem valor de consumo

### Requirement: Encerramento sob comando manual é decidido pelo Xano
O sistema DEVE (MUST) oferecer um comando manual de execução única para solicitar ao Xano a verificação de chamados `Resolvido`. Quando esse comando for executado, o Xano DEVE (MUST) encerrar os chamados cuja entrada registrada em `Resolvido` ocorreu há pelo menos 72 horas corridas, sem rejeição posterior, desde que essa entrada seja igual ou posterior ao início de vigência do encerramento, definido explicitamente na publicação e nunca derivado dos dados. O comando NÃO DEVE (MUST NOT) selecionar candidatos nem alterar chamados diretamente; o Xano DEVE (MUST) decidir a elegibilidade e revalidar o status `Resolvido` antes de gravar. O encerramento DEVE (MUST) registrar o comentário público "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução.", definir `Encerrado`, atualizar `ultima_atualizacao_em` e registrar `alteracao_chamado` com `Resolvido` → `Encerrado` e referência ao comentário, sem usuário, apresentado como `Sistema` no histórico e no comentário público. Chamado sem entrada em `Resolvido` registrada NÃO DEVE (MUST NOT) ser encerrado por timestamp inferido. Retorno de telemetria NÃO DEVE (MUST NOT) participar da decisão. Sem execução do comando, nenhum encerramento por prazo é prometido.

#### Scenario: Chamado elegível
- **WHEN** o chamado entrou em `Resolvido` após o início de vigência, há 72 horas ou mais, e a verificação é disparada
- **THEN** o Xano o encerra, registra o comentário público de sistema e a transição com autor `Sistema`

#### Scenario: Rejeição antes da revalidação
- **WHEN** o chamado é rejeitado entre a seleção e a gravação do encerramento
- **THEN** a revalidação falha e o chamado não é encerrado

#### Scenario: Execução repetida
- **WHEN** a verificação é disparada novamente
- **THEN** chamados já `Encerrado` não são alterados nem recebem novo registro

#### Scenario: Prazo não vencido
- **WHEN** o chamado está `Resolvido` há menos de 72 horas corridas
- **THEN** o chamado permanece `Resolvido`

#### Scenario: Chamado resolvido antes da vigência
- **WHEN** o chamado já estava `Resolvido` antes do início de vigência, mesmo há mais de 72 horas
- **THEN** o Xano não o encerra automaticamente, inclusive na primeira execução, e o reporta como fora da vigência

#### Scenario: Nova resolução após a vigência
- **WHEN** um chamado resolvido antes da vigência é rejeitado e volta a `Resolvido` após o início de vigência
- **THEN** o prazo de 72 horas conta a partir da nova entrada em `Resolvido`

#### Scenario: Entrada em Resolvido desconhecida
- **WHEN** o chamado está `Resolvido` sem transição registrada para esse estado
- **THEN** o Xano não o encerra automaticamente e o reporta como não elegível

#### Scenario: Comando não decide
- **WHEN** o comando manual dispara a verificação uma vez
- **THEN** ele não envia identificadores de chamados, não altera chamados diretamente e termina após receber a resposta do Xano

#### Scenario: Prazo vencido sem execução do comando
- **WHEN** um chamado completa 72 horas em `Resolvido` e ninguém executa o comando
- **THEN** ele permanece `Resolvido` até uma execução posterior ou alteração manual autorizada

### Requirement: Estados terminais permanecem bloqueados
`Encerrado` e `Cancelado` DEVEM (MUST) continuar bloqueando reabertura e edição funcional por qualquer fluxo desta capacidade, inclusive o encerramento automático e a rejeição de solução.

#### Scenario: Rejeição após encerramento
- **WHEN** a rejeição é tentada em chamado `Encerrado`
- **THEN** o Xano a recusa como conflito sem alterar o chamado
