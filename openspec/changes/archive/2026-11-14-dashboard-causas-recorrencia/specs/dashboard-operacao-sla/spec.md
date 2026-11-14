## MODIFIED Requirements

### Requirement: Recortes gerenciais de operação são explícitos
O dashboard DEVE (MUST) aplicar período civil em `America/Sao_Paulo` à volumetria e à conformidade, e permitir filtros por Loja histórica comprovada no `criado_em` do chamado e por Categoria. O atalho Hoje da página compartilhada DEVE (MUST) selecionar `[00h local, 00h local do dia seguinte)` e limitar os fatos observáveis ao instante da consulta, sem antecipar chamados ou transições futuras. O risco atual DEVE (MUST) usar Loja e Categoria, mas não restringir sua base ao período selecionado. Filtros inválidos DEVEM (MUST) ser rejeitados.

Na página compartilhada, Disponibilidade, Chamados/SLA e Causas/recorrência DEVEM (MUST) ocupar abas distintas sob o breadcrumb, sem criar outra entrada na sidebar. O período e a Loja DEVEM (MUST) afetar os painéis aos quais se aplicam; Totem aparece nas abas de disponibilidade e causas/recorrência; Categoria aparece nas abas de chamados/SLA e causas/recorrência. A interface DEVE (MUST) identificar esses escopos para não sugerir que um filtro afeta painéis incompatíveis.

#### Scenario: Loja histórica após transferência
- **WHEN** um Totem é transferido após a abertura do chamado
- **THEN** o filtro por Loja usa o vínculo comprovado no `criado_em`, sem substituí-lo pela Loja atual

#### Scenario: Risco atual com período curto
- **WHEN** a Diretoria seleciona Hoje e há chamado antigo ainda em contagem de SLA
- **THEN** o chamado pode entrar no risco atual, com indicação de que esse painel é um retrato do instante da consulta

#### Scenario: Período ou filtro inválido
- **WHEN** o período é invertido, futuro ou Loja/Categoria informada é inválida
- **THEN** o Xano rejeita a entrada sem retornar agregados

#### Scenario: Filtros específicos na página compartilhada
- **WHEN** a Diretoria seleciona Totem e Categoria na mesma página
- **THEN** Totem recorta disponibilidade/MTTD/MTTR e causas/recorrência, Categoria recorta volumetria/SLA e causas/recorrência, e os escopos ficam visíveis

#### Scenario: Troca entre as abas executivas
- **WHEN** a Diretoria alterna entre Disponibilidade, Chamados/SLA e Causas/recorrência
- **THEN** vê apenas os painéis e filtros próprios da aba selecionada, preservando o período e a Loja escolhidos
