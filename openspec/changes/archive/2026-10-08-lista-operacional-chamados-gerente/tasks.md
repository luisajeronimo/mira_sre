# Tasks

## 1. Inventário e contratos da lista

- [x] 1.1 Inventariar a função, endpoint, DTO, cliente, State, página e testes atuais de `GET /gerente/chamados`, verificando que o escopo por Loja existente permanece a única fonte de autoridade.
- [x] 1.2 Validar com Xano Developer MCP/parser a estratégia de whitelist, texto case-insensitive e sort server-side direto no plano Free; interromper antes de schema adicional se a estratégia não for suportada.
- [x] 1.3 Inventariar read-only os registros existentes com `criado_em` ou `ultima_atualizacao_em` ausente e registrar somente contagem e IDs, sem backfill ou mutação.

## 2. Consulta operacional no Xano

- [x] 2.1 Evoluir a função e o endpoint existentes para aceitar somente número exato, status canônico, Totem autorizado, início/fim de abertura, campo de ordenação e direção whitelistados; cobrir em testes entrada inválida, status inválido e Totem de outra Loja.
- [x] 2.2 Implementar composição no Xano de escopo da Loja, filtros e `total` filtrado com resposta `{items, total}`, cobrindo filtros isolados, combinados, lista vazia e total coerente.
- [x] 2.3 Implementar a ordenação default `criado_em DESC, id DESC` e ramos autorizados para todas as colunas; cobrir ASC/DESC, texto case-insensitive para título/status/prioridade/Totem/Categoria, número numérico, datas cronológicas e desempate determinístico.
- [x] 2.4 Implementar período inclusivo de abertura por intervalo temporal seguro; cobrir limites de datas, início posterior ao fim, ASC/DESC, default e combinação de filtro com ordenação.
- [x] 2.5 Ampliar o DTO de lista com descrição e última atualização sem expor campos internos, segredos ou Loja sob controle do cliente; executar testes XanoScript de contrato e autorização.
- [x] 2.6 Simplificar todos os ramos temporais para `db.query` direta, removendo partições e merges exclusivos de null, sem alterar filtros, prioridade, autorização ou ordenação server-side.
- [x] 2.7 Verificar criação manual e incidente automático para garantir um único instante funcional reutilizado em `criado_em` e `ultima_atualizacao_em`.

## 3. Cliente e State Reflex

- [x] 3.1 Evoluir DTOs e cliente Service Desk para os contratos que representam chamado válido, com `criado_em` e `ultima_atualizacao_em` obrigatórios; cobrir parsing estrito de `items`, `total`, timestamps obrigatórios e respostas incompatíveis.
- [x] 3.2 Implementar no `ChamadosGerenteState` filtros em edição e aplicados, ordenação, items, total, loading e erro sanitizado; cobrir aplicar, limpar sem trocar ordenação, estados vazios, falhas 401/403/404/422/5xx e preservação de sessão confirmada diante de falha de consulta ou concorrência.
- [x] 3.3 Implementar a derivação local da ocorrência de 80 caracteres e contadores `total`/exibidos; cobrir descrição nula, exatamente 80 caracteres, truncamento com reticência, timestamps obrigatórios e ausência de fallback para `created_at`.

## 4. Lista operacional do Gerente

- [x] 4.1 Substituir os cards da lista por tabela acessível com as oito colunas aprovadas, ação Criar chamado, navegação existente ao detalhe e estados de loading/vazio/erro, verificando aderência a `DESIGN.md` nos componentes tocados.
- [x] 4.2 Adicionar controles de filtro, indicação visual dos filtros aplicados, aplicar/limpar e ordenação ASC/DESC por coluna, verificando que a UI apenas solicita a consulta e não ordena localmente.
- [x] 4.3 Exibir total filtrado e quantidade atual de itens e testar tabela, cabeçalhos, badges, timestamps funcionais e responsividade básica sem incluir paginação.

## 5. Abertura manual refinada

