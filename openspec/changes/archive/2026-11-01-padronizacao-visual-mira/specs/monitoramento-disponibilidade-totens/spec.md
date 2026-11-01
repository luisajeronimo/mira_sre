# Spec Delta

## ADDED Requirements

### Requirement: Estados operacionais preservam dados e usam badge consistente
A página de monitoramento DEVE (MUST) apresentar estados persistidos de Totens
e incidentes em maiúsculas com o mesmo padrão semântico de badge da interface.
A apresentação NÃO DEVE (MUST NOT) alterar valores, cálculos, autorização ou
fatos persistidos.

#### Scenario: Totem retorna estado persistido
- **WHEN** a consulta existente retorna `online` ou `offline`
- **THEN** a interface exibe respectivamente `ONLINE` ou `OFFLINE` como
  apresentação visual, mantendo o valor retornado pela consulta
