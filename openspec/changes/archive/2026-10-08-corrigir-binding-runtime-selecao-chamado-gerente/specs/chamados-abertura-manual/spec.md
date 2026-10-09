# Spec Delta

## MODIFIED Requirements

### Requirement: Seleção manual preserva os identificadores funcionais
Durante a abertura manual, o sistema DEVE (MUST) manter o identificador do ativo e da categoria selecionados separado do texto apresentado e usar esses identificadores mantidos no State na validação e no payload de criação, independentemente de eventos de interface transmitidos no acionamento do salvamento.

#### Scenario: Ativo e categoria selecionados
- **WHEN** o Gerente seleciona um ativo e uma categoria válidos nos catálogos exibidos
- **THEN** a seleção atual permanece disponível no State e o salvamento envia os respectivos identificadores numéricos ao contrato de abertura

#### Scenario: Labels não são autoridade
- **WHEN** o nome exibido de um ativo ou categoria contém texto formatado para apresentação
- **THEN** o backend recebe somente o identificador correspondente, sem usar o label como valor funcional

#### Scenario: Acionamento por clique do botão Salvar
- **WHEN** o Gerente clica no botão Salvar após selecionar ativo e categoria
- **THEN** a ação de abertura consome os valores selecionados no State e não descarta a seleção em decorrência do evento de clique da interface
