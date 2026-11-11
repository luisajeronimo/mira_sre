# vinculo-historico-totem-loja Specification

## Purpose
Definir o vínculo histórico comprovado entre Totem e Loja e a resolução da Loja de um fato no instante em que ele ocorreu, sem inferência retroativa para chamados legados.

## Requirements

### Requirement: Vínculo histórico registra a Loja comprovada de um Totem por instante
O Xano DEVE (MUST) manter `historico_vinculos_totem_loja` com `ativos_referencia_id`, `loja_origem_id` opcional, `loja_destino_id`, `tipo` ∈ {`criacao`, `marco`, `transferencia`} e `efetivado_em`, com no máximo um vínculo por Totem e instante. Cada vínculo DEVE (MUST) comprovar que, a partir de `efetivado_em`, o Totem pertence a `loja_destino_id`. O sistema NÃO DEVE (MUST NOT) registrar vínculo com instante anterior ao momento em que o fato que o origina ocorreu.

#### Scenario: Criação de Totem
- **WHEN** o Administrador cria um Totem associado a uma Loja
- **THEN** o Xano registra um vínculo `criacao` para essa Loja no instante da criação

#### Scenario: Transferência com mudança de Loja
- **WHEN** o Administrador transfere um Totem para Loja diferente da atual
- **THEN** o Xano registra um vínculo `transferencia` com origem, destino e o instante da transferência, e atualiza a Loja atual do Totem

#### Scenario: Atualização sem mudança de Loja
- **WHEN** o Administrador altera dados do Totem mantendo a mesma Loja
- **THEN** nenhum vínculo é registrado

### Requirement: Loja de um fato é resolvida pelo vínculo vigente no instante
O Xano DEVE (MUST) resolver a Loja de um fato de Totem (por exemplo, a criação de um chamado) como `loja_destino_id` do vínculo mais recente com `efetivado_em` menor ou igual ao instante do fato. Sem vínculo nessas condições, ou sem instante, a Loja resolvida DEVE (MUST) ser nula. A resolução NÃO DEVE (MUST NOT) usar a Loja atual do Totem, `created_at` ou qualquer outra estimativa.

#### Scenario: Totem com vínculo anterior ao chamado
- **WHEN** o Totem possui vínculo com `efetivado_em` anterior ou igual ao `criado_em` do chamado
- **THEN** a Loja do chamado é o destino do vínculo mais recente nessas condições

#### Scenario: Totem transferido depois da abertura
- **WHEN** o Totem foi transferido para outra Loja depois do `criado_em` do chamado
- **THEN** a Loja do chamado continua sendo a Loja vigente no instante da abertura

#### Scenario: Totem sem vínculo histórico
- **WHEN** o Totem não possui vínculo com `efetivado_em` anterior ou igual ao `criado_em` do chamado
- **THEN** a Loja do chamado é nula, inclusive quando o Totem possui Loja atual

### Requirement: Chamado novo comprova a Loja do Totem sem histórico
Ao criar um chamado novo, por abertura manual ou por incidente automático de heartbeat, para Totem que não possui nenhum vínculo, o Xano DEVE (MUST) registrar um vínculo `marco` com a Loja atual do Totem e `efetivado_em` igual ao `criado_em` do novo chamado, desde que o Totem tenha Loja atual. Se o Totem já possuir qualquer vínculo, ou não possuir Loja atual, nenhum marco DEVE (MUST) ser registrado.

#### Scenario: Chamado novo com criação de marco
- **WHEN** um chamado é criado para Totem sem nenhum vínculo histórico
- **THEN** o Xano registra o marco no instante do chamado e a Loja desse chamado passa a ser resolvida para a Loja atual do Totem

#### Scenario: Totem com histórico existente
- **WHEN** um chamado é criado para Totem que já possui vínculo
- **THEN** nenhum vínculo é registrado e a Loja do chamado é resolvida pelo histórico existente

#### Scenario: Abertura manual sem Loja atual
- **WHEN** a abertura manual é solicitada para um Totem sem histórico e sem Loja atual
- **THEN** a abertura é rejeitada e nenhum marco é registrado

#### Scenario: Incidente automático sem Loja atual
- **WHEN** o heartbeat cria um incidente automático para Totem sem histórico e sem Loja atual
- **THEN** o incidente é criado sem marco, sua Loja histórica permanece nula e ele não pertence à Loja de nenhum Gerente

### Requirement: Chamados legados não recebem vínculo retroativo
O sistema NÃO DEVE (MUST NOT) criar vínculos com `efetivado_em` anterior ao fato que os origina, preencher automaticamente vínculos para chamados existentes, nem usar a Loja atual como substituta da Loja histórica. Chamado sem evidência histórica DEVE (MUST) permanecer com Loja resolvida nula.

#### Scenario: Chamado legado sem evidência
- **WHEN** um chamado criado antes de qualquer vínculo do seu Totem é consultado
- **THEN** a Loja resolvida é nula e nenhum vínculo é criado pela consulta

#### Scenario: Marco não retroage
- **WHEN** um marco é registrado pela criação de um chamado novo
- **THEN** chamados anteriores do mesmo Totem continuam com Loja resolvida nula

### Requirement: DTOs de chamado apresentam a Loja histórica
Os contratos que expõem a Loja de um chamado (fila e detalhe globais, detalhe do Gerente, detalhe do solicitante e detalhe de monitoramento do incidente) DEVEM (MUST) apresentar a Loja resolvida pelo vínculo vigente no `criado_em` do chamado, como `{id, nome}` ou nula, sem substituí-la pela Loja atual.

#### Scenario: Loja histórica disponível
- **WHEN** o chamado possui Loja resolvida
- **THEN** o DTO apresenta essa Loja, mesmo que o Totem tenha sido transferido depois

#### Scenario: Loja histórica ausente
- **WHEN** o chamado não possui Loja resolvida
- **THEN** o DTO apresenta a Loja como nula