- [x] 5.1 Implementar Limpar como descarte local dos campos editáveis sem POST e cobrir que o formulário permanece na página.
- [x] 5.2 Implementar Descartar como abandono local seguido de retorno à lista e Voltar como navegação sem mutação; cobrir que nenhuma das ações chama criação, cancelamento ou exclusão.
- [x] 5.3 Preservar Salvar e autoridade backend de Loja, Totem, Categoria, prioridade, solicitante, origem, status e SLA; cobrir regressões do payload funcional atual.
- [x] 5.4 Implementar confirmação de sucesso observável antes/durante a navegação ao detalhe, sem endpoint adicional, e cobrir que a mensagem não some antes de ser percebida.

## 6. Validação integrada e publicação controlada

- [x] 6.1 Executar testes locais completos, incluindo contratos Xano, cliente, State, tabela, abertura e regressões de autorização; registrar a quantidade e interromper diante de falha fora do escopo.
- [x] 6.2 Executar `PYTHONPATH=. .venv/bin/reflex compile --dry`, `openspec validate lista-operacional-chamados-gerente --strict`, `openspec validate --all --strict` e `git diff --check`.
- [x] 6.3 Validar todos os XanoScripts alterados via MCP/parser e confirmar compatibilidade com plano Free, ausência de schema não aprovado e de recursos pagos.
- [x] 6.4 Executar `xano workspace push --dry-run`, revisar que o preview contém somente a evolução de `GET /gerente/chamados` e recursos estritamente relacionados; parar diante de alteração inesperada.
- [x] 6.5 Após autorização humana aplicável, publicar somente recursos aprovados sem `--records`, `--delete`, `--env` ou `--sync`, e confirmar `No changes to push` no dry-run posterior.
- [x] 6.6 Validar tecnicamente com sessão de Gerente e fixtures seguras: backend remoto, tabela SSR, filtros, ordenação, contadores, abertura com Limpar/Descartar/Voltar e regressões de sessão; não criar ou alterar dados além do explicitamente autorizado para a validação.
  - Evidência runtime: sessão de Gerente renderizou a tabela com os quatro chamados autorizados (`#34`, `#33`, `#32`, `#31`), oito colunas, contadores coerentes, título/ocorrência, navegação ao detalhe completo e comentários públicos; Limpar, Descartar e Voltar foram exercitados sem criação de registro.
  - Evidência runtime remota: `listar_chamados_gerente` retornou a lista completa da Loja 1, incluindo `#34`, e confirmou filtros, período inclusivo, isolamento, entradas numéricas inválidas e todas as ordenações disponíveis com dados reais.
  - Correção de sessão: sort/filtros repetidos reutilizam a sessão confirmada; falhas de consulta, timeout e contrato não limpam identidade, enquanto 401 real continua redirecionando ao login. Concorrência durante carregamento é ignorada sem sobrescrever a lista.
  - Correção de ordenação: campos textuais usam projeção Xano `to_lower` server-side; prioridade não usa mais ranking semântico ou merge; número e datas mantêm comparação numérica/cronológica e default `criado_em DESC, id DESC`.
  - `VALIDADO_AUTOMATIZADO_SEM_FIXTURE_RUNTIME`: cenários que exigem diversidade adicional (todos os status/categorias, descrição com mais de 80 caracteres, criação/feedback sem criar record) permanecem cobertos pela suíte automatizada.
  - `REMOTE_RUNTIME_BLOCKED_BY_HARNESS`: o navegador conectado exibiu aviso de conexão do canal de eventos; os cliques dinâmicos de consulta não foram declarados como runtime de UI. A aceitação visual/manual final será realizada pela responsável após o Archive, conforme decisão humana desta rodada. Nenhum dado foi alterado.

## 7. Revisão e encerramento

- [x] 7.1 Revisar read-only a correção de sessão, ordenação case-insensitive server-side, escopo por Loja, backend, segurança, semântica temporal, ausência de paginação e regressões da abertura; a revisão técnica independente da Parte 1 foi aprovada e a Parte 2 foi validada por parser, runtime diagnóstico e suíte estrutural.
- [x] 7.2 Reconciliar tasks somente com evidência real, executar validações finais e preparar Archive apenas após autorização humana explícita e revisão final; Archive executado e validações pós-Archive aprovadas.
