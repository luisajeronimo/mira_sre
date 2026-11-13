# dashboard-operacao-sla Specification

## Purpose

Permitir que a Diretoria acompanhe o volume de chamados por status e a situação de SLA com dados persistidos, recortes gerenciais explícitos e distinção entre resultado do período e risco atual.

## Requirements

### Requirement: Consulta executiva de operação exige Diretoria autenticada
Os contratos e painéis de volumetria e SLA DEVEM (MUST) atender somente à Diretoria autenticada, com sessão válida e troca de senha concluída. O Xano DEVE (MUST) aplicar a autorização a cada consulta antes de ler chamados.

#### Scenario: Diretoria consulta a operação
- **WHEN** usuário da Diretoria com sessão válida consulta os indicadores
- **THEN** recebe os agregados correspondentes aos filtros válidos

#### Scenario: Outro perfil ou sessão inválida
- **WHEN** Gerente, Técnico, Administrador, usuário anônimo ou sessão com troca pendente consulta diretamente o contrato
- **THEN** a consulta é negada sem dados de chamados ou SLA

### Requirement: Recortes gerenciais de operação são explícitos
O dashboard DEVE (MUST) aplicar período civil em `America/Sao_Paulo` à volumetria e à conformidade, e permitir filtros por Loja histórica comprovada no `criado_em` do chamado e por Categoria. O atalho Hoje da página compartilhada DEVE (MUST) selecionar `[00h local, 00h local do dia seguinte)` e limitar os fatos observáveis ao instante da consulta, sem antecipar chamados ou transições futuras. O risco atual DEVE (MUST) usar Loja e Categoria, mas não restringir sua base ao período selecionado. Filtros inválidos DEVEM (MUST) ser rejeitados.

Na página compartilhada, Disponibilidade e Chamados/SLA DEVEM (MUST) ocupar abas distintas sob o breadcrumb, sem criar outra entrada na sidebar. O período e a Loja DEVEM (MUST) afetar os painéis aos quais se aplicam; Totem aparece apenas na aba de disponibilidade e Categoria apenas na aba de chamados/SLA. A interface DEVE (MUST) identificar esses escopos para não sugerir que um filtro afeta painéis incompatíveis.

#### Scenario: Loja histórica após transferência
- **WHEN** um Totem é transferido após a abertura do chamado
- **THEN** o filtro por Loja usa o vínculo comprovado no `criado_em`, sem substituí-lo pela Loja atual

#### Scenario: Risco atual com período curto
- **WHEN** a Diretoria seleciona Hoje e há chamado antigo ainda em contagem de SLA
- **THEN** o chamado pode entrar no risco atual, com indicação de que esse painel é um retrato do instante da consulta

#### Scenario: Período ou filtro inválido
- **WHEN** o período é invertido, futuro ou Loja/Categoria informada é inválida
- **THEN** o Xano rejeita a entrada sem retornar agregados

#### Scenario: Filtros específicos na página compartilhada
- **WHEN** a Diretoria seleciona Totem e Categoria na mesma página
- **THEN** Totem recorta somente disponibilidade/MTTD/MTTR, Categoria recorta somente volumetria/SLA, e os escopos ficam visíveis

#### Scenario: Troca entre as abas executivas
- **WHEN** a Diretoria alterna entre Disponibilidade e Chamados/SLA
- **THEN** vê apenas os painéis e filtros próprios da aba selecionada, preservando o período e a Loja escolhidos

### Requirement: Volumetria agrupa chamados abertos no período pelo status atual
O Xano DEVE (MUST) contar uma vez cada chamado com `criado_em` no período, agrupando pelo status persistido no instante da consulta. O resultado DEVE (MUST) informar o total e a contagem de status ausente ou não canônico separadamente, sem inferir status ou reescrever dados.

#### Scenario: Chamado muda de status após abrir
- **WHEN** chamado aberto no período passa de `Novo` para `Em Atendimento` antes da consulta
- **THEN** ele aparece uma vez em `Em Atendimento`, não em `Novo`

