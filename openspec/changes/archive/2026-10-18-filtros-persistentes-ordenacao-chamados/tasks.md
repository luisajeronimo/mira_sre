# Tasks

## 1. Contratos e persistência Xano

- [x] 1.1 Criar a estrutura de preferência por usuário autenticado e escopo,
  com filtros canônicos e ordenação, sem token ou seleção de escopo.
- [x] 1.2 Implementar leitura e save autorizado das preferências e validar
  usuário, perfil, escopo, filtros, Status, Prioridade e ordenação.
- [x] 1.3 Estender `GET /tecnico/chamados` e sua função para ordenação
  whitelistada, estável e server-side.

## 2. Reflex e cliente

- [x] 2.1 Estender o cliente tipado e o State técnico para carregar, aplicar,
  limpar e salvar preferências por escopo: consultar a lista candidata antes do
  save e confirmar State/lista somente após ambas, com rollback confirmado.
- [x] 2.2 Adicionar Prioridade ao filtro técnico e controles de ordenação nas
  colunas autorizadas, incluindo Abertura e Última atualização, sem alterar a
  jornada do Gerente.
- [x] 2.3 Manter login em `Todos`, preservar filtros independentes por escopo
  e não persistir a seleção de `Atribuídos a mim`.

## 3. Validação

- [x] 3.1 Cobrir perfis, escopos, Status case-insensitive/canônico, filtros e
  ordenação combinados, desempate, rollback e last-valid-write-wins.
- [x] 3.2 Cobrir 401; 403 de perfil/escopo enumerado proibido; 422 de literal
  ou combinação de escopo inválida; e indisponibilidade de consulta ou
  persistência sem vazamento entre usuários.
- [x] 3.3 Executar testes relevantes e completos, compile Reflex, validação
  XanoScript/MCP, OpenSpec strict e `git diff --check`.

## 4. Ajuste autorizado: responsável na fila global

- [x] 4.1 Incluir filtro persistente por Técnico/`Não atribuído` e ordenação
  server-side por nome do responsável, com nulos após nomes e desempate por ID.
- [x] 4.2 Remover somente a coluna visual `Atribuído em` da fila global e
  preservar detalhes, APIs e histórico.
- [x] 4.3 Cobrir filtro, ordenação, persistência por escopo e remoção visual;
  validar os recursos Xano alterados e os testes focados.

## Evidências de fechamento — 18/10/2026

- Validação humana autorizada: `GET /tecnico/chamados` respondeu HTTP 200, com
  filtros e ordenação ASC/DESC corretos no Xano e no Reflex.
- Suíte Python: `383 passed`; compilação Reflex em modo dry-run concluída;
  OpenSpec strict e `git diff --check` válidos.
- MCP XanoScript validou os sete artefatos Xano alterados, sem avisos; o
  dry-run pós-publicação retornou `No changes to push`.
- Revisão independente do MIRA Reviewer: `aprovado`.
