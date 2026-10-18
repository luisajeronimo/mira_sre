# Delta: autorização-perfis

## ADDED Requirements

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
