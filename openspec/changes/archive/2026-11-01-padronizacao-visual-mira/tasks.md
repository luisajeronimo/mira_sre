# Tasks

## 1. Base visual e casca desktop

- [x] 1.1 Definir tokens de apresentação e tema Reflex para canvas, tipografia, superfícies, bordas, foco e acento rose/ruby; verificar que não há dependência nova nem alteração de State.
- [x] 1.2 Aplicar sidebar e topbar desktop compartilhadas com logo oficial, identidade, logout e navegação existente; verificar a matriz, o item ativo, foco e ausência de drawer pelos testes de sidebar.

## 2. Página inicial global

- [x] 2.1 Padronizar o cabeçalho compartilhado da jornada global; verificar que Técnico, Diretoria e Administrador continuam renderizando a mesma fila em `/inicio`.
- [x] 2.2 Aplicar superfícies, espaçamento e estados visuais aos controles, filtros, tabela, badges e botões já existentes da fila global; verificar por teste focado que filtros, ordenação, escopos e ações não mudaram.

## 3. Verificação do recorte

- [x] 3.1 Executar testes focados da navegação e fila global, `reflex compile --dry`, `openspec validate padronizacao-visual-mira --strict` e `git diff --check`; registrar a evidência nas tasks (85 testes passaram; compile, strict e diff-check passaram).
- [x] 3.2 Solicitar revisão independente do MIRA Reviewer sobre o escopo visual, regressões funcionais e validações; corrigir somente apontamentos dentro desta change (aprovado sem apontamentos).

## 4. Correção visual pós-validação humana

- [x] 4.1 Reorganizar a casca: topbar sem texto genérico, identificação única com cargo em maiúsculas e saída; verificar matriz e logout pelos testes de sidebar.
- [x] 4.2 Criar componentes visuais compartilhados para labels, pares de data, campos de informação e badges; verificar transformação somente de apresentação.
- [x] 4.3 Aplicar filtros rotulados, tabelas densas e cabeçalhos centralizados nas listas de Gerente e fila global, preservando handlers, persistências e indicadores ativos.
- [x] 4.4 Refatorar detalhes e comentários de Gerente e perfis globais em grids e cards compactos, preservando drawer, linha do tempo, postagem, ordem e visibilidade.
- [x] 4.5 Aplicar badges semânticos com status em maiúsculas às telas de chamados e monitoramento, sem alterar State ou serviços.

## 5. Verificação do refinamento

- [x] 5.1 Executar testes focados de sidebar, Gerente, fila global e monitoramento, `reflex compile --dry`, OpenSpec strict e `git diff --check` (132 testes passaram; demais gates aprovados).
- [x] 5.2 Solicitar nova revisão independente do MIRA Reviewer sobre a correção visual, preservação funcional e evidências (aprovado após conferir badges de status, filtros ativos e ausência de regressão funcional).

## 6. Refinamento com referência Figma

- [x] 6.1 Registrar a referência Figma no guia visual e na change, sem alterar requisitos funcionais existentes.
- [x] 6.2 Aplicar componentes compartilhados para grade alinhada de filtros, períodos `Abertura`/`Atualização`, ação de saída rose e cabeçalhos de tabela rose com contraste, preservando todos os handlers e contratos.
- [x] 6.3 Executar testes focados, compilação Reflex, OpenSpec strict, `git diff --check` e revisão independente do MIRA Reviewer (132 testes passaram; compile, strict e diff-check passaram; revisão aprovada).

## 7. Ajustes de acabamento de filtros e tabelas

- [x] 7.1 Corrigir recorte de superfícies com tabela, aumentar padding do painel de filtros e fixar ações no topo do painel compartilhado.
- [x] 7.2 Reforçar o peso tipográfico dos cabeçalhos rose, preservando contraste, ordenação, setas e acessibilidade.
- [x] 7.3 Validar testes focados, compilação Reflex, OpenSpec strict, `git diff --check` e revisão independente do MIRA Reviewer (132 testes passaram; compile, strict e diff-check passaram; revisão aprovada).

## 8. Seletor visual de intervalo

- [x] 8.1 Adicionar wrapper local com dependência npm fixada para calendário rose de intervalo, conectado somente aos campos de data existentes.
- [x] 8.2 Substituir os pares nativos `De`/`Até` das filas Gerente e global, preservando handlers de aplicar, limpar, persistência e consulta.
- [x] 8.3 Executar testes focados, compilação Reflex, OpenSpec strict, `git diff --check` e revisão independente do MIRA Reviewer (134 testes passaram; compile, strict e diff-check passaram; revisão aprovada).

## 9. Ajuste do seletor de período

