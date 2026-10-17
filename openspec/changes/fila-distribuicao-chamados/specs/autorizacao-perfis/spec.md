# Delta: autorizacao-perfis

## MODIFIED Requirements

### Requirement: Negação por padrão
O sistema DEVE (MUST) negar qualquer consulta técnica global destinada a usuário que não esteja explicitamente autorizado para o perfil e escopo autenticados. Administrador possui acesso global à fila e ao detalhe nesta capacidade, além das permissões administrativas já definidas. `admin`, `bot_fiscalizacao` e valores não oficiais não recebem permissões humanas.

#### Scenario: Operação sem permissão definida
- **WHEN** um usuário autenticado solicita consulta técnica global sem permissão definida para seu perfil
- **THEN** o Xano rejeita a operação sem expor dados

#### Scenario: Perfil não oficial
- **WHEN** uma requisição está associada a `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `bot_fiscalizacao` ou qualquer outro valor não oficial
- **THEN** o Xano não atribui permissões de um perfil oficial à requisição

## ADDED Requirements

### Requirement: Técnico consulta fila e detalhe globais
O sistema DEVE (MUST) autorizar o Técnico a consultar globalmente a fila e os detalhes dos chamados conforme a spec da fila. A autorização é aplicada no Xano.

#### Scenario: Técnico consulta dados da fila
- **WHEN** um Técnico autenticado consulta a fila ou o detalhe técnico global
- **THEN** o Xano retorna os dados globais previstos na spec da fila

### Requirement: Diretoria consulta fila e detalhe globais
O sistema DEVE (MUST) autorizar a Diretoria a consultar globalmente a fila e os detalhes de chamados previstos nesta capacidade, sem restringi-la a uma única unidade.

#### Scenario: Diretoria consulta dados globais
- **WHEN** um usuário da Diretoria autenticado solicita consulta global prevista pelo MIRA
- **THEN** o Xano autoriza a consulta sem restringi-la a uma única Loja

### Requirement: Gerente não acessa a fila técnica global
O sistema NÃO DEVE (MUST NOT) conceder ao Gerente acesso à fila ou ao detalhe técnico global; sua jornada autorizada permanece separada.

#### Scenario: Gerente tenta consultar jornada técnica global
- **WHEN** um Gerente autenticado solicita a fila ou o detalhe técnico global
- **THEN** o Xano responde HTTP 403 sem expor chamados fora dos contratos próprios do Gerente

## REMOVED Requirements

### Requirement: Técnico recebe acesso operacional compatível com a tratativa
**Reason**: A autorização de mutações operacionais não pertence mais a esta change de fila.
**Migration**: A matriz de tratativa é definida por `tratativa-operacional-chamados`.

### Requirement: Diretoria possui acesso global de consulta
**Reason**: A regra anterior limitava Diretoria fora da gestão imediata de responsável, modelo superado.
**Migration**: A consulta global permanece nesta change; a matriz operacional é definida pela change posterior.
