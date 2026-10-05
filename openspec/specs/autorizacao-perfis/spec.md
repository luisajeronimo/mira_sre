# autorização por perfis Specification

## Purpose

Definir a autorização aplicada pelo Xano aos perfis oficiais do MIRA, incluindo o isolamento dos dados da unidade associada ao Gerente.

## Requirements

### Requirement: Autorização é aplicada no Xano
O sistema DEVE (MUST) autorizar cada requisição destinada a usuários no Xano, utilizando a identidade autenticada e o perfil oficial, independentemente do que o Reflex exibir ou ocultar.

#### Scenario: Interface oculta uma ação proibida
- **WHEN** um usuário tenta chamar diretamente uma operação que seu perfil não autoriza
- **THEN** o Xano rejeita a operação mesmo que a chamada não tenha sido originada pela interface do Reflex

#### Scenario: Operação autorizada
- **WHEN** um usuário autenticado solicita uma operação explicitamente permitida ao seu perfil e ao seu escopo
- **THEN** o Xano permite que a operação prossiga

### Requirement: Negação por padrão
O sistema DEVE (MUST) negar qualquer operação destinada a usuários que não esteja explicitamente autorizada para o perfil e o escopo do usuário autenticado. `administrador` somente recebe nesta capacidade a criação administrativa de usuários; `admin`, `bot_fiscalizacao` e valores não oficiais não recebem permissões humanas.

#### Scenario: Operação sem permissão definida
- **WHEN** um usuário autenticado solicita uma operação sem permissão definida para seu perfil
- **THEN** o Xano rejeita a operação sem executar alterações

#### Scenario: Perfil não oficial
- **WHEN** uma requisição está associada a `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `bot_fiscalizacao` ou qualquer outro valor que não represente Gerente, Técnico, Diretoria ou Administrador
- **THEN** o Xano não atribui permissões de um perfil oficial à requisição

### Requirement: Gerente acessa somente sua unidade
O sistema DEVE (MUST) restringir o Gerente à unidade à qual ele estiver associado e aos dados relacionados a essa unidade, incluindo seus ativos e chamados que o Gerente esteja autorizado a acompanhar.

#### Scenario: Gerente consulta a própria unidade
- **WHEN** um Gerente autenticado consulta dados pertencentes à sua unidade associada
- **THEN** o Xano retorna somente os dados permitidos dessa unidade

#### Scenario: Gerente informa outra unidade diretamente
- **WHEN** um Gerente autenticado tenta consultar ou alterar dados de uma unidade diferente da sua associação
- **THEN** o Xano rejeita a operação sem retornar dados da outra unidade

#### Scenario: Gerente sem unidade associada
- **WHEN** um Gerente autenticado solicita uma operação dependente de unidade e não possui uma associação válida com uma Loja
- **THEN** o Xano rejeita a operação sem ampliar seu escopo de acesso

### Requirement: Técnico recebe acesso operacional compatível com a tratativa
O sistema DEVE (MUST) autorizar o Técnico a consultar os chamados da fila e as informações de ativos e telemetria necessárias à tratativa, sem criar níveis distintos de Técnico.

#### Scenario: Técnico consulta dados necessários à tratativa
- **WHEN** um Técnico autenticado consulta a fila ou as informações de ativo e telemetria necessárias ao atendimento
- **THEN** o Xano autoriza a consulta conforme os contratos funcionais disponíveis

#### Scenario: Técnico solicita operação administrativa
- **WHEN** um Técnico autenticado solicita uma operação administrativa ou destrutiva que não pertence à tratativa documentada
- **THEN** o Xano rejeita a operação sem executá-la

### Requirement: Diretoria possui acesso global de consulta
O sistema DEVE (MUST) autorizar a Diretoria a consultar dados globais necessários aos dashboards e indicadores, sem conceder por esse motivo permissões de alteração operacional.

#### Scenario: Diretoria consulta dados globais
- **WHEN** um usuário da Diretoria autenticado solicita uma consulta global prevista pelo MIRA
- **THEN** o Xano autoriza a consulta sem restringi-la a uma única unidade

#### Scenario: Diretoria tenta alterar dados operacionais
- **WHEN** um usuário da Diretoria autenticado solicita uma alteração operacional que não faz parte de suas responsabilidades documentadas
- **THEN** o Xano rejeita a operação sem executá-la

### Requirement: CRUDs genéricos não ampliam permissões
O sistema NÃO DEVE (MUST NOT) permitir que endpoints CRUD genéricos contornem as regras de autorização ou concedam operações administrativas e destrutivas não previstas para os perfis oficiais. A criação de usuário administrativo DEVE permanecer no contrato funcional específico autorizado apenas a Administrador.

#### Scenario: Acesso direto a mutação genérica
- **WHEN** um usuário autenticado chama diretamente um endpoint genérico de criação, alteração ou exclusão sem permissão funcional correspondente
- **THEN** o Xano rejeita a operação sem modificar os dados

#### Scenario: Consulta genérica fora do escopo
- **WHEN** uma consulta genérica poderia retornar dados além do escopo autorizado ao usuário
- **THEN** o Xano aplica o filtro de escopo no backend ou rejeita a consulta sem expor esses dados

### Requirement: Automações permanecem fora desta autorização de usuários
O sistema NÃO DEVE (MUST NOT) alterar, nesta capacidade, o acesso utilizado pelo Simulator para envio de telemetria nem pelo Fiscal para disparo da verificação de heartbeat.

#### Scenario: Aplicação da change
- **WHEN** esta change for implementada
- **THEN** os contratos de acesso usados pelo Simulator e pelo Fiscal permanecem com o comportamento anterior à change

### Requirement: Autorização central considera troca obrigatória pendente
O sistema DEVE (MUST) aplicar centralmente o estado de troca obrigatória antes da autorização de operações funcionais normais. A sessão pendente somente DEVE passar para a consulta da própria identidade e para a operação autenticada de troca de senha.

#### Scenario: Autorização de operação normal com pendência
- **WHEN** uma sessão pendente alcança a autorização de uma operação funcional normal
- **THEN** o sistema a rejeita antes de executar a regra funcional da operação

#### Scenario: Operação permitida durante pendência
- **WHEN** uma sessão pendente consulta a própria identidade ou envia sua nova senha ao contrato de primeiro acesso
- **THEN** o sistema permite a operação autenticada correspondente
