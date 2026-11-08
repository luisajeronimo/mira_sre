# Evidência de validação do Apply — Sprint 5

Data: 2026-11-07. Alvo: workspace Xano 152692, branch `v1`, datasource `live`. O usuário autorizou a publicação e as correções da Sprint 5. As mutações de validação atingiram somente registros identificados por `E2E S5 c37f6cab` ou contas descartáveis criadas nesta rodada. A senha fornecida pelo usuário não foi gravada em arquivo, log ou evidência.

## Publicação

O primeiro push parcial publicou 34 documentos da change após validação sintática e `xano workspace push --dry-run -b v1`. Correções posteriores afetaram apenas contratos da Sprint 5. A última correção de compatibilidade com Lojas legadas publicou três funções e dois endpoints; antes dela, os cinco XanoScripts passaram no Xano Developer MCP e o dry-run mostrou exatamente esses cinco objetos. O dry-run imediatamente posterior retornou `No changes to push`. Não foram usados `--force`, `--records`, `--sync`, opções destrutivas ou push de Simulator/Fiscal.

## Verificações executadas

| Área | Resultado | Evidência e limite |
| --- | --- | --- |
| Python e Reflex | **Passou**: `make check`, 460 testes e compilação Reflex em produção | Testes locais usam mocks; a navegação real está descrita abaixo. |
| XanoScript | **Passou**: 130 arquivos válidos, 0 inválidos, 2 avisos | Validação de sintaxe pelo Xano Developer MCP. |
| OpenSpec e diff | **Passou**: `openspec validate administracao-mira --strict` e `git diff --check` | Verificação formal, não substitui teste de comportamento. |
| Xano Free | **Passou** para os fluxos sequenciais testados na `v1` | Tabela temporal, transações, consultas temporais, validações e contratos específicos funcionaram em dados de teste. |
| Sessão e autorização | **Passou** | Dez chamadas sem token retornaram 401. Gerente, Técnico e Diretoria receberam 403 nos GETs administrativos testados; Gerente também recebeu 403 em criação de Loja/Totem, exclusão de usuário e abertura administrativa. |
| Lojas | **Passou** | Criação inicia `Ativa`; listagem, detalhe, edição, inativação, reativação e exclusão de Loja livre passaram. Campo obrigatório ausente e exclusão com vínculo atual ou temporal retornaram 400. |
| Totens | **Passou** nos fluxos principais | Criação, consulta, edição, transferência entre Lojas Ativas e exclusão do Totem livre com seu único vínculo inicial passaram. Destino `Inativa`, Totem com fatos e Totem com transferência histórica foram bloqueados. Totem novo não recebeu `Online`/`Offline`. |
| Usuários | **Passou** nos fluxos principais | Criação existente reutilizada; e-mail único, perfis canônicos, senha temporária e primeiro acesso validados. Listagem/detalhe omitiram credenciais. Edição, mudança de perfil e transferência de Gerente passaram. Técnico atribuído, e-mail duplicado, Loja Inativa de destino, usuário com chamado e autoexclusão administrativa foram bloqueados. Uma conta Administrador de teste mudou para Diretoria enquanto outro Administrador permanecia. |
| Chamados e Loja Inativa | **Passou** | Gerente abriu chamado na Loja A Inativa; Administrador abriu chamado global para a Loja B. Gerente vinculado à Loja Inativa comentou no chamado existente; Gerente da outra Loja recebeu 403. Técnico assumiu chamado; sua mudança de perfil foi bloqueada. |
| Histórico temporal | **Passou** para chamados e telemetria | Após transferências do Totem 17, chamado 90 permaneceu na Loja 6 e chamado 91 na Loja 7. Listas, detalhes e filtros por Loja da fila global e dos Gerentes refletiram esses vínculos. Telemetrias 1566, 1567 e 1568 apareceram respectivamente nas Lojas 6, 7 e 6; a última foi ingerida com a Loja 6 Inativa. IDs e timestamps dos fatos foram preservados. |
| Reflex no navegador | **Passou** nos fluxos exercitados | Conta administrativa descartável fez login e primeiro acesso; fila técnica e abas de Lojas, Totens, Usuários e abertura manual carregaram. Uma Loja de teste foi criada pelo formulário e excluída após confirmação. A identidade da sessão permaneceu visível ao trocar de aba. |
| Compatibilidade legada | **Passou** para leitura e catálogo | Cinco Lojas existentes com status `Ativo` aparecem no catálogo ativo sem reescrita; novas edições aceitam apenas `Ativa`/`Inativa`. Usuário não Gerente legado com `lojas_id=0` é projetado como sem Loja. Estado de Totem vazio é apresentado como não informado, sem presumir disponibilidade. |

