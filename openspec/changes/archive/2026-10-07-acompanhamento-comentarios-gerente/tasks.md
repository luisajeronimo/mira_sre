# Tasks

## 1. Preparação e inventário de mutações

- [x] 1.1 Inventariar os produtores e mutações funcionais atuais de `chamados` — criação manual, criação automática e assunção — e verificar por busca/XanoScript que não existe rota funcional de mudança de status a adaptar nesta change.
- [x] 1.2 Registrar no material de implementação que uma futura mutação funcional de status deve atualizar `ultima_atualizacao_em` atomicamente, sem criar nesta change endpoint, PATCH genérico ou tratativa; verificar que o diff não introduz tais operações.

## 2. Modelo temporal e produtores existentes

- [x] 2.1 Adicionar `chamados.ultima_atualizacao_em` como timestamp opcional, preservar nulos legados e validar schema/XanoScript pelo parser/MCP sem backfill ou uso de `created_at`.
- [x] 2.2 Evoluir a criação manual para capturar um único instante do backend para `criado_em` e `ultima_atualizacao_em`, retornar o campo no DTO e cobrir criação válida, autoridade de campos e legado sem inferência em testes.
- [x] 2.3 Evoluir a criação automática de heartbeat para inicializar `ultima_atualizacao_em` igual a `criado_em` dentro da transação existente, sem mudar heartbeat, deduplicação, prioridade ou autoria; verificar testes de regressão do heartbeat.
- [x] 2.4 Evoluir a assunção técnica para atualizar `ultima_atualizacao_em` somente quando a atribuição for efetivada, mantendo-a inalterada na repetição idempotente e no conflito; cobrir os três cenários em testes XanoScript/harness.
- [x] 2.5 Verificar que leitura, operações genéricas negadas e quaisquer registros internos legados não alteram `ultima_atualizacao_em`; cobrir ausência de escrita e preservação de nulo em testes aplicáveis.

## 3. Comentários públicos seguros no Xano

- [x] 3.1 Evoluir `interacoes_chamado` com visibilidade opcional e valores canônicos `publica` e `interna`, sem default público nem classificação de registros existentes; validar parser/MCP e teste de fail closed para nulo.
- [x] 3.2 Implementar função reutilizável de localização/autorização do chamado pela cadeia chamado → Totem → Loja para comentário de Gerente; cobrir sessão, perfil, Loja ausente, chamado inexistente e outra Loja.
- [x] 3.3 Implementar consulta funcional específica de comentários públicos por chamado, com DTO fechado de `id`, `conteudo`, `criado_em` e `autor.nome` opcional, sem ID/e-mail/perfil/Loja ou atributos internos do autor, filtragem explícita de visibilidade e ordenação DESC; cobrir público, interno, legado sem visibilidade e autor ausente/incompatível.
- [x] 3.4 Implementar criação funcional específica de comentário aceitando somente conteúdo, derivando autor, data e visibilidade pública no Xano e atualizando `ultima_atualizacao_em` na mesma unidade de escrita; cobrir whitespace, campos controlados pelo cliente e ausência de escrita parcial.
- [x] 3.5 Bloquear no backend a criação em `Encerrado` e `Cancelado`, mantendo a leitura pública permitida; cobrir ambos os estados e estado não terminal em testes XanoScript.
- [x] 3.6 Criar os endpoints `MIRA Service Desk` de leitura e criação de comentários com autenticação `usuarios`, autorização exclusiva de Gerente e erros 401/403/404/422 sanitizados; verificar que CRUD genérico não foi reaberto.

## 4. Cliente e detalhe Reflex do Gerente

- [x] 4.1 Adicionar DTOs e operações tipadas do cliente Service Desk para comentários públicos, mantendo validação estrita do autor público (`null` ou somente nome) e sem armazenar segredo; cobrir parse de autor/data, coleção ordenada, autor ausente e contrato inválido.
- [x] 4.2 Completar o State e a página de detalhe para apresentar Totem, Categoria, solicitante, Técnico ou ausência de atribuição, SLA, origem, abertura, `ultima_atualizacao_em` e autoria do Bot já consolidados; apresentar `Não informado` para última atualização legada nula e cobrir os detalhes manual, automático e legado.
- [x] 4.3 Implementar carregamento, envio, erro sanitizado e descarte exclusivamente local do rascunho de comentário; verificar que o payload contém somente conteúdo e que 401/403/404/422 preservam os contratos de sessão atuais.
- [x] 4.4 Ocultar somente a ação de envio para `Encerrado` e `Cancelado`, mantendo comentários públicos visíveis; verificar que a proteção visual não substitui a rejeição do backend.

