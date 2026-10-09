# Spec Delta

## MODIFIED Requirements

### Requirement: Listagem técnica retorna DTO funcional estável

O sistema DEVE (MUST) retornar em cada item da fila `id`, `titulo`, `status`, `prioridade`, `origem`, `criado_em`, `ultima_atualizacao_em`, `sla_horas_aplicado`, `atribuido_em`, ativo, categoria, solicitante e técnico atual quando existir. Todo chamado válido possui ambos os timestamps funcionais; o contrato NÃO DEVE (MUST NOT) inferi-los de `created_at` nem apresentar fallback temporal para registros históricos que os tenham ausentes.

#### Scenario: Chamado manual na fila

- **WHEN** um chamado manual elegível e válido é retornado
- **THEN** a resposta preserva origem manual, prioridade, os dois timestamps funcionais, snapshot de SLA, ativo, categoria e Técnico atual

#### Scenario: Chamado automático na fila

- **WHEN** um chamado automático elegível e válido é retornado
- **THEN** a resposta preserva origem automática, os dois timestamps funcionais e os demais dados já persistidos, sem alterar a regra do heartbeat

#### Scenario: Chamado legado na consulta

- **WHEN** um registro histórico elegível possui origem, SLA ou atribuição ausentes
- **THEN** a resposta preserva esses campos como nulos sem inferência; timestamps funcionais ausentes não recebem fallback nem tornam o registro compatível com a jornada operacional
