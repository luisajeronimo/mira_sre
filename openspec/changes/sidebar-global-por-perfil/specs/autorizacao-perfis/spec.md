# Delta: autorização-perfis

## ADDED Requirements

### Requirement: Consulta de monitoramento possui contrato global autorizado
O Xano DEVE (MUST) fornecer contrato dedicado de consulta de monitoramento de
Totens somente para Técnico, Diretoria e Administrador autenticados. O contrato
DEVE (MUST) aplicar a identidade da sessão no backend e NÃO DEVE (MUST NOT)
alterar o contrato existente de ativos genéricos.

#### Scenario: Perfil global consulta monitoramento
- **WHEN** Técnico, Diretoria ou Administrador autenticado solicita o contrato
  dedicado de monitoramento
- **THEN** o Xano retorna somente a coleção global prevista pelo contrato

#### Scenario: Gerente chama o contrato diretamente
- **WHEN** Gerente autenticado chama diretamente o contrato de monitoramento
- **THEN** o Xano responde HTTP 403 sem retornar dados globais

#### Scenario: Sessão ausente ou inválida
- **WHEN** a consulta de monitoramento não possui sessão válida
- **THEN** o Xano responde HTTP 401 sem retornar dados

#### Scenario: Contrato genérico de ativos preservado
- **WHEN** consumidor autorizado usa o contrato genérico de ativos existente
- **THEN** seu comportamento e escopo permanecem inalterados por esta capacidade
