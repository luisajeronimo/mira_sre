# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente pode consultar o detalhe básico do chamado
O sistema DEVE (MUST) fornecer uma página de detalhe que consulte `GET /gerente/chamados/{chamados_id}` e apresente identificação, título, descrição, status, prioridade, origem, abertura, última atualização, SLA aplicado, ativo, Loja, categoria, solicitante e técnico quando houver. A página DEVE (MUST) oferecer botão Detalhe do Totem que abre drawer lateral direito, com superfície própria, largura adequada e rolagem interna, fechável por X, com o resumo autorizado do Totem. A telemetria NÃO DEVE (MUST NOT) duplicar-se no corpo do chamado. A página DEVE (MUST) consultar e apresentar separadamente os comentários públicos autorizados do chamado, sem oferecer edição do chamado, mudança de status, atribuição, diagnóstico, solução ou resolução nesta capacidade.

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

### Requirement: Reflex controla filtros, ordenação e contadores da lista
O State DEVE (MUST) restaurar antes da consulta os filtros básicos confirmados persistidos por Gerente autenticado e reutilizar o catálogo de ativos já carregado ao aplicar ordenação, filtros ou limpeza. Essas interações DEVEM (MUST) consultar o endpoint de chamados e NÃO DEVEM (MUST NOT) repetir consultas auxiliares desnecessárias que possam gerar request storm. Somente aplicar e limpar alteram a preferência; a ordenação permanece local e selecionada.

#### Scenario: Preferência restaurada
- **WHEN** o Gerente navega de volta para a lista ou autentica novamente
- **THEN** o State recupera número, Status, Totem e os dois períodos confirmados e consulta a lista da própria Loja

#### Scenario: Ordenações consecutivas
- **WHEN** o Gerente alterna a ordenação várias vezes após o catálogo de ativos ter sido carregado
- **THEN** cada consulta de lista mantém a sessão e não dispara nova consulta de ativos

#### Scenario: Aplicação e limpeza de filtros
- **WHEN** o Gerente aplica ou limpa critérios de filtro
- **THEN** o State consulta novamente a lista, preserva a ordenação selecionada, apresenta os critérios efetivamente aplicados e atualiza a preferência somente após consulta válida

#### Scenario: Ordenação de coluna
- **WHEN** o Gerente escolhe uma coluna ordenável e direção
- **THEN** o Reflex solicita a ordenação autorizada ao backend, sem ordenar somente a coleção local nem alterar a preferência de filtros

#### Scenario: Falha de consulta não encerra sessão confirmada
- **WHEN** uma consulta de lista, filtro ou ordenação falha por indisponibilidade, timeout ou contrato incompatível
- **THEN** o Reflex apresenta erro sanitizado de serviço e preserva a identidade já confirmada; somente falha real de autenticação pode redirecionar ao login

#### Scenario: Falha de persistência não encerra sessão confirmada
- **WHEN** o save de preferência falha por indisponibilidade, timeout ou contrato incompatível
- **THEN** o Reflex apresenta erro sanitizado de serviço, preserva a identidade e o último estado confirmado; somente falha real de autenticação pode redirecionar ao login

#### Scenario: Contadores da consulta atual
- **WHEN** a lista responde a uma consulta com ou sem filtros
- **THEN** a interface apresenta o total filtrado e o tamanho atual de `items`