#### Scenario: Chamado anterior ao período
- **WHEN** chamado foi aberto antes de `t0`, embora permaneça em atendimento
- **THEN** não participa da volumetria desse período

#### Scenario: Status sem classificação válida
- **WHEN** chamado aberto no período tem status ausente ou fora da lista canônica
- **THEN** ele entra na contagem separada de não classificados, sem ser imputado a um status válido

### Requirement: Conformidade de SLA usa entradas no estado de parada vigente
A conformidade DEVE (MUST) seguir `indicadores-operacionais` e `sla-encerramento-chamados`: contar os chamados elegíveis que entram em `Resolvido` ou `Encerrado` no período e comparar seu consumo calculado ao SLA aplicado. `Cancelado` com entrada nesse status no período e não calculáveis entre os candidatos à parada DEVEM (MUST) ficar fora do denominador e em contagens separadas. Sem elegíveis, o percentual DEVE (MUST) ser indisponível.

#### Scenario: Conjunto conhecido
- **WHEN** oito de dez chamados elegíveis no período cumprem o SLA e há dois Cancelados
- **THEN** a conformidade é 80%, com dez elegíveis e dois Cancelados informados separadamente

#### Scenario: Rejeição seguida de nova resolução
- **WHEN** um chamado sai de `Resolvido` por rejeição e volta a `Resolvido` no período
- **THEN** seu consumo preserva o saldo anterior sem contar o tempo pausado, e o chamado é avaliado no estado de parada vigente sem duplicação

#### Scenario: Nenhum chamado elegível
- **WHEN** não há chamados elegíveis no período
- **THEN** a conformidade é indisponível e o denominador é mostrado como zero, sem percentual zero presumido

#### Scenario: Cancelamento no período
- **WHEN** um chamado entra em `Cancelado` no período selecionado
- **THEN** ele é contado separadamente, sem entrar no numerador ou denominador da conformidade

### Requirement: Termômetro de risco representa chamados em contagem no instante da consulta
O risco atual DEVE (MUST) considerar todos os chamados cujo status vigente consome SLA, mesmo que tenham sido abertos antes do período selecionado. O Xano DEVE (MUST) classificar cada consumo calculável nas faixas consolidadas normal, risco, crítico e violado, e contar separadamente os não calculáveis. Chamados `Resolvido`, `Encerrado` e `Cancelado` NÃO DEVEM (MUST NOT) entrar nas faixas de risco atual.

#### Scenario: Chamado antigo em risco
- **WHEN** chamado aberto antes do período está em `Em Atendimento` no instante da consulta com 95% do SLA consumido
- **THEN** ele entra uma vez na faixa crítico do risco atual, mesmo com período Hoje selecionado

#### Scenario: Chamado pausado ou terminal
- **WHEN** chamado está em `Resolvido`, `Encerrado` ou `Cancelado`
- **THEN** não entra nas faixas do risco atual

#### Scenario: Consumo não calculável
- **WHEN** a linha do tempo de um chamado em contagem é inconsistente
- **THEN** ele aparece na contagem de não calculáveis, sem faixa de risco presumida

### Requirement: Página distingue período, risco atual e estados de dados
O Reflex DEVE (MUST) apresentar volumetria, conformidade e risco em painéis distintos na página de Indicadores da Diretoria, com período e filtros efetivos, instante do retrato de risco, unidades e contagens devolvidas pelo Xano. Carregamento, erro e ausência de dados DEVEM (MUST) ser distinguíveis. O frontend NÃO DEVE (MUST NOT) calcular indicadores a partir de chamados brutos.

#### Scenario: Resposta válida
- **WHEN** o Xano retorna agregados de um período e retrato de risco
- **THEN** a página mostra a distribuição por status, a conformidade do período e as faixas do risco atual com seus recortes explícitos

#### Scenario: Falha após troca de filtro
- **WHEN** a consulta falha depois que a Diretoria altera o recorte
- **THEN** a página mostra erro e não apresenta valores do recorte anterior como se fossem atuais
