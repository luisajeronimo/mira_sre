# Delta: autorizacao-perfis

## MODIFIED Requirements

### Requirement: Gerente usa Loja histórica comprovada do chamado
O Xano DEVE (MUST) autorizar o Gerente em lista, detalhe e comentários pela Loja comprovada na abertura de cada chamado, inclusive nos contratos genéricos de consulta de `chamados`. A Loja atual do Totem NÃO DEVE (MUST NOT) conceder acesso a chamado antigo de outra Loja. Sem Loja histórica demonstrável, o acesso do Gerente DEVE (MUST) falhar fechado.

#### Scenario: Totem transferido
- **WHEN** Gerente da Loja de destino solicita chamado anterior à transferência
- **THEN** o Xano rejeita sem expor o chamado ou suas interações

#### Scenario: Origem indeterminada
- **WHEN** a Loja histórica de um chamado legado não pode ser demonstrada
- **THEN** nenhum Gerente recebe acesso por inferência da Loja atual do Totem

#### Scenario: Lista genérica restrita à Loja histórica
- **WHEN** um Gerente autenticado solicita `GET /chamados`
- **THEN** o Xano devolve somente chamados cuja Loja comprovada na abertura é a Loja do Gerente, sem usar a Loja atual do Totem

#### Scenario: Detalhe genérico de chamado de outra Loja histórica
- **WHEN** um Gerente autenticado solicita `GET /chamados/{chamados_id}` de chamado cuja Loja comprovada na abertura é outra ou não pode ser demonstrada
- **THEN** o Xano rejeita a operação antes de ler e retornar o registro do chamado

#### Scenario: Consulta genérica global preservada
- **WHEN** Técnico ou Diretoria autenticados solicitam `GET /chamados` ou `GET /chamados/{chamados_id}`
- **THEN** o Xano mantém a consulta global, e Administrador e perfis não oficiais continuam negados nesses contratos
