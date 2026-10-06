# Spec Delta

## MODIFIED Requirements

### Requirement: Simulator exige credencial técnica de finalidade antes de telemetria

O sistema DEVE (MUST) exigir o header `X-MIRA-Simulator-Key` em `POST /telemetria_equipamentos` e validar sua credencial técnica de finalidade antes da validação funcional de presença do payload, de qualquer persistência ou de lógica operacional. O Simulator NÃO DEVE (MUST NOT) enviar requisição anônima quando sua credencial não estiver disponível.

#### Scenario: Chave Simulator ausente ou inválida
- **WHEN** `POST /telemetria_equipamentos` não contém `X-MIRA-Simulator-Key` ou contém valor inválido e o payload não contém um ou mais campos funcionais obrigatórios
- **THEN** o sistema responde HTTP 401 com o corpo público exato `{"error":"Não autenticado."}`, sem outros campos, credencial esperada, configuração, existência parcial, dados operacionais ou erro de campo do payload
- **AND** não executa validação funcional de presença, leitura, persistência, cálculo de heartbeat, alteração de disponibilidade ou incidente antes da rejeição

#### Scenario: Credencial do Simulator indisponível no servidor
- **WHEN** a credencial técnica do Simulator não está disponível na configuração do servidor
- **THEN** o sistema responde HTTP 401 com o mesmo corpo público exato `{"error":"Não autenticado."}` da credencial ausente ou inválida, sem outros campos
- **AND** falha fechado sem aceitar valores vazios ou nulos

#### Scenario: Chave Simulator válida com payload incompleto
- **WHEN** `POST /telemetria_equipamentos` contém `X-MIRA-Simulator-Key` válido e o payload não contém um ou mais campos funcionais obrigatórios
- **THEN** o sistema rejeita a requisição com erro funcional de payload, sem persistir telemetria
- **AND** não responde HTTP 401

#### Scenario: Chave Simulator válida
- **WHEN** o Simulator envia `X-MIRA-Simulator-Key` com a credencial válida para sua finalidade e payload funcional válido
- **THEN** o endpoint preserva URL, método e payload funcional bem-sucedido atuais

#### Scenario: Credencial do Simulator ausente no processo
- **WHEN** o processo Simulator não possui sua credencial técnica
- **THEN** ele falha explicitamente antes de enviar chamada anônima
