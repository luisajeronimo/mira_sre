# Delta: autorizacao-perfis

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Administrador possui tratativa operacional global
O sistema DEVE (MUST) autorizar Administrador a consultar globalmente fila e detalhe e a executar a mesma tratativa operacional do Técnico em chamados não terminais, além de adicionar comentários Público ou Interno inclusive em terminal. As permissões administrativas existentes permanecem separadas desse contrato funcional.

#### Scenario: Administrador salva tratativa global
- **WHEN** Administrador autenticado envia Save válido para chamado não terminal
- **THEN** o Xano autoriza a operação no escopo global

#### Scenario: Administrador comenta chamado terminal
- **WHEN** Administrador autenticado envia comentário Interno não vazio para chamado terminal
- **THEN** o Xano cria o comentário sem reabrir nem editar campos funcionais
