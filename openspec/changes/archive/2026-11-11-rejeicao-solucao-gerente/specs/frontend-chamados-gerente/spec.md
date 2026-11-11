# Spec Delta

## ADDED Requirements

### Requirement: Gerente rejeita solução pelo detalhe do chamado
O Reflex DEVE (MUST) apresentar no detalhe do Gerente a ação "Rejeitar solução" somente quando o status do detalhe for `Resolvido`. A interface DEVE (MUST) exigir justificativa não vazia após trim antes do envio, transmitir somente a justificativa e o `ultima_atualizacao_em` do detalhe confirmado e NÃO DEVE (MUST NOT) enviar autor, Loja, status, visibilidade ou timestamp funcional. A condição visual e a validação local NÃO DEVEM (MUST NOT) ser tratadas como autorização. A interface DEVE (MUST) apresentar carregamento, sucesso e erro sem simular a transição.

#### Scenario: Rejeição confirmada
- **WHEN** o Gerente envia justificativa válida e o Xano confirma
- **THEN** o Reflex apresenta sucesso, atualiza o detalhe com o status retornado e a justificativa entre os comentários públicos e limpa o campo

#### Scenario: Justificativa vazia
- **WHEN** a justificativa está vazia ou contém somente espaços
- **THEN** o Reflex informa a validação e não chama o contrato

#### Scenario: Ação indisponível fora de Resolvido
- **WHEN** o detalhe apresenta status diferente de `Resolvido`
- **THEN** o Reflex não oferece a ação

#### Scenario: Envio em andamento
- **WHEN** a rejeição está em processamento
- **THEN** o Reflex impede envio duplicado e informa o carregamento

#### Scenario: Rejeição recusada
- **WHEN** o Xano recusa por autorização, justificativa, status ou detalhe desatualizado
- **THEN** o Reflex não altera o status localmente, preserva a justificativa e apresenta erro sanitizado; em conflito, informa e recarrega o detalhe

## MODIFIED Requirements

### Requirement: Gerente pode consultar o detalhe básico do chamado
O sistema DEVE (MUST) fornecer uma página de detalhe que consulte `GET /gerente/chamados/{chamados_id}` e apresente identificação, título, descrição, status, prioridade, origem, abertura, última atualização, SLA aplicado, ativo, Loja, categoria, solicitante e técnico quando houver. A página DEVE (MUST) oferecer botão Detalhe do Totem que abre drawer lateral direito, com superfície própria, largura adequada e rolagem interna, fechável por X, com o resumo autorizado do Totem. A telemetria NÃO DEVE (MUST NOT) duplicar-se no corpo do chamado. A página DEVE (MUST) consultar e apresentar separadamente os comentários públicos autorizados do chamado, sem oferecer edição do chamado, mudança de status, atribuição, diagnóstico, solução ou resolução nesta capacidade, com a única exceção da ação específica de rejeitar solução em chamado `Resolvido`.

#### Scenario: Detalhe carregado
- **WHEN** o Xano retorna um chamado autorizado da Loja
- **THEN** o Reflex apresenta seus dados funcionais, incluindo ativo, Loja, categoria, solicitante, técnico quando houver e última atualização, sem usar `created_at` como abertura

#### Scenario: Drawer do Totem
- **WHEN** o Gerente aciona Detalhe do Totem
- **THEN** o Reflex abre drawer à direita com Totem, Loja, estado, valores e
  timestamp da última telemetria autorizada, sem navegar para `/monitoramento`

#### Scenario: Telemetria ausente
- **WHEN** o resumo do Totem retorna telemetria nula
- **THEN** o drawer informa a ausência sem exibir valores inventados

#### Scenario: Técnico ainda não atribuído
- **WHEN** o detalhe retorna técnico nulo
- **THEN** o Reflex apresenta a ausência de atribuição sem oferecer ação para atribuir ou assumir

#### Scenario: Comentários públicos carregados
- **WHEN** a consulta de comentários públicos do chamado é aceita
- **THEN** o Reflex apresenta somente os comentários retornados, do mais recente ao mais antigo

#### Scenario: Sem ações técnicas
- **WHEN** o detalhe está em qualquer status
- **THEN** o Reflex não oferece Save operacional, mudança direta de status, atribuição ou comentário interno ao Gerente
