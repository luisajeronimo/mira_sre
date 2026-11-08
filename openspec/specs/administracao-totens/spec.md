# administracao-totens Specification

## Purpose

Definir a gestão de Totens pelo Administrador, incluindo vínculo atual com Loja e preservação dos fatos operacionais quando esse vínculo muda.

## Requirements

### Requirement: Administrador cria Totem em Loja Ativa
O Xano DEVE (MUST) permitir somente a Administrador autenticado e sem pendência criar Totem com identificação, nome e Loja existente `Ativa`. A criação DEVE (MUST) manter o estado operacional sem classificação `Online` ou `Offline` até existir primeira telemetria válida.

#### Scenario: Criação válida sem telemetria
- **WHEN** Administrador cria Totem com identificação e nome não vazios em Loja `Ativa`
- **THEN** o Totem recebe ID e vínculo temporal inicial com a Loja, sem estado operacional artificial nem evento de disponibilidade

#### Scenario: Dados ou Loja inválidos
- **WHEN** identificação ou nome está vazio, ou a Loja não existe ou está `Inativa`
- **THEN** o Xano rejeita a criação sem persistir Totem

### Requirement: Administração lista e consulta Totens
O Xano DEVE (MUST) fornecer listagem e detalhe administrativos de Totens com identificação, nome, Loja atual e estado operacional persistido, inclusive quando a Loja está `Inativa` ou o estado ainda é desconhecido. Somente Administrador pode usar esses contratos.

#### Scenario: Totem em Loja Inativa
- **WHEN** Administrador consulta Totem já vinculado a Loja `Inativa`
- **THEN** o cadastro permanece consultável sem reclassificar o estado operacional

#### Scenario: Perfil indevido
- **WHEN** outro perfil ou sessão pendente chama contrato administrativo de Totens
- **THEN** o Xano rejeita sem expor dados

### Requirement: Administrador edita cadastro e transfere Totem
O Xano DEVE (MUST) permitir edição de identificação e nome e transferência para Loja existente `Ativa`, preservando o ID. A transferência DEVE (MUST) aplicar a nova Loja às operações futuras e NÃO DEVE (MUST NOT) alterar fatos anteriores de telemetria, disponibilidade ou chamados.

#### Scenario: Transferência válida
- **WHEN** Administrador transfere Totem para outra Loja `Ativa`
- **THEN** o ID é preservado, a transferência temporal e o vínculo atual mudam juntos, e fatos anteriores permanecem intactos

#### Scenario: Loja de destino inválida
- **WHEN** a Loja de destino não existe ou está `Inativa`
- **THEN** o Xano rejeita a transferência sem alterar o vínculo atual

#### Scenario: Falha durante transferência
- **WHEN** registro temporal ou atualização do vínculo atual falha
- **THEN** nenhuma das duas alterações permanece parcialmente aplicada

### Requirement: Vínculo temporal determina Loja da ocorrência
O Xano DEVE (MUST) registrar criação e transferências de Totem com instante efetivo e origem/destino. Para chamado, telemetria ou evento com vínculo demonstrável, a Loja DEVE (MUST) ser a vigente em seu instante funcional. Sem evidência temporal suficiente, o sistema NÃO DEVE (MUST NOT) usar a Loja atual como Loja histórica presumida.

#### Scenario: Fato em cada lado da transferência
- **WHEN** existem fatos do Totem antes e depois de uma transferência registrada, ambos com vínculo temporal demonstrável
- **THEN** cada fato é atribuído à Loja válida no próprio instante, sem reescrever seu registro

#### Scenario: Fato exatamente na transferência
- **WHEN** um fato ocorre no mesmo instante efetivo da transferência
- **THEN** ele é atribuído à Loja de destino

#### Scenario: Fato legado sem origem comprovada
- **WHEN** fato anterior ao primeiro vínculo temporal comprovado não possui outra evidência confiável de Loja
- **THEN** sua Loja histórica permanece indeterminada, sem backfill ou inferência pelo vínculo atual

#### Scenario: Primeiro chamado novo de Totem legado
- **WHEN** um chamado novo é aberto antes da primeira transferência de Totem legado sem vínculo temporal registrado
- **THEN** o Xano registra a Loja atual comprovada no instante do chamado, preserva a Loja indeterminada dos fatos anteriores e mantém o novo chamado no escopo histórico correto

### Requirement: Exclusão física de Totem respeita dependências
O Xano DEVE (MUST) excluir fisicamente Totem somente sem telemetria, eventos de disponibilidade, chamados, preferências, transferências ou outro vínculo ou histórico impeditivo. Quando houver somente o vínculo temporal inicial e nenhum fato operacional, o Xano DEVE (MUST) remover explicitamente esse vínculo junto do Totem na mesma operação. A exclusão NÃO DEVE (MUST NOT) ocorrer em cascata automática.

#### Scenario: Totem sem dependências
- **WHEN** Administrador exclui Totem sem vínculos ou fatos históricos impeditivos
- **THEN** somente o cadastro do Totem é removido

#### Scenario: Totem com histórico
- **WHEN** Totem possui telemetria, chamado ou evento de disponibilidade
- **THEN** o Xano retorna erro funcional e preserva todos os registros

#### Scenario: Totem nunca usado
- **WHEN** Totem possui somente o vínculo temporal inicial, sem transferência nem fato operacional
- **THEN** o Xano remove explicitamente o vínculo inicial e o Totem na mesma operação, sem apagar outros registros