- [x] 9.1 Suavizar o texto do gatilho e liberar o popover do calendário para extrapolar o painel de filtros, mantendo o recorte somente nas tabelas.
- [x] 9.2 Executar testes focados, compilação Reflex, OpenSpec strict e `git diff --check` (134 testes passaram; compile, strict e diff-check passaram).

## 10. Popover de calendário sem recorte

- [x] 10.1 Renderizar o calendário em portal no documento, posicionado junto ao gatilho e fora de contêineres com overflow.
- [x] 10.2 Executar testes focados, compilação Reflex, OpenSpec strict e `git diff --check` (134 testes passaram; compilação completa e dry, strict e diff-check passaram).

## 11. Persistência visual do intervalo

- [x] 11.1 Aplicar tokens rose ao popover em portal e manter o primeiro dia no estado local até a seleção do `Até`.
- [x] 11.2 Executar testes focados, compilação Reflex, OpenSpec strict e `git diff --check` (134 testes passaram; compile, strict e diff-check passaram).

## 12. Seleção de intervalo em duas etapas

- [x] 12.1 Manter o calendário aberto até o segundo clique e aplicar rose somente aos círculos dos dois dias selecionados.
- [x] 12.2 Executar testes focados, compilação Reflex, OpenSpec strict e `git diff --check` (134 testes passaram; compile, strict e diff-check passaram).

## 13. Tokens do DayPicker

- [x] 13.1 Aplicar tokens rose diretamente na raiz do DayPicker e manter o intervalo em rose claro, com extremidades circulares rose.
- [x] 13.2 Executar testes focados, compilação Reflex, OpenSpec strict e `git diff --check` (134 testes passaram; compile, strict e diff-check passaram).

## 14. Ajuste compacto da fila do Gerente

- [x] 14.1 Compactar somente os períodos de Abertura e Atualização, alinhar Criar chamado ao cabeçalho e ocultar o rótulo visual de ações, preservando filtros e eventos.
- [x] 14.2 Executar validação focada, `reflex compile --dry` e `git diff --check` (103 testes passaram; compile e diff-check passaram).

## 15. Consistência da fila global

- [x] 15.1 Aplicar os períodos compactos e ocultar o rótulo visual de ações na fila global reutilizada por Técnico, Diretoria e Administrador, sem inserir ação inexistente.
- [x] 15.2 Executar validação focada, `reflex compile --dry` e `git diff --check` (103 testes passaram; compile e diff-check passaram).

## 16. Compactação dos períodos

- [x] 16.1 Reduzir os controles de período e ajustar suas colunas para manter Abertura e Atualização lado a lado em cada fila.
- [x] 16.2 Executar validação focada, `reflex compile --dry` e `git diff --check` (103 testes passaram; compile e diff-check passaram).

## 17. Reversão do refinamento da tabela do Gerente

- [x] 17.1 Restabelecer a tabela do Gerente no padrão rose compartilhado pelos demais perfis, removendo exclusivamente a variante lavanda recém-testada.
- [x] 17.2 Executar testes focados, `reflex compile --dry` e `git diff --check` (103 testes passaram; compile e diff-check passaram).

## 18. Alinhamento das tabelas de chamados

- [x] 18.1 Distribuir colunas equivalentes nas filas de Gerente e global, reservando o espaço remanescente para título/chamado e centralizando as demais células nos dois eixos.
- [x] 18.2 Executar testes focados, `reflex compile --dry` e `git diff --check` (103 testes passaram; compile e diff-check passaram).

## 19. Acabamento de tabelas e detalhes

- [x] 19.1 Aplicar hover integral de cabeçalho, badges ajustados, faixa de detalhe, campos rose e comentários/histórico compactos em Gerente e jornada global, sem alterar eventos ou dados.
- [x] 19.2 Executar testes focados, `reflex compile --dry` e `git diff --check` (103 testes passaram; compile e diff-check passaram).

## 20. Correção visual pós-validação humana

- [x] 20.1 Estabilizar hover e largura das tabelas, remover overflow horizontal e reorganizar detalhes, comentário e histórico conforme a referência de Dados do Incidente.
- [x] 20.2 Executar testes focados, `reflex compile --dry`, `git diff --check` e revisão independente do MIRA Reviewer (104 testes passaram; compile e diff-check passaram; reviewer aprovado). Comparação runtime permanece bloqueada pelo WebSocket local e aguarda validação humana.

## 21. Estabilidade de hover e overflow da tabela

- [x] 21.1 Fixar a geometria do botão de ordenação no hover e desativar o overflow horizontal nativo das tabelas com layout fixo.
- [x] 21.2 Executar testes focados, `reflex compile --dry` e `git diff --check` (104 testes passaram; compile e diff-check passaram).

## 22. Uniformidade do detalhe entre perfis

