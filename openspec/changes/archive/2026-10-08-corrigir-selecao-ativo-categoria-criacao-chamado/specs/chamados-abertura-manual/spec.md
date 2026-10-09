# Spec Delta

## ADDED Requirements

### Requirement: Seleção manual preserva os identificadores funcionais
Durante a abertura manual, o sistema DEVE (MUST) manter o identificador do ativo e da categoria selecionados separado do texto apresentado e usar esses identificadores na validação e no payload de criação.

#### Scenario: Ativo e categoria selecionados
- **WHEN** o Gerente seleciona um ativo e uma categoria válidos nos catálogos exibidos
- **THEN** a seleção atual permanece disponível no State e o salvamento envia os respectivos identificadores numéricos ao contrato de abertura

#### Scenario: Labels não são autoridade
- **WHEN** o nome exibido de um ativo ou categoria contém texto formatado para apresentação
- **THEN** o backend recebe somente o identificador correspondente, sem usar o label como valor funcional

### Requirement: Abertura rejeita seleção incompleta antes do request
A abertura manual DEVE (MUST) rejeitar a submissão quando o ativo ou a categoria não estiver selecionado com um identificador positivo e NÃO DEVE (MUST NOT) executar o request de criação nessa condição.

#### Scenario: Ativo ausente
- **WHEN** a categoria está selecionada e o ativo está vazio ou inválido
- **THEN** o sistema mantém a mensagem de seleção e não cria chamado

#### Scenario: Categoria ausente
- **WHEN** o ativo está selecionado e a categoria está vazia ou inválida
- **THEN** o sistema mantém a mensagem de seleção e não cria chamado

#### Scenario: Ambos ausentes
- **WHEN** o Gerente tenta salvar sem ativo e sem categoria
- **THEN** o sistema rejeita a submissão antes do backend e não cria chamado

#### Scenario: Ambos válidos
- **WHEN** ativo, categoria e os demais campos obrigatórios são válidos
- **THEN** a validação de seleção é aprovada e o fluxo existente prossegue para a criação do chamado
