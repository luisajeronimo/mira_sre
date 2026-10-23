# Spec Delta

## ADDED Requirements

### Requirement: Lista do Gerente comunica a direção da ordenação
A lista de chamados do Gerente DEVE (MUST) exibir, junto ao título ordenável
ativo, somente a seta da direção selecionada: subida para `ASC` e descida para
`DESC`. Títulos inativos NÃO DEVEM (MUST NOT) exibir seta, e a interface NÃO
DEVE (MUST NOT) exibir os literais `ASC` ou `DESC`.

#### Scenario: Direção ativa na lista do Gerente
- **WHEN** a lista é exibida com uma coluna e direção selecionadas
- **THEN** somente o ícone correspondente à direção ativa aparece no respectivo
  cabeçalho, e os demais cabeçalhos não exibem ícone

#### Scenario: Clique mantém a ordenação gerencial existente
- **WHEN** o Gerente clica um título ordenável
- **THEN** a interação existente alterna ou inicia a direção e solicita a lista
  ao backend, sem alterar filtros, colunas ou contratos