- [x] 22.1 Compartilhar a faixa `Chamado #ID - título`, destacar a ação do Totem, exibir Origem em maiúsculas e manter descrição e comentário fora do painel de dados em Gerente e jornada global.
- [x] 22.2 Executar testes focados, `reflex compile --dry`, OpenSpec strict e `git diff --check` (104 testes passaram; compile, strict e diff-check passaram; Gerente conferido no navegador com o bundle atualizado).

## 23. Superfície da descrição

- [x] 23.1 Igualar o fundo da descrição à superfície branca do painel de dados em todos os perfis, mantendo-a como seção externa.
- [x] 23.2 Executar testes focados, `reflex compile --dry`, OpenSpec strict e `git diff --check` (104 testes passaram; compile, strict e diff-check passaram; superfície branca confirmada no navegador).

## 24. Simplificação da fila global

- [x] 24.1 Remover a coluna redundante `Ações` da fila global e redistribuir suas larguras, preservando o acesso ao detalhe pelo número do chamado.
- [x] 24.2 Executar testes focados, `reflex compile --dry`, OpenSpec strict e `git diff --check` (104 testes passaram; compile, strict e diff-check passaram; bundle local atualizado).

## 25. Prévia da descrição na fila global

- [x] 25.1 Exibir título e prévia compacta da descrição na mesma célula da fila global, igualando-a ao padrão do Gerente sem alterar dados ou navegação.
- [x] 25.2 Executar testes focados, `reflex compile --dry`, OpenSpec strict e `git diff --check` (106 testes passaram; compile, strict e diff-check passaram; validação visual da fila global permanece pendente de sessão Técnico, Diretoria ou Administrador).

## 26. Abertura manual conforme referência visual

- [x] 26.1 Registrar o frame específico e o delta visual da abertura do Gerente, preservando prioridades, ações e contratos existentes.
- [x] 26.2 Reorganizar o formulário de `/chamados/novo` em cabeçalho, superfície de dados, seleção horizontal de prioridade e faixa de ações, sem alterar State ou eventos.
- [x] 26.3 Executar testes focados, `reflex compile --dry`, OpenSpec strict, `git diff --check`, comparação visual e revisão independente do MIRA Reviewer (34 testes focados, compile, strict e diff-check passaram; quatro cards `263 × 60 px` sem overflow e seleção rose confirmados no preview; revisão aprovada. As quatro falhas parametrizadas de troca de sessão foram reproduzidas antes da troca e classificadas fora do escopo visual).

## 27. Login público conforme referência visual

- [x] 27.1 Registrar o frame `1:546`, a substituição do título pelo logotipo oficial e os limites funcionais do login.
- [x] 27.2 Reorganizar `app/pages/login.py` em painel desktop dividido, preservando formulário, eventos, mensagens, carregamento e redirecionamentos existentes.
- [x] 27.3 Executar testes focados, `reflex compile --dry`, OpenSpec strict, `git diff --check`, comparação visual e revisão independente do MIRA Reviewer (29 testes passaram; compile, strict e diff-check passaram; card de 1152 px com colunas 5/7, logo oficial de 112 px e ausência de overflow confirmados no navegador; revisão aprovada).

## 28. Simplificação visual do login pós-validação humana

- [x] 28.1 Remover os elementos decorativos `ACESSO SEGURO` e `MIRA • OPERAÇÃO INTEGRADA`, além de simplificar a instrução para `Faça login para acessar o MIRA.`, preservando o formulário e a autenticação.
- [x] 28.2 Executar teste focado, `reflex compile --dry`, OpenSpec strict, `git diff --check` e comparação visual no navegador (1 teste focado passou; compile, strict e diff-check passaram; instrução simplificada e ausência dos dois elementos confirmadas em `http://127.0.0.1:3001/login/`, sem recortes ou sobreposição).

## 29. Refinamento textual do login pós-validação humana

- [x] 29.1 Substituir a instrução por `Entre com suas credenciais.` e reduzir a ação normal do botão a `Entrar` em peso forte, preservando o estado de carregamento e o envio existentes.
- [x] 29.2 Executar teste focado, `reflex compile --dry`, OpenSpec strict, `git diff --check` e comparação visual no navegador (1 teste focado passou; compile, strict e diff-check passaram; `Entre com suas credenciais.` e o botão `Entrar` em peso forte foram confirmados em `http://127.0.0.1:3001/login/`).

## 30. Indicador visual da ação de login

- [x] 30.1 Recolocar a seta ao lado de `Entrar`, mantendo o texto em peso forte e preservando envio e carregamento existentes.
- [x] 30.2 Executar teste focado, `reflex compile --dry`, OpenSpec strict, `git diff --check` e comparação visual no navegador (1 teste focado passou; compile, strict e diff-check passaram; seta alinhada ao texto `Entrar` foi confirmada em `http://127.0.0.1:3001/login/`).
