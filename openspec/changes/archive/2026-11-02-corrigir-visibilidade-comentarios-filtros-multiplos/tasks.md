# Tasks

> A reprovação humana anterior foi sucedida pela aprovação humana dos filtros informada nesta revisão. A aprovação não equivale a testes HTTP específicos de erros ou autorização.

### Encerramento por decisão humana

- O usuário dispensou as três validações HTTP autenticadas pendentes e autorizou o encerramento. Elas permanecem **não executadas**, não aprovadas: entradas inválidas e JSON que não seja array (422), e perfil ou escopo não autorizado (403).
- Risco residual aceito: os códigos e a rejeição efetiva desses casos na fronteira HTTP publicada não foram comprovados. Em particular, o `inputerror` para JSON que não seja array não explicita 422. A aprovação funcional dos filtros e os testes de funções/mocks não eliminam esse risco.
- As tasks 2.3, 2.4 e 3.1 são encerradas com essa dispensa explícita, sem afirmar a execução ou aprovação das verificações dispensadas. A conferência visual final da timeline é responsabilidade do usuário.

### Verificação HTTP sem nova autenticação

- GET real de `tecnico/chamados` sem token: **401**; GET real de `gerente/chamados` sem token: **401**. São verificações de ausência de autenticação, não de autorização de perfil.
- Nenhum token de sessão de usuário foi encontrado nas variáveis locais de ambiente ou no `.env`; não foi realizado login, acesso ao navegador ou extração de sessão do Reflex.
- **Não executados:** HTTP autenticado com valores inválidos ou JSON que não seja array e verificação do código 422; HTTP com perfil ou escopo indevido e verificação do código 403. Não há evidência para afirmar que esses casos passam; `inputerror` na fronteira para não-array não explicita 422.
- Tasks 2.3, 2.4 e 3.1 permanecem abertas. Para concluir os critérios HTTP, é necessária uma sessão de API já autenticada com os perfis/escopos correspondentes e a execução dos casos negativos, sem expor tokens nos registros.

### Revisão final após aprovação humana dos filtros

- O usuário informou aprovação humana dos filtros após a publicação. O código mantém OR por coleção, AND entre critérios, catálogo global de Técnicos e isolamento por usuário/escopo; testes existentes cobrem rascunho, aplicação, limpeza, legado e ordenação.
- Timeline ajustada: cada card apresenta uma data; no agrupado é a data da alteração, com badge do comentário abaixo. O State preserva as datas originais de ambos os registros.
- Validação local: 198 testes focados, compilação Reflex, OpenSpec strict e validação sintática dos cinco XanoScripts de listagem/catálogo passaram. A validação visual do último ajuste fica pendente de revisão humana.
- Permanecem sem prova específica as respostas HTTP de erro/autorização, incluindo filtros proibidos e entradas inválidas; não se contabilizam testes de debugger ou mocks como HTTP. As tasks 2.3, 2.4 e 3.1 continuam abertas pelos critérios ainda não comprovados.

### Publicação e validação pendente — 02/11/2026

- Dry-run completo e seletivo: exatamente `tecnico/chamados` GET, `gerente/chamados` GET e `service_desk/listar_ativos_tecnico`; diff remoto revisado e os três recursos publicados com autorização explícita.
- XanoScript: três arquivos válidos. Dry-run completo após publicação: nenhuma alteração pendente.
- Testes remotos focados: quatro testes aprovados (cinco asserções): OR de Status, AND entre filtros, responsável com não atribuído e catálogo global. São testes de funções com mocks, não testes HTTP dos endpoints.
- Cliente: três testes focados aprovados. Arrays são codificados em um único parâmetro JSON e os endpoints exigem array após decodificação; entradas ausentes tornam-se listas vazias. A execução HTTP real desse contrato permanece pendente.
- Pendências daquela rodada: a aprovação humana posterior dos filtros foi informada pelo usuário; a validação visual do novo ajuste da timeline e os testes HTTP negativos específicos permanecem pendentes.

## 1. Modelo de visibilidade e timeline

- [x] 1.1 Remover `visibilidade` da escrita de novos eventos `atribuicao`, `reatribuicao`, `liberacao` e `alteracao_chamado`, mantendo-a obrigatória nos comentários; verificar com unit tests Xano de cada tipo e sem alterar a tabela ou registros históricos.
- [x] 1.2 Normalizar o DTO global para retornar visibilidade somente em comentários e `null` em eventos operacionais novos ou legados; verificar testes de comentário Público/Interno, evento legado com metadado e agrupamento por `comentario_interacao_id`.
- [x] 1.3 Renderizar badge somente para comentários, inclusive agrupados, e nenhum badge em evento operacional; verificar testes Reflex de cards independentes/agrupados e compilação focada.
- [x] 1.4 Endurecer a consulta pública do Gerente para exigir interação de comentário explicitamente Pública, mantendo status atual pelo detalhe autorizado; verificar testes Xano contra comentário Interno, evento sem visibilidade, evento legado e chamado de outra Loja.

