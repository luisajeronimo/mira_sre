# Spec Delta

## ADDED Requirements

### Requirement: Fiscal exige URL operacional explícita
O processo Fiscal DEVE (MUST) exigir `XANO_BASE_URL` configurada explicitamente e não DEVE (MUST NOT) usar URL remota embutida como fallback.

#### Scenario: URL ausente ou vazia
- **WHEN** o Fiscal inicia com `XANO_BASE_URL` ausente ou vazia
- **THEN** ele falha com erro claro antes de qualquer request de heartbeat

#### Scenario: URL configurada
- **WHEN** `XANO_BASE_URL` e a credencial técnica estão configuradas
- **THEN** o Fiscal usa a URL informada para o mesmo `GET /verificar-falhas` com a autenticação existente
