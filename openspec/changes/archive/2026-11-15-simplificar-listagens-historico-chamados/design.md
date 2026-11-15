# Design — listagens e detalhe dos chamados

## Context

Os filtros de chamados mantêm opções textuais com ID e nome, usadas também na restauração de preferências. Os indicadores já separam `value` e `label`, mas acrescentam o ID ao rótulo dos Totens. A timeline operacional agrupa comentário e alteração pelo vínculo existente, porém repete a autoria e desenha bordas por diferença. Ver motivação e limites em `proposal.md`.

## Goals / Non-Goals

Preservar os componentes, tokens e identidade de `DESIGN.md`, com Impeccable no modo Operate. Não alterar contratos Xano, dados, regras de visibilidade, Save, acesso por perfil, números dos chamados ou IDs usados internamente. README e infraestrutura permanecem fora do escopo.

## Decisions

### Rótulo não é valor

Acrescentar uma opção de apresentação ao dropdown compartilhado para ocultar o prefixo de ID somente nos filtros indicados. Os eventos e seleções continuam usando o valor integral existente. Isso evita migração de preferências, colisão entre nomes repetidos e refatoração de estado sem necessidade. Nos indicadores, alterar apenas `label`, preservando `value`; nomes que contêm travessões devem permanecer completos.

### Composição compacta

Mover o seletor de visibilidade para o cabeçalho do comentário, com largura de conteúdo e rótulo acessível. Preservar o caso Público obrigatório. Não mudar o tamanho ou comportamento da caixa de texto para resolver a largura excessiva do seletor.

### Histórico com menos contornos

Manter um card compacto por entrada operacional e retirar as bordas dos campos internos. A grade de diferenças conserva duas colunas ajustadas ao conteúdo, os valores anterior/resultante e a ordem dos fatos, com 8 px entre linhas e entre os blocos do registro. Conforme revisão do usuário, o badge de Público/Interno fica abaixo da data no cabeçalho à direita, também para comentários agrupados. Sua classificação continua sendo a do comentário; o evento não recebe classificação. Comentário correlacionado usa texto e espaçamento, sem nova caixa. Histórico público do Gerente pode usar linhas sem cards aninhados, preservando seu escopo de leitura.

### Autoria por identidade

Decidir se a autoria complementar é necessária usando os IDs dos autores já presentes nos DTOs, sem expô-los. Não usar apenas igualdade de nomes, pois pessoas distintas podem ter o mesmo nome. A representação de view pode guardar uma flag de exibição; não há novo campo de domínio ou persistência. Datas iguais na apresentação também não precisam ser repetidas dentro do agrupamento.

## Risks / Trade-offs

- Nomes repetidos deixam de ser diferenciados pelo ID visível: preservar opções e valores independentes; não inventar novos atributos cadastrais.
- Mudança no dropdown afetar outros campos: apresentação opt-in, aplicada somente a Técnico, Totem e Loja.
- Remover informação de autoria: testar mesma identidade, identidades diferentes e nomes iguais com IDs diferentes.
- Dificuldade de inspeção autenticada: usar componentes reais em prévia isolada, com dados fictícios e rede externa bloqueada; distinguir essa validação do teste humano do dev normal.

## Validação e entrega

Testes locais dos contratos de seleção e da timeline, `make check`, `git diff --check` e OpenSpec strict. Inspecionar a prévia em larguras desktop de 1280 e 1440 px, conteúdo longo, menu de visibilidade e teclado. Disponibilizar o Reflex normal em dev para teste humano e parar antes de Archive, commit ou publicação.