## 2. Persistência e consultas Xano

- [x] 2.1 Obter aprovação humana explícita do campo recomendado antes de editar schema; após aprovação, adicionar somente `filtros_multiplos` opcional a `preferencias_fila_chamados` e verificar via Xano Developer MCP/dry-run que não há conversão, tabela nova, backfill ou remoção.
- [x] 2.2 Evoluir obter/salvar preferência global para objeto completo, fallback apenas quando JSON for `null`, falha fechada quando inválido e neutralização dos escalares no primeiro save; verificar unit tests de legado, objeto vazio, Limpar, filtro antigo não reaparecer e isolamento usuário+escopo.
- [x] 2.3 Evoluir a listagem global e seu endpoint para arrays de Status, Totem, Loja, Responsável e Prioridade mais `incluir_nao_atribuido`; verificar transporte JSON no GET, OR interno, AND externo, normalização, IDs positivos, Não atribuído com Técnicos, datas/número/ordenação e autorização. **Validações HTTP negativas dispensadas pelo usuário; não executadas.**
- [x] 2.4 Evoluir obter/salvar preferência e listagem do Gerente somente para arrays de Status/Totem, mantendo Loja da sessão; verificar unit tests de fallback legado, objeto vazio, Totem externo, rejeição 422 dos filtros ausentes e perfil indevido. **Validações HTTP negativas dispensadas pelo usuário; não executadas.**
- [x] 2.5 Validar todos os XanoScripts afetados e executar seus testes unitários focados antes de concluir o grupo.

## 3. Contratos e interface Reflex

- [x] 3.1 Atualizar DTOs, parsers e cliente Service Desk para arrays canônicos, coleções JSON em GET, payloads PUT exatos e booleano separado de Não atribuído; verificar testes de request/response, listas vazias, preferência escalar normalizada e erro de contrato. **Validações HTTP negativas dispensadas pelo usuário; não executadas.**
- [x] 3.2 Criar um componente compartilhado de dropdown multisseleção com check, resumo, foco e estado desabilitado conforme `DESIGN.md`, sem dependência nova; verificar testes estruturais, teclado/foco e compilação Reflex.
- [x] 3.3 Atualizar State/página do Gerente para rascunho, confirmado e aplicado múltiplos somente em Status/Totem; verificar alternância sem consulta, Aplicar, Limpar, restauração após login e ausência de Loja/Responsável/Prioridade.
- [x] 3.4 Atualizar State/página global para os cinco filtros múltiplos; verificar etiquetas, Não atribuído separado, isolamento `Todos`/`Atribuídos a mim`, Aplicar/Limpar, restauração após login e preservação da ordenação.

## 4. Integração e gates

- [x] 4.1 Executar suíte Python focada, compilação Reflex, OpenSpec strict e `git diff --check`; registrar separadamente qualquer falha externa ao escopo.
- [x] 4.2 Executar `xano workspace push --dry-run`, confirmar somente os recursos enumerados em `design.md` e não publicar sem autorização humana explícita.
- [x] 4.3 Solicitar revisão read-only do MIRA Reviewer sobre specs, diff, testes, autorização, histórico e compatibilidade legada; resolver correções ou interromper diante de nova decisão humana.

## Evidências da retomada — 2026-11-02

- Integração local existente preservada e revisada. Arrays conectam dropdowns, States, cliente HTTP e inputs Xano. Filtros sucessivos combinam AND; pertencimento em cada coleção combina OR, incluindo responsável nulo junto a Técnicos.
- Corrigidos nesta retomada: validação da Loja de cada Totem na leitura da preferência do Gerente; rejeição de filtros proibidos vazios via arrays anuláveis com default null; normalização de visibilidade pública legada em evento operacional no helper de apresentação.
- Suíte Python completa: **431 passed**. Inclui testes comportamentais de rascunho/Aplicar/Limpar e isolamento de sessão, cliente HTTP com parâmetros repetidos e guardas estáticas Xano. Expectativas escalares foram adaptadas ao contrato aprovado preservando autorização e ordenação.
- Reflex `compile --dry`: **passou**. Avisos de SitemapPlugin e depreciação de App(theme=...) não impedem compilação.
- Xano Developer MCP: **108 arquivos locais válidos, zero inválidos**; os três arquivos Xano corrigidos nesta retomada foram revalidados e passaram.
- OpenSpec strict e `git diff --check`: **passaram**.
- Runtime da implementação Xano nova: **não executado**. Validação sintática e guardas Python não comprovam execução/persistência no runtime. Nenhum teste CLI remoto foi contabilizado como validação local. Tasks 1.1, 1.2, 1.4 e 2.2–2.5 permanecem abertas por seus critérios runtime, apesar da implementação local presente.
- Teclado/foco em navegador: **não executado**; estrutura do componente e compilação passaram. Task 3.2 permanece aberta.
- Dry-run Xano: **passou**, somente recursos previstos no design; nenhum recurso removido. Não houve publicação, migração histórica, commit, push Git, merge ou Archive.

