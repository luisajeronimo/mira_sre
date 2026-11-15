## ADDED Requirements

### Requirement: Visibilidade do comentário usa controle compacto acima do texto
No detalhe operacional, a visibilidade DEVE (MUST) ser apresentada acima da caixa de comentário em um seletor compacto e rotulado. A opção selecionada e os eventos de alteração DEVEM (MUST) permanecer os existentes. Quando a regra de status exigir comentário público, a interface DEVE (MUST) preservar a indicação fixa de Público.

#### Scenario: Visibilidade pode ser escolhida
- **WHEN** o comentário permite Público ou Interno
- **THEN** o usuário escolhe em um seletor compacto acima da caixa de texto, com navegação por teclado e indicação da seleção

#### Scenario: Status exige Público
- **WHEN** o destino da alteração exige comentário público
- **THEN** a composição mantém Público fixo e não permite contornar a exigência pela troca do controle

### Requirement: Histórico mantém uma superfície por registro
O detalhe DEVE (MUST) manter comentários e eventos em ordem cronológica vigente, com hierarquia entre título, autor, data, conteúdo e diferenças. As diferenças do mesmo evento DEVEM (MUST) permanecer agrupadas, sem caixas ou bordas individuais aninhadas para cada campo. Conteúdos longos DEVEM (MUST) caber no painel sem corte ou rolagem horizontal da página.

#### Scenario: Vários campos foram alterados
- **WHEN** um evento contém diferenças de mais de um campo
- **THEN** apresenta todos os pares anterior/resultante em grade compacta, com colunas ajustadas ao conteúdo e menor espaçamento entre diferenças, sem card individual para cada diferença

#### Scenario: Comentário acompanha a alteração
- **WHEN** comentário e evento são agrupados pela correlação já existente
- **THEN** preserva conteúdo e metadados no mesmo registro visual, sem caixa adicional em torno do comentário

### Requirement: Autoria repetida é apresentada uma vez no agrupamento
Quando evento e comentário correlacionados possuem o mesmo autor, a interface DEVE (MUST) apresentar sua autoria uma única vez. Se os autores forem distintos, DEVE (MUST) preservar ambas as autorias com contexto. A visibilidade DEVE (MUST) continuar vinculada somente ao comentário, sem atribuí-la ao evento operacional.

#### Scenario: Mesmo autor nos dois fatos
- **WHEN** evento e comentário correlacionado foram produzidos pela mesma identidade
- **THEN** o nome do autor não é repetido dentro do agrupamento

#### Scenario: Autores distintos
- **WHEN** evento e comentário correlacionado possuem identidades diferentes
- **THEN** ambos os autores continuam identificados, inclusive se seus nomes de exibição coincidirem

#### Scenario: Comentário público ou interno
- **WHEN** o registro visual contém comentário com classificação explícita
- **THEN** apresenta o badge do comentário abaixo da data no cabeçalho do registro, inclusive quando agrupado com uma alteração, sem classificar o evento operacional
