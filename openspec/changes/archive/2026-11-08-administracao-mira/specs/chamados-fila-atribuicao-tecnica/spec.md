# Spec Delta

## ADDED Requirements

### Requirement: Fila global preserva Loja histórica de chamados
Quando um Totem muda de Loja, a fila, o detalhe e filtros por Loja DEVEM (MUST) usar o vínculo demonstrável no `criado_em` de cada chamado, sem reclassificar fatos anteriores pelo vínculo atual. Chamado sem Loja histórica comprovável DEVE (MUST) continuar na consulta global sem atribuição de Loja presumida.

#### Scenario: Filtro por Loja após transferência
- **WHEN** perfil global filtra a fila pela Loja de origem após transferência de Totem com histórico comprovado
- **THEN** chamados anteriores à transferência continuam nesse resultado e novos chamados pertencem à Loja de destino

#### Scenario: Chamado legado sem Loja comprovada
- **WHEN** um chamado global não possui vínculo histórico demonstrável
- **THEN** permanece consultável na fila global sem Loja atribuída e não aparece indevidamente em filtro por Loja atual do Totem
