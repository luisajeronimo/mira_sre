# Design

## Context

Ver `proposal.md` e os deltas desta change. A página `/indicadores/disponibilidade` já oferece à Diretoria período, Loja e Totem para os indicadores de Totens. `indicadores-operacionais` define conformidade e faixas de SLA; `sla-encerramento-chamados` define o consumo por linha do tempo e `service_desk/calcular_consumo_sla_chamado` o implementa no Xano. Chamados não armazenam Loja: o vínculo histórico do Totem no `criado_em` é a autoridade. A referência do Figma orienta a disposição dos painéis, mas seus números, metas e ações são ilustrativos.

## Goals / Non-Goals

**Goals:** consulta agregada reproduzível, separação clara entre métricas do período e retrato atual, autorização no Xano, ausência explícita de dados e verificação com conjunto conhecido de chamados.

**Non-Goals:** alterar a função de consumo individual sem defeito demonstrado, persistir agregados, reescrever histórico, criar agendamento, exportar dados ou adotar metas de SLA do Figma.

## Decisions

### D1. Contratos dedicados e recortes efetivos

Criar contrato autenticado de leitura para volumetria, conformidade e risco, e catálogo mínimo de Loja e Categoria se o catálogo existente não atender sem expor dados brutos. Exigir Diretoria antes das leituras. O contrato devolve período solicitado/efetivo, instante de referência do risco, filtros efetivos, contagens e valores nulos explícitos. Período e IDs são validados no Xano; o Reflex apenas apresenta o resultado. Reutilizar os atalhos “Últimos 30 dias”, “Hoje” e período personalizado da página, sem torná-los temporizador de atualização.

Na mesma página, Hoje já seleciona o dia civil completo com `t1` exclusivo no próximo 00h. Este contrato aceita a exceção por `visao=hoje` somente para esse intervalo do dia atual; captura um único instante de consulta, limita volumetria e conformidade ao que já ocorreu e usa o mesmo instante para o risco. Outros períodos futuros continuam inválidos.

### D2. Três bases diferentes, uma resposta coerente

Para volumetria, selecionar chamados por `criado_em ∈ [t0,t1)` e agrupar pelo status persistido no instante da consulta, contando uma vez por ID. Para conformidade, selecionar chamados cuja entrada no estado de parada vigente (`Resolvido` ou `Encerrado`) pertence ao período; usar a resolução vigente após eventual rejeição, contando o chamado uma vez. Cancelamentos cuja transição para `Cancelado` ocorre no período são contados à parte; não calculáveis são contados entre os candidatos à parada. Para risco, selecionar todos os chamados em estados que consomem SLA no instante da consulta, independentemente da abertura e do período. O mesmo instante de referência é usado em todo o retrato de risco. `Resolvido`, `Encerrado` e `Cancelado` não entram nas faixas atuais; dados não calculáveis e status não canônicos ficam em contagens próprias. Não combinar os denominadores dessas bases.

### D3. Cálculo e Loja histórica no Xano

Reutilizar `service_desk/calcular_consumo_sla_chamado` para o consumo individual, incluindo pausas em `Resolvido`, retomadas após rejeição e falha fechada para linha do tempo inconsistente. O Xano classifica as faixas conforme `indicadores-operacionais` e agrega quantidades; o Reflex não percorre chamados brutos nem recalcula percentual. Para filtro por Loja, resolver a Loja do Totem no `criado_em` do chamado; sem vínculo comprovado, o chamado permanece na visão global e não é imputado a Loja filtrada. Categoria usa a associação persistida do chamado. O recorte por Prioridade é removido do contrato desta capacidade conforme a decisão humana.

### D4. Composição na página existente

Acrescentar painéis de volumetria por status, conformidade do período e risco atual à mesma rota protegida da Diretoria, sem alterar a navegação. A página usa abas de Disponibilidade e Chamados/SLA logo após o breadcrumb; cada aba tem título, filtros, erros e painéis próprios. Período e Loja permanecem compartilhados onde aplicáveis; Totem aparece somente na aba de disponibilidade e Categoria somente na aba de chamados/SLA. A troca de aba preserva os filtros e apresenta resultados já consultados, sem criar outra rota ou entrada na sidebar. Cada painel identifica sua base temporal. A composição apresenta primeiro os números de volume e conformidade, depois a distribuição por status em rosca com legenda textual e o termômetro de risco em quatro faixas; os resumos e a distribuição continuam sendo uma única base de volumetria. O risco mostra o instante do retrato e as contagens não calculáveis; a conformidade mostra numerador, denominador, Cancelados e não calculáveis. Reutilizar superfícies claras, hierarquia de cartões e acentos discretos do `DESIGN.md` e da referência visual. Não usar a meta de 95%, as categorias visuais ou números da referência como regras do produto.

## Risks / Trade-offs

- [Risco atual exige percorrer chamados antigos ainda em contagem] → usar consultas e índices compatíveis com os filtros, medir volume/latência em dados reais e não devolver resultado parcial silencioso; se o plano Free não sustentar a carga, voltar à revisão antes de limitar o requisito.
- [Função de consumo individual pode gerar custo por chamado] → reutilizar a função sem duplicar regra, executar testes nativos com conjunto conhecido e medir tempo de resposta da agregação.
- [Histórico de status legado ou vínculo de Loja ausente] → manter não calculáveis e Loja não comprovada explícitos, sem fabricar transições ou atribuição retroativa.
- [Período do topo não restringe risco atual] → mostrar o instante do retrato e a legenda “Risco atual” junto do painel para não sugerir que a contagem segue a janela de abertura.

## Migration Plan

Implementar e testar contratos Xano em leitura, validar XanoScript com o Developer MCP e executar dry-run seletivo antes de qualquer publicação. Após autorização de publicação, verificar os contratos com conjunto conhecido e repetir o dry-run. Integrar cliente, State e painéis Reflex depois da resposta estável. Não há migração de dados; rollback de interface não altera histórico, e remoção remota de contratos exige revisão própria.