## 5. Validação integrada e publicação controlada

- [x] 5.1 Executar os testes locais relevantes e a suíte completa com `.venv/bin/python -m pytest -q`, verificando cobertura de timestamps, comentários, autorização, terminal, dados legados e regressões de criação, heartbeat e assunção.
- [x] 5.2 Executar `PYTHONPATH=. .venv/bin/reflex compile --dry`, `openspec validate acompanhamento-comentarios-gerente --strict` e `git diff --check`; corrigir somente falhas dentro do escopo aprovado.
- [x] 5.3 Validar todos os XanoScripts alterados via MCP/parser e confirmar compatibilidade com plano Free, ausência de segredo em logs e inexistência de escrita de comentário/timestamp antes das validações obrigatórias.
- [x] 5.4 Executar `xano workspace push --dry-run`, revisar que o preview contém somente schema, funções e endpoints desta change e interromper diante de recurso inesperado.
- [x] 5.5 Após autorização de publicação aplicável, executar push estrutural sem `--records`, `--delete`, `--env` ou `--sync`, repetir o dry-run até `No changes to push` e registrar somente metadados não sensíveis.
- [x] 5.6 Validar runtime com chamado e Gerente autorizados: comentário público aparece em DESC, autoria vem da sessão, terminal bloqueia escrita, outra Loja é negada e dados internos/sem visibilidade não aparecem; não consultar ou registrar segredos.

## 6. Revisão e encerramento da change

- [x] 6.1 Solicitar revisão independente do mira-reviewer sobre escopo, visibilidade fail closed, autoria, timestamps, terminais, legados, Free plan, testes e ausência de requisitos da Change 2.
- [x] 6.2 Reconciliar tasks somente com evidência real, executar validações finais exigidas pela change e preparar Archive apenas após aprovação humana explícita e revisão final.

## Evidências de runtime pós-publicação

- **VALIDADO_RUNTIME:** sessão real de Gerente acessou o controle da própria Loja, com detalhe completo; comentário público autenticado foi publicado, persistiu após recarga, ficou no topo em `criado_em DESC`, exibiu apenas autoria sanitizada e alterou `ultima_atualizacao_em`; descarte limpou somente o rascunho. O chamado de outra Loja foi negado. Nas fixtures controladas, as interações identificadas como interna e sem visibilidade não foram renderizadas na consulta pública; o chamado terminal Encerrado permitiu leitura do comentário público e não ofereceu campo, botão ou ação acionável para postagem.
- **VALIDADO_AUTOMATIZADO:** whitespace, DTO público fechado, autoria derivada da sessão, visibilidade fail-closed para interna/nula/incompatível, rejeição de POST em Encerrado e Cancelado sem escrita ou alteração de timestamp, timestamps de criação/assunção e regressões de heartbeat possuem cobertura local; unidades remotas de abertura e detalhe normal/legado/automático passaram após a publicação.
- **RUNTIME_NAO_EXECUTADO_SEM_FIXTURE_SEGURA:** incidente automático não foi provocado no ambiente.
- **REMOTE_RUNTIME_BLOCKED_BY_HARNESS:** a unidade remota preexistente de assunção retornou `Access Denied` antes de alcançar a regra; a cobertura local de assunção efetiva, idempotência e conflito permanece válida, sem declarar runtime desse fluxo.
- **FIXTURES TEMPORÁRIAS REMOVIDAS MANUALMENTE PELA RESPONSÁVEL:** comentário público `#4`, interação interna `#5`, interação sem visibilidade `#6` e chamado terminal `#35` foram excluídos após a coleta de evidências. Esses registros não fazem parte do produto e não foram recriados.
