# Spec Delta

## MODIFIED Requirements

### Requirement: Reflex controla filtros, ordenação e contadores da lista
O State DEVE (MUST) restaurar antes da consulta os filtros básicos confirmados persistidos por Gerente autenticado e reutilizar o catálogo de Totens da Loja atual já carregado ao aplicar ordenação, filtros ou limpeza. Essas interações DEVEM (MUST) consultar o endpoint de chamados e NÃO DEVEM (MUST NOT) repetir consultas auxiliares desnecessárias que possam gerar request storm. Somente aplicar e limpar alteram a preferência; a ordenação permanece local e selecionada.

#### Scenario: Preferência restaurada
- **WHEN** o Gerente navega de volta para a lista ou autentica novamente
- **THEN** o State recupera número, Status, Totem atualmente elegível e os dois períodos confirmados e consulta a lista da própria Loja

#### Scenario: Ordenações consecutivas
- **WHEN** o Gerente alterna a ordenação várias vezes após o catálogo de ativos ter sido carregado
- **THEN** cada consulta de lista mantém a sessão e não dispara nova consulta de ativos

#### Scenario: Aplicação e limpeza de filtros
- **WHEN** o Gerente aplica ou limpa critérios de filtro
- **THEN** o State consulta novamente a lista, preserva a ordenação selecionada, apresenta os critérios efetivamente aplicados e atualiza a preferência somente após consulta válida

#### Scenario: Totem transferido não aparece no filtro
- **WHEN** um Totem já pertenceu à Loja do Gerente, mas sua Loja atual é outra
- **THEN** o State não o apresenta nas opções do filtro nem como seleção restaurada

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