Um teste unitário novo da função `administracao/validar_criacao_usuario` com Loja legada `Ativo` passou na `v1`. A lista de opções administrativas retornou os IDs das cinco Lojas legadas.

## Correções encontradas durante os testes

- A primeira versão de `service_desk/abrir_chamado_manual` gravava referência de Totem/Categoria incorreta. O contrato foi corrigido e passou a conferir as referências persistidas. Os chamados de teste 88 e 89, criados durante essa falha, foram reparados **somente nesses dois registros de teste** pela interface do Xano: Categoria 2 e Totem 17. Foram mantidos IDs, autoria, títulos, instantes e demais campos. Não houve migração nem alteração de chamado preexistente. A fila técnica voltou a validar os 22 itens retornados.
- O State Reflex da gestão usava campos de formulário com os mesmos nomes da identidade da sessão (`nome`, `email`, `lojas_id`). Foram separados; a navegação deixou de apagar o nome autenticado e a gestão passou a carregar.
- Leituras de Lojas/usuários legados e do estado vazio de Totem foram adaptadas sem modificar linhas legadas. O aviso inicial de contrato incompatível desapareceu da gestão e a fila carregou após a correção dos registros de teste e da interpretação do estado vazio.

## Situação dos dados de teste

O usuário informou que removeu manualmente os cadastros descartáveis da rodada anterior. Os IDs citados na evidência histórica não são inventário atual e não devem ser usados para novas operações. Nesta revisão de frontend não foram criados, editados ou excluídos registros na `v1`; submissões mutáveis foram exercitadas com mocks. Nenhuma limpeza adicional foi feita.

## Revisão de navegação e experiência administrativa — 2026-11-07

| Área | Resultado | Evidência e limite |
| --- | --- | --- |
| Rotas | **Passou** | Sidebar abriu `/administracao/gestao`; acesso direto a `/administracao/usuarios` redirecionou para a mesma gestão, com guarda de administrador. A página independente e o formulário duplicado foram removidos. |
| Dashboard | **Passou** | Navegador com sessão administrativa exibiu três cards, indicadores derivados dos contratos, composição próxima ao frame Figma e layout verificado em larguras de 1024 e 800 px. |
| Modais | **Passou** para abertura e cancelamento visual; **passou** para submissão em mocks | Modais de Usuário, Loja e Totem abriram e fecharam. Criação, validação, mensagem de erro/sucesso e atualização da lista foram testadas localmente; nenhuma criação foi submetida ao Xano live. |
| Listagens | **Passou** | As três listagens carregaram na rota de gestão. Busca textual, estado vazio, ações contextuais e confirmação de exclusão foram exercitados visualmente; a exclusão foi cancelada. |
| Chamados | **Passou** para navegação e catálogo visual; **passou** para submissão em mocks | Administrador viu `Criar chamado` em `/inicio` e o formulário compartilhado em `/chamados/novo`, com Totens globais. O Gerente continua usando o mesmo componente sob o próprio escopo. Nenhum chamado foi criado nesta rodada. |
| Sessão | **Passou** em testes locais | State rejeita mutações sem perfil/token de administrador e descarta resposta assíncrona após troca de token/usuário. |
| Python, Reflex e OpenSpec | **Passou** | `make check`: 461 testes e compilação Reflex; `openspec validate administracao-mira --strict`; `git diff --check`. |
| Xano nesta revisão | **Não executado** para push e testes mutáveis | Nenhum XanoScript foi alterado nesta rodada. Dry-run somente leitura identificou dois endpoints `interacoes_chamado` fora do escopo como atualizados; não foram publicados. |

O navegador exibiu ocasionalmente uma notificação transitória `Connection Error` do runtime Reflex, embora os dados e ações de leitura tenham carregado. O fluxo de submissão de cadastro e chamado no navegador live permanece propositalmente não executado para não gerar registros. O autofill do Chrome preencheu campos de um modal com valores salvos pelo navegador; as credenciais de cadastro não são persistidas em State.

