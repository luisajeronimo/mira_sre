# Delta: autorizacao-perfis

## MODIFIED Requirements

### Requirement: Negação por padrão
O sistema DEVE (MUST) negar qualquer operação destinada a usuários que não esteja explicitamente autorizada para o perfil e escopo autenticados. Administrador possui acesso global à fila e à gestão de atribuição de chamados nesta capacidade, além das permissões administrativas já definidas. `admin`, `bot_fiscalizacao` e valores não oficiais não recebem permissões humanas.

#### Scenario: Operação sem permissão definida
- **WHEN** um usuário autenticado solicita uma operação sem permissão definida para seu perfil
- **THEN** o Xano rejeita a operação sem executar alterações

#### Scenario: Administrador usa fila global
- **WHEN** um Administrador autenticado consulta a fila ou gere a atribuição por contrato funcional
- **THEN** o Xano autoriza somente as operações previstas para esta capacidade

#### Scenario: Perfil não oficial
- **WHEN** uma requisição está associada a `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `bot_fiscalizacao` ou qualquer outro valor não oficial
- **THEN** o Xano não atribui permissões de um perfil oficial à requisição

### Requirement: Técnico recebe acesso operacional compatível com a tratativa
O sistema DEVE (MUST) autorizar o Técnico a consultar globalmente a fila e os detalhes dos chamados, assumir chamados sem responsável, atribuir ou reatribuir Técnico responsável em chamados não terminais e liberar somente a própria atribuição. A autorização e a validação de que o responsável escolhido é Técnico são aplicadas no Xano.

#### Scenario: Técnico consulta dados necessários à tratativa
- **WHEN** um Técnico autenticado consulta a fila, o detalhe ou as informações necessárias à tratativa
- **THEN** o Xano retorna os dados globais previstos na spec da fila

#### Scenario: Técnico solicita operação administrativa
- **WHEN** um Técnico autenticado solicita uma operação administrativa ou destrutiva que não pertence à tratativa documentada
- **THEN** o Xano rejeita a operação sem executá-la

#### Scenario: Técnico gere atribuição permitida
- **WHEN** um Técnico autenticado assume, atribui, reatribui ou libera atribuição própria conforme a spec da fila
- **THEN** o Xano autoriza a operação sem alterar status automaticamente

### Requirement: Diretoria possui acesso global de consulta
O sistema DEVE (MUST) autorizar a Diretoria a consultar globalmente a fila e os detalhes de chamados e gerir atribuições conforme a spec da fila. Essa permissão não concede alteração de status nem outras mutações operacionais fora da gestão de responsável prevista.

#### Scenario: Diretoria consulta dados globais
- **WHEN** um usuário da Diretoria autenticado solicita consulta global prevista pelo MIRA
- **THEN** o Xano autoriza a consulta sem restringi-la a uma única unidade

#### Scenario: Diretoria gere atribuição
- **WHEN** um usuário da Diretoria autenticado atribui, reatribui ou libera o Técnico responsável de chamado não terminal
- **THEN** o Xano autoriza a operação nos limites da spec da fila

#### Scenario: Diretoria tenta alterar dados operacionais
- **WHEN** um usuário da Diretoria solicita alteração operacional fora da gestão de responsável prevista
- **THEN** o Xano rejeita a operação sem executá-la