### Recursos exatamente pendentes no dry-run

- Tabela `preferencias_fila_chamados`: UPDATE + ADD_FIELD (`filtros_multiplos` opcional).
- Funções `service_desk/`: `assumir_chamado_tecnico`, `listar_chamados_gerente`, `listar_chamados_tecnico`, `listar_comentarios_publicos_gerente`, `obter_chamado_tecnico`, `obter_preferencia_fila_tecnica`, `obter_preferencia_filtros_gerente`, `salvar_preferencia_fila_tecnica`, `salvar_preferencia_filtros_gerente`, `validar_save_tratativa_chamado`.
- Endpoints: `gerente/chamados GET`, `gerente/preferencias-fila PUT`, `tecnico/chamados GET`, `tecnico/preferencias-fila PUT`.
- Os endpoints GET de preferências não exigem diff: já delegam às funções modificadas.

- Revisão independente MIRA Reviewer: **aprovado** após confirmar as três correções; aprovação do código, com runtime Xano e teclado real explicitamente pendentes. Progresso: **8/16 tasks concluídas**.

## Revisão direcionada da 2.3 e preparação de publicação

- Listagem e endpoint reinspecionados: sem nova correção funcional identificada; OR/AND, responsável misto, escopo e ordenação presentes no código local.
- Dry-run reconferido: exatamente 15 recursos previstos (1 tabela, 10 funções, 4 endpoints), sem publicação.
- Preparados matriz de testes remotos, critérios de evidência e sequência com schema JSON antes das funções em [validacao-publicacao.md](validacao-publicacao.md).
- Pendência local identificada: completar mocks das leituras `db.get usuarios` nos testes Xano antigos de responsável e acrescentar testes determinísticos de preferências/multisseleção. A cobertura atual não torna essas tasks exclusivamente dependentes do remoto. Teclado local também permanece pendente.
- Nenhuma checkbox adicional concluída nesta rodada; testes remotos da versão nova continuam não executados.


## Publicação e validação autorizadas — 2026-11-02

- Publicados os 15 recursos: schema primeiro; depois 10 funções e 4 endpoints. Correções posteriores somente em fixtures de `obter_chamado_tecnico`, republicadas no mesmo recurso.
- Task 3.2: seis checks reais de teclado passaram (Chrome headless/Playwright, harness Reflex prod importando o componente original).
- Tasks 1.1/1.4: testes remotos de escrita operacional passaram; leitura real do chamado 52 confirmou comentário Interno/Público, evento legado com visibilidade null, consulta pública restrita e negação de Loja externa.
- Task 2.2: testes remotos de legado/null, vazio e inválido passaram; persistência/Limpar reais e isolamento Técnico 2/Todos, Técnico 2/Atribuídos a mim e Técnico 14/Todos passaram; preferência original restaurada e relida. Gerente 9 também passou persistência/Limpar/restauração.
- Tasks 2.3/2.4 continuam abertas: funções têm evidência remota, mas desserialização de GET repetido e respostas HTTP autenticadas 422 ainda precisam de sessão de usuário. Não há credencial/sessão HTTP disponível no ambiente; debugger CLI não substitui essa fronteira.
- Dry-run final após republicação: **sem alterações pendentes**. OpenSpec strict e diff-check passaram. Revalidação MCP: 22 funções Service Desk válidas.
- Detalhes das evidências e das fixtures em `validacao-publicacao.md`. Sem commit, push Git, merge ou Archive.

- Fechamento automatizado: **68/68 testes remotos focados, 113 asserções**, após repetição somente das quatro fixtures corrigidas; **54 testes Python focados** passaram novamente. Reviewer aprovou a correção e a separação entre debugger e HTTP. **14/16 tasks concluídas**, mantendo 2.3/2.4 abertas exclusivamente pelos critérios HTTP ainda sem evidência.
