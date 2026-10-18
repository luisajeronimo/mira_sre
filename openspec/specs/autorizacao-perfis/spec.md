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
O sistema DEVE (MUST) negar qualquer consulta técnica global destinada a usuário que não esteja explicitamente autorizado para o perfil e escopo autenticados. Administrador possui acesso global à fila e ao detalhe nesta capacidade, além das permissões administrativas já definidas. `admin`, `bot_fiscalizacao` e valores não oficiais não recebem permissões humanas.

#### Scenario: Operação sem permissão definida
- **WHEN** um usuário autenticado solicita consulta técnica global sem permissão definida para seu perfil
- **THEN** o Xano rejeita a operação sem expor dados

#### Scenario: Perfil não oficial
- **WHEN** uma requisição está associada a `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `bot_fiscalizacao` ou qualquer outro valor não oficial
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

### Requirement: Técnico consulta fila e detalhe globais
O sistema DEVE (MUST) autorizar Técnico a consultar globalmente fila e detalhe e a executar a tratativa definida: editar Responsável, Status, Prioridade e Categoria em chamado não terminal e adicionar comentários Público ou Interno, inclusive em terminal. A autorização DEVE (MUST) ser aplicada no Xano.

#### Scenario: Técnico salva tratativa global
- **WHEN** um Técnico autenticado envia Save válido para chamado global não terminal
- **THEN** o Xano autoriza a operação conforme o contrato de tratativa

#### Scenario: Técnico altera chamado terminal
- **WHEN** um Técnico tenta editar campo funcional de chamado Encerrado ou Cancelado
- **THEN** o Xano rejeita a alteração sem impedir comentário permitido

#### Scenario: Técnico consulta dados da fila
- **WHEN** um Técnico autenticado consulta fila, detalhe ou catálogo necessário à tratativa
- **THEN** o Xano retorna somente os dados globais previstos pelos contratos funcionais

#### Scenario: Técnico solicita operação administrativa
- **WHEN** um Técnico autenticado solicita operação administrativa ou destrutiva fora da tratativa documentada
- **THEN** o Xano rejeita a operação sem executá-la

### Requirement: Diretoria consulta fila e detalhe globais
O sistema DEVE (MUST) autorizar Diretoria a consultar globalmente fila e detalhe e a executar a mesma tratativa operacional do Técnico em chamados não terminais, além de adicionar comentários Público ou Interno inclusive em terminal. Essa autorização NÃO DEVE (MUST NOT) conceder CRUD genérico.

#### Scenario: Diretoria salva tratativa global
- **WHEN** usuário da Diretoria autenticado envia Save válido para chamado não terminal
- **THEN** o Xano autoriza a operação no escopo global

#### Scenario: Diretoria usa CRUD genérico
- **WHEN** usuário da Diretoria tenta alterar chamado por CRUD genérico
- **THEN** o Xano rejeita a requisição sem modificar dados

#### Scenario: Diretoria consulta dados globais
- **WHEN** usuário da Diretoria autenticado solicita consulta global prevista pelo MIRA
- **THEN** o Xano autoriza a consulta sem restringi-la a uma única Loja

#### Scenario: Diretoria tenta alterar dados operacionais
- **WHEN** usuário da Diretoria solicita alteração operacional fora da tratativa documentada
- **THEN** o Xano rejeita a operação sem executá-la

### Requirement: Gerente não acessa a fila técnica global
O sistema NÃO DEVE (MUST NOT) conceder ao Gerente acesso à fila ou ao detalhe técnico global; sua jornada autorizada permanece separada.

#### Scenario: Gerente tenta consultar jornada técnica global
- **WHEN** um Gerente autenticado solicita a fila ou o detalhe técnico global
- **THEN** o Xano responde HTTP 403 sem expor chamados fora dos contratos próprios do Gerente

### Requirement: Administrador possui tratativa operacional global
O sistema DEVE (MUST) autorizar Administrador a consultar globalmente fila e detalhe e a executar a mesma tratativa operacional do Técnico em chamados não terminais, além de adicionar comentários Público ou Interno inclusive em terminal. As permissões administrativas existentes permanecem separadas desse contrato funcional.

#### Scenario: Administrador salva tratativa global
- **WHEN** Administrador autenticado envia Save válido para chamado não terminal
- **THEN** o Xano autoriza a operação no escopo global

#### Scenario: Administrador comenta chamado terminal
- **WHEN** Administrador autenticado envia comentário Interno não vazio para chamado terminal
- **THEN** o Xano cria o comentário sem reabrir nem editar campos funcionais

### Requirement: Preferências globais de fila são autorizadas pelo dono autenticado
O Xano DEVE (MUST) autorizar leitura e escrita de preferências da fila global
somente para Técnico, Diretoria e Administrador autenticados, usando o usuário
da sessão como único dono do registro. Gerente não possui esse contrato;
Diretoria e Administrador só podem usar o escopo `Todos`.

#### Scenario: Identificador de usuário forjado
- **WHEN** cliente tenta indicar outro usuário ao ler ou salvar preferência
- **THEN** o contrato ignora ou rejeita o identificador e usa exclusivamente a
  identidade autenticada, sem expor preferência alheia

#### Scenario: Perfil autorizado usa a própria preferência
- **WHEN** Técnico, Diretoria ou Administrador autenticado usa escopo permitido
- **THEN** o Xano lê ou grava somente o registro pertencente àquela identidade

#### Scenario: Escopo enumerado é proibido ao perfil
- **WHEN** Diretoria ou Administrador solicita `Atribuídos a mim`
- **THEN** o Xano responde HTTP 403 sem expor ou alterar preferência

#### Scenario: Gerente tenta preferência global
- **WHEN** Gerente autenticado chama leitura ou save de preferências globais
- **THEN** o Xano responde HTTP 403 sem expor ou alterar registro
