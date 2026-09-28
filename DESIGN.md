# Design visual do MIRA

## Propósito e hierarquia

Este documento é a autoridade visual global do MIRA. A ordem de precedência é:

1. requisitos funcionais autorizados;
2. este `DESIGN.md`;
3. o PNG relacionado em `docs/design/references/`;
4. componentes Reflex existentes.

Um requisito funcional sempre vence qualquer contradição visual. Na ausência de
PNG relacionado, derive a interface deste documento e das referências já
existentes. Revise e reutilize componentes Reflex antes de criar variações.

Os PNGs são referências visuais sanitizadas, não funcionais e não
pixel-perfect. Textos, nomes, números, métricas, prioridades, status, SLAs,
perfis, entidades, exemplos, ações e comportamentos mostrados neles são apenas
ilustrativos e nunca definem requisitos funcionais. Eles servem somente para
composição, hierarquia, densidade, identidade, navegação, aparência de
componentes, espaçamento e linguagem visual.

## Princípios

- Clareza operacional: informação e ação relevantes devem ser reconhecíveis sem
  depender da cor isoladamente.
- Simplicidade corporativa: superfícies claras, conteúdo organizado e pouca
  ornamentação.
- Consistência: padrões compartilhados para interação, estados e hierarquia.
- Densidade responsável: telas operacionais podem ser compactas sem reduzir
  legibilidade, área de toque ou foco.

## Identidade, cor e tipografia

A identidade é clara, clean, moderna, minimalista e profissional, com rose/rosa
como acento de marca. Use rose para ação primária, seleção e foco; use neutros
claros em canvas e superfícies; use texto em tom escuro de alto contraste; e
reserve cores semânticas para estados de sucesso, atenção, erro e informação.
Não associe uma cor a regra de negócio: rótulo, ícone e contexto devem manter o
significado quando a cor não estiver disponível.

`Plus Jakarta Sans` é a família principal para títulos, navegação, rótulos e
texto de interface. Use `JetBrains Mono` apenas quando útil para dados técnicos,
identificadores, timestamps, valores numéricos ou trechos que se beneficiem de
alinhamento monoespaçado. Mantenha uma escala tipográfica curta, com títulos
fortes e texto de leitura confortável.

## Layout, forma e elevação

Use grid de 12 colunas em desktop, 8 em tablet e 4 em mobile, com conteúdo
fluido e margens proporcionais. Adote escala de espaçamento baseada em 4 px,
priorizando 8, 12, 16, 24 e 32 px. Agrupe elementos por proximidade e mantenha
respiro entre seções.

Controles usam cantos suavemente arredondados; cards, painéis e modais podem
usar raio um pouco maior. Bordas finas e sombras discretas devem separar planos.
Elevação é funcional: base para conteúdo normal, baixa para menus e popovers,
maior apenas para modais e superfícies transitórias. Evite sombras pesadas,
gradientes decorativos e efeitos chamativos.

## Estrutura e navegação

A sidebar organiza áreas principais com item ativo claro, ícone opcional e
colapso previsível em telas menores. A topbar concentra contexto de página,
ações globais e elementos de sessão quando existentes. Não deduza itens de
navegação, perfis ou permissões dos PNGs.

Pesquisa e filtros ficam próximos ao conjunto de dados que afetam, com estado
ativo visível, rótulo compreensível e ação para limpar quando o contrato
funcional a prever. Use navegação por teclado, ordem de foco lógica e feedback
para carregamento ou atualização.

## Componentes

- **Formulários:** rótulo persistente, ajuda ou erro próximo ao campo,
  preenchimento confortável, borda neutra e foco rose com contraste suficiente.
- **Botões:** primário rose para a ação principal da área; secundário contornado
  ou neutro; terciário/ghost para ações auxiliares. Estados disabled, hover,
  focus e loading devem ser distinguíveis.
- **Cards:** superfície clara, borda sutil, título e conteúdo organizados; não
  os use para simular uma ação que não exista no contrato.
- **Tabelas:** cabeçalho legível, alinhamento coerente, densidade adequada,
  hover/foco discretos e alternativa responsiva para telas estreitas.
- **Badges:** pequenos e semânticos, com texto além da cor; não introduzem
  status, prioridade ou SLA novos.
- **Dashboards:** destaque poucas métricas por vez, mantenha hierarquia visual
  e use gráficos apenas quando a leitura comparativa for autorizada.

## Estados e acessibilidade

Projete estados de vazio, carregamento, sucesso, erro, indisponibilidade,
hover, foco, seleção e desabilitado. Os textos e ações desses estados dependem
do requisito funcional aplicável; a referência define apenas sua apresentação.

Garanta contraste adequado, foco sempre visível, navegação completa por teclado,
alvos interativos confortáveis, semântica acessível, mensagens de erro claras e
layout que suporte zoom e redução de movimento. Não use cor, posição ou ícone
como único portador de significado.

## Responsividade, reutilização e evolução

Em telas estreitas, preserve a tarefa principal, empilhe grupos quando necessário
e torne tabelas e filtros utilizáveis sem depender de largura fixa. Reutilize
tokens, componentes e composições existentes antes de criar novos padrões.

Evolua este guia por mudanças focadas e revisáveis. Uma referência PNG pode
inspirar uma composição, mas não substitui requisitos autorizados nem justifica
comportamento, entidade, ação ou permissão nova.
