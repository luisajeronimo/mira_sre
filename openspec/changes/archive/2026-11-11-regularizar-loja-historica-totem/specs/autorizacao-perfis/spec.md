# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente acessa somente sua unidade
O sistema DEVE (MUST) restringir o Gerente à unidade à qual ele estiver associado e aos dados relacionados a essa unidade, incluindo seus ativos e chamados que o Gerente esteja autorizado a acompanhar. Para chamados, a unidade DEVE (MUST) ser a Loja resolvida pelo vínculo histórico do Totem no `criado_em` do chamado, conforme `vinculo-historico-totem-loja`; chamado sem Loja resolvida NÃO DEVE (MUST NOT) ser tratado como pertencente à unidade de nenhum Gerente.

#### Scenario: Gerente consulta a própria unidade
- **WHEN** um Gerente autenticado consulta dados pertencentes à sua unidade associada
- **THEN** o Xano retorna somente os dados permitidos dessa unidade

#### Scenario: Gerente informa outra unidade diretamente
- **WHEN** um Gerente autenticado tenta consultar ou alterar dados de uma unidade diferente da sua associação
- **THEN** o Xano rejeita a operação sem retornar dados da outra unidade

#### Scenario: Gerente sem unidade associada
- **WHEN** um Gerente autenticado solicita uma operação dependente de unidade e não possui uma associação válida com uma Loja
- **THEN** o Xano rejeita a operação sem ampliar seu escopo de acesso

#### Scenario: Chamado de Totem transferido depois da abertura
- **WHEN** o Totem de um chamado foi transferido para a Loja do Gerente depois do `criado_em` do chamado
- **THEN** o chamado pertence à Loja vigente na abertura e o Xano rejeita o acesso do Gerente da nova Loja

#### Scenario: Chamado sem Loja histórica
- **WHEN** um Gerente consulta chamado cuja Loja resolvida é nula
- **THEN** o Xano rejeita o acesso como não autorizado, sem usar a Loja atual do Totem