**Ajuste visual posterior:** o botão `Criar chamado` de Administrador e Gerente passou a usar o mesmo componente e a mesma composição de cabeçalho. As mensagens visíveis da gestão deixaram de mencionar a integridade ou as validações do Xano. `make check` passou com 461 testes e compilação Reflex. O servidor de produção local foi reiniciado na porta 3001; a confirmação visual foi feita pelo usuário, conforme sua preferência de não abrir mais o navegador pelo agente.

**Correção da confirmação de exclusão:** uma resposta de dependência impeditiva do Totem passa a aparecer dentro do diálogo, que permanece aberto após a tentativa. Cancelar limpa a mensagem. Os testes locais cobrem vínculos/histórico e transferência histórica com cliente fictício; nenhuma exclusão foi enviada à `v1` nesta correção. `make check` passou com 463 testes e compilação Reflex; OpenSpec strict e `git diff --check` passaram. A validação visual desta correção fica a cargo do usuário, conforme sua orientação de não abrir o navegador pelo agente.

**Refino das listagens:** IDs internos foram removidos da apresentação; o nome da Loja aparece para usuários e Totens; perfil e situações aparecem visualmente em maiúsculas. O card de usuários mostra as quantidades dos quatro perfis. Busca, limpeza contextual e contagem filtrada foram reorganizadas. `make check` passou com 464 testes e compilação Reflex; OpenSpec strict e `git diff --check` passaram. A validação visual segue com o usuário, sem abertura de navegador pelo agente.

**Consulta pontual somente leitura na `v1`:** o Totem denominado `E2E S5 c37f6cab Totem` tinha, no instante da consulta, três telemetrias e dois registros de transferência temporal; não foram encontrados chamados, eventos de disponibilidade ou preferências da fila ligados a ele. Esses registros explicam o bloqueio da exclusão segundo o contrato atual. Nenhum dado foi criado, alterado ou excluído durante a consulta. O resultado é um retrato temporal, não um inventário permanente do ambiente.

## Evidências ainda pendentes

- **Não executado:** cenário real de “último Administrador” na `v1`. Há dois Administradores existentes; reduzir esse número para testar a condição alteraria contas reais. O código Xano faz a checagem na transação, e o cenário positivo com outro Administrador passou, mas o bloqueio do último não foi observado em HTTP persistido. Corrida concorrente entre duas mudanças e rollback por falha provocada também não foram demonstrados.
- **Parcial:** exclusão de Totem foi testada com telemetria/chamados e com transferência temporal, mas não isoladamente com cada tipo de preferência e evento de disponibilidade. A checagem existe no contrato; os casos não executados não são declarados aprovados.
- **Parcial:** leitura histórica de eventos de disponibilidade foi coberta por testes de código/mocks, sem evento persistido de teste antes e depois da transferência.
- **Parcial:** interface Reflex não teve submissão visual de abertura manual, edição de todos os cadastros, erro de dependência e bloqueio do último Administrador na `v1`. O endpoint global, os formulários e o isolamento de sessão foram testados separadamente com mocks.
- **Limitação aceita no escopo acadêmico:** não há prova de isolamento forte entre duas escritas simultâneas no Xano Free; os testes comprovam fluxos sequenciais, não garantia absoluta de concorrência. Não houve teste de carga/stress.

## Encerramento autorizado — 2026-11-08

O usuário solicitou explicitamente finalizar e arquivar esta change com **31 de 34 tasks concluídas**. As tasks 4.4, 5.4 e 6.4 permanecem abertas porque seus cenários isolados de dependência, último Administrador e evento histórico de disponibilidade não foram integralmente demonstrados sem alterar dados da `v1`. O Archive registra essa limitação aceita para o encerramento documental; não transforma cenários não executados em testes aprovados nem autoriza mutações em dados reais.

Na revisão final, `make check` passou com 464 testes e compilação Reflex; as 130 definições XanoScript passaram na validação sintática; `openspec validate administracao-mira --strict`, `openspec validate --specs` e `git diff --check` passaram. O dry-run de `xano workspace push -b v1` mostrou somente dois endpoints genéricos de `interacoes_chamado` fora do escopo, que não foram publicados. As delta specs foram consolidadas nas specs principais. Não houve nova escrita de dados no Xano nesta revisão final.
