# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente acompanha todos os chamados da própria Loja
O sistema DEVE (MUST) fornecer `GET /gerente/chamados` e `GET /gerente/chamados/{chamados_id}` no grupo `mira-service-desk`. A lista DEVE (MUST) retornar `items` com resumo funcional e `total` correspondente à consulta atual; o detalhe DEVE (MUST) retornar um objeto `chamado` com os campos do contrato de criação. Ambos DEVEM (MUST) determinar pertencimento à Loja pela Loja resolvida pelo vínculo histórico do Totem no `criado_em` do chamado (`vinculo-historico-totem-loja`), independentemente do solicitante e da origem. Chamado sem Loja resolvida NÃO DEVE (MUST NOT) aparecer na lista nem ser autorizado no detalhe de nenhum Gerente.

#### Scenario: Lista da Loja
- **WHEN** um Gerente autenticado consulta a lista de chamados
- **THEN** o Xano retorna todos os chamados cuja Loja resolvida é a sua, incluindo chamados de outros solicitantes e chamados automáticos, sem retornar chamados de outras Lojas nem chamados sem Loja resolvida

#### Scenario: Detalhe da própria Loja
- **WHEN** um Gerente consulta o identificador de um chamado cuja Loja resolvida é a sua
- **THEN** o Xano retorna o detalhe funcional do chamado com a Loja histórica

#### Scenario: Detalhe de outra Loja
- **WHEN** um Gerente consulta o identificador de um chamado cuja Loja resolvida é outra Loja
- **THEN** o Xano rejeita a operação como não autorizada sem retornar os dados do chamado

#### Scenario: Detalhe sem Loja histórica
- **WHEN** um Gerente consulta o identificador de um chamado cuja Loja resolvida é nula
- **THEN** o Xano rejeita a operação como não autorizada sem retornar os dados do chamado

#### Scenario: Loja histórica indeterminada
- **WHEN** o chamado legado não possui vínculo de Loja demonstrável em `criado_em`
- **THEN** o Xano não o atribui à Loja atual do Totem nem o expõe ao Gerente

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta um identificador de chamado que não existe
- **THEN** o Xano responde como recurso não encontrado
