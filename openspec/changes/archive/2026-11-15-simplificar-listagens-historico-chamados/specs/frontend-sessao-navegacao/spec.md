## ADDED Requirements

### Requirement: Listagens apresentam nomes sem IDs internos
Listagens, filtros e seletores DEVEM (MUST) apresentar Totens e Lojas pelo nome, sem prefixar ou acrescentar IDs internos. A fila de chamados DEVE (MUST) aplicar o mesmo padrão aos Técnicos. Os valores usados para seleção, consulta e preferências DEVEM (MUST) preservar os identificadores originais, sem usar nomes como chaves.

#### Scenario: Opções conhecidas são apresentadas
- **WHEN** a interface apresenta uma opção de Técnico na fila, Totem ou Loja
- **THEN** mostra o nome sem ID interno e mantém o valor original ao selecionar a opção

#### Scenario: Nomes repetidos ou com separadores
- **WHEN** duas opções possuem o mesmo nome ou o nome contém um travessão
- **THEN** cada opção conserva seu valor e seleção independentes, e o nome é apresentado integralmente

#### Scenario: Preferência existente é restaurada
- **WHEN** uma preferência salva por identificadores é carregada
- **THEN** as opções continuam selecionadas com nomes sem IDs, sem alterar o recorte nem regravar a preferência por nome

#### Scenario: Número do chamado e identificação do equipamento
- **WHEN** a página apresenta o número de um chamado ou um código de identificação pertencente ao cadastro
- **THEN** preserva esses dados, distinguindo-os dos IDs internos ocultados nas opções
