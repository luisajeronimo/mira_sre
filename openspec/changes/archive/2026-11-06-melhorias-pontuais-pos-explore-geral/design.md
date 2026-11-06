# Design

## Context

Ver `proposal.md`. A análise foi feita somente nos arquivos locais. `git status` estava limpo e não havia change ativa antes desta criação. O frontend usa contratos funcionais do Service Desk; nenhum consumidor ativo dos dois GETs genéricos de interações apareceu em `app/`, `simulator/` ou `fiscal/`. A integração externa não é observável apenas pelo repositório. O histórico arquivado de 02/11/2026 registra como **não executadas** as validações HTTP autenticadas de 422/403.

## Goals / Non-Goals

**Goals:** dez trilhas pequenas e independentes, com evidência própria e sem compartilhar refatorações; preservar contratos e regras consolidadas; aplicar autorização no Xano; distinguir correção comprovada, conflito documental e suspeita de desempenho.

**Non-Goals:** implementar nesta etapa de Propose; modificar schema, dados históricos, autenticação geral, regras de ciclo de vida, consultas por hipótese, funcionalidades futuras ou infraestrutura de testes; usar instância Xano ou navegador nesta etapa.

## Decisions

### 1. Leitura genérica de interações — correção de segurança comprovada

`interacoes_chamado_GET.xs` e `interacoes_chamado_id_GET.xs` retornam o registro bruto e permitem Gerente, inclusive quando a interação é interna. O contrato funcional `gerente/chamados/{id}/comentarios` já delega a `listar_comentarios_publicos_gerente`, que filtra `visibilidade == "publica"`; o frontend não chama os GETs genéricos.

| Perfil | Coleção atual | Por ID atual | Delta confirmado |
| --- | --- | --- | --- |
| Gerente | Permitido na própria Loja, com registro bruto | Permitido na própria Loja, com registro bruto | Negar ambos |
| Técnico | Permitido globalmente | Permitido globalmente | Preservar |
| Diretoria | Negado | Negado | Preservar a negação |
| Administrador | Negado | Negado | Preservar a negação |

A matriz atual decorre dos dois XanoScripts locais e dos helpers `autorizacao/exigir_perfil` e `autorizacao/exigir_escopo_loja`; não prova como uma instância remota está configurada. O usuário confirmou em 06/11/2026 o delta mínimo da tabela: Gerente negado, Técnico preservado e Diretoria/Administrador ainda sem esses GETs genéricos. Isso não amplia nem revoga o acesso destes últimos aos contratos funcionais da fila. A ausência de consumidores em `app/`, `simulator/` e `fiscal/` não comprova ausência de integração externa; verificar integrações declaradas antes da edição e submeter qualquer incompatibilidade encontrada à revisão.

A menor mudança é retirar apenas o Gerente dos dois GETs, preservando a permissão técnica e as negações atuais. A alternativa de sanitizar o CRUD genérico duplicaria o contrato funcional e exigiria dois DTOs; negar só a coleção deixaria a busca por ID aberta. Antes de publicar, revisar o diff desses dois recursos e confirmar que não surgiu consumidor externo documentado. Validar Gerente 403 nos dois, Técnico autorizado, e rota pública do Gerente sem conteúdo interno.

### 2. State do Gerente — isolamento local comprovadamente ausente

`AuthState.logout` limpa identidade/token, mas não os campos de `ChamadosGerenteState`; a flag `preferencia_filtros_carregada` pode manter filtros da sessão anterior. Usar o padrão de contexto por `usuario_id`, `_versao_sessao` e token já empregado na fila técnica, em uma rotina local ao State do Gerente. A saída acionada pela topbar deve descartar o contexto do Gerente antes do redirecionamento; entradas de carga e retornos assíncronos devem comparar o contexto atual para impedir reaproveitamento/repopulação após troca de sessão. Uma nova sessão do mesmo usuário relê a preferência durável. A composição pontual do evento de saída na casca é aceitável; não reescrever login, `AuthState` nem State técnico. Testar logout, troca de usuário, novo login do mesmo usuário e resposta tardia.

### 3. Regras de negócio — decisão humana por precedência temporal da spec

| Tema | Fontes em conflito | Estado local observado | Decisão explícita de 06/11/2026 |
| --- | --- | --- | --- |
| Comentário interno e `ultima_atualizacao_em` | `chamados-acompanhamento-gerente/spec.md` (07/10) proíbe atualização por evento interno não visível; `tratativa-operacional-chamados/spec.md` (16/10) exige atualização por comentário interno | `criar_comentario_operacional.xs` atualiza em todos os comentários | Preservar a regra operacional posterior: comentário interno atualiza a data, mas continua oculto no DTO público. Reconciliar a spec anterior do Gerente. |
| Interações em `Encerrado`/`Cancelado` | `domain-model.md` (27/09) proíbe novas interações; specs de tratativa (16/10) e acompanhamento do Gerente (17/10) permitem comentários sem reabrir | Funções de comentário aceitam terminal | Preservar comentários autorizados em terminal e bloqueio de campos funcionais; alinhar o modelo de domínio. |
| Gerente em terminal | `frontend-chamados-gerente/spec.md` (07/10) prevê ocultar envio; `chamados-acompanhamento-gerente/spec.md` (17/10) permite comentário público | `pages.py` apresenta o campo e `state.py` envia sem barrar por status | Preservar o comentário público autorizado em terminal; reconciliar a spec anterior do frontend. |
| Rejeição de solução | `domain-model.md` (27/09) atribui rejeição ao solicitante; `tratativa-operacional-chamados/spec.md` (16/10) permite Save operacional para `Solução Rejeitada` | Contrato de Save aceita a transição operacional | Preservar o Save de Técnico, Diretoria e Administrador com comentário obrigatório; distinguir o fluxo futuro de aceite/rejeição pelo solicitante no modelo de domínio. |

O usuário escolheu em 06/11/2026 manter as decisões da spec mais recente em cada tema. As datas acima são dos trechos relevantes (`git blame`), não da última alteração do arquivo inteiro. O código local já implementa essas quatro decisões; a trilha 3 reconcilia apenas o delta da spec anterior e o modelo de domínio, sem alterar contratos, autorização ou persistência. Os deltas devem ser validados antes de qualquer mudança funcional posterior.

### 4. Teste de filtros — correção de expectativa, sem mudança de contrato

`tests/test_lista_operacional_gerente.py` espera `int[] ativo_ids?` no endpoint, mas o endpoint recebe `text ativo_ids?`, decodifica JSON e passa `int[]` à função. Atualizar só a asserção do transporte e verificar ausência/lista JSON e não-array com testes focados já próximos. Não alterar cliente, endpoint nem função. A execução HTTP real de rejeição pertence ao item 8.

### 5. Simulator — corrigir agendamento sem nova infraestrutura

O laço atual dorme cinco minutos **após** o ciclo; isso soma duração do ciclo ao período. Registrar o início por `time.monotonic()`, calcular o próximo início a partir dele e dormir apenas o saldo positivo após a execução sequencial. Se um ciclo exceder o período, iniciar o seguinte depois da conclusão, sem sobreposição e sem executar ciclos de compensação. Preservar variáveis, 15 Totens e espaçamento interno de três segundos. Validar com relógio/sono simulados, incluindo ciclo demorado.

### 6. Fiscal — falhar sem URL explícita

Remover somente o valor padrão remoto de `XANO_BASE_URL`; a validação existente deve detectar ausência/valor vazio antes de `requests.get`, inclusive em execução direta do comando de verificação. Manter endpoint, chave e demais tempos. Testar ambiente sem URL e URL explícita com request simulado. `.env.example` já declara a variável; não é necessária alteração nele.

### 7. UI — ajustes locais em componentes existentes

Os inputs de `app/pages/administracao.py` dependem de placeholder. Aplicar o padrão de rótulo persistente já usado em `app/chamados/gerente/pages.py`, inclusive no seletor de Loja condicional e na troca de senha de primeiro acesso, sem trocar os controles nem regras de envio. A primeira implementação adicionou o título da rota na topbar compartilhada, mas o usuário a reprovou visualmente e determinou sua remoção em todos os perfis. Retirar somente a função de mapeamento de rota e o texto da topbar; manter identidade, saída, sidebar, títulos do conteúdo e rotas. O delta de `navegacao-lateral-perfis` e `DESIGN.md` registram que a topbar não repete o título. Validar compilação Reflex e testes focados; a avaliação visual do usuário é a evidência da rejeição da versão anterior.

### 8. Evidência HTTP negativa — matriz pequena, dependente de sessões

Executar, **somente em Apply autorizado e com sessões válidas disponíveis**, uma requisição por fronteira distinta: `gerente/chamados` com JSON não-array em `status` ou `ativo_ids` (esperado 422), `tecnico/chamados` com JSON não-array em um filtro múltiplo (esperado 422), `gerente/chamados` com filtro proibido (esperado 422), `tecnico/chamados` chamado por Gerente (esperado 403) e os dois GETs genéricos de interações chamados por Gerente (esperado 403 e nenhum conteúdo interno). Acrescentar caso de Loja alheia apenas quando houver sessão Gerente e IDs autorizados para provar o escopo, sem criar ou modificar dados. Registrar status/corpo sanitizado sem token. Se o Xano devolver código diferente, registrar **falhou** e tratar o contrato em revisão; não presumir que `inputerror` equivale a 422. Sem sessões, registrar **não executado/bloqueado por acesso autorizado**, nunca aprovado. Não construir harness de login nem entrar no navegador.

Em 06/11/2026, a matriz autorizada confirmou 403 de Gerente nos GETs genéricos e na fila técnica, 403 para Loja alheia, 200 de Técnico nos GETs genéricos e DTO público restrito; três entradas inválidas retornaram inicialmente 400, em desacordo com o 422 consolidado. A [documentação oficial de utilitários do Xano](https://docs.xano.com/the-function-stack/functions/utility-functions) descreve status personalizado via header. Uma primeira tentativa de `util.set_header` seguido de `return` validou sintaticamente, mas retornou 200 com corpo de erro e foi revertida. Após nova revisão e autorização humana específica, os dois GETs funcionais passaram a configurar o status em um ramo condicional e a usar `response` normal, sem executar a consulta no ramo inválido. O HTTP autenticado confirmou 422 nos três inválidos e 200 nas listas válidas; o dry-run posterior não mostrou alterações pendentes. A correção preservou o contrato 422 sem editar a spec consolidada.

Após essa validação, a requisição sem chave aos guards técnicos de `GET /verificar-falhas` e `POST /telemetria_equipamentos` (payload vazio) confirmou HTTP 200 com `{"error":"Não autenticado."}` nos dois casos, em desacordo com `openspec/specs/autenticacao-automacoes/spec.md`. O `return` antecipado após `util.set_header` tem o mesmo padrão que falhou nos filtros. O usuário autorizou corrigir essa falha. A menor alteração usa status `HTTP/1.1 401 Unauthorized` e a resposta normal do endpoint, atribuindo inicialmente o corpo público exato e executando a lógica operacional apenas no ramo autenticado. A comparação de chave, as validações funcionais e o payload de sucesso foram preservados. Após validação XanoScript, testes e dry-run seletivo com dois UPDATEs, o push autorizado publicou as duas rotas; o HTTP confirmou 401 e corpo exato sem chave e com chave aleatória inválida, e o dry-run posterior ficou limpo. O caminho positivo não foi executado, pois não havia credencial técnica autorizada para esse teste.

### 9. Consultas — investigação sem autorização para otimizar

`listar_ativos_monitoramento.xs` faz uma consulta de ativos e duas consultas por ativo; `listar_chamados_tecnico.xs` possui múltiplos ramos. Isso demonstra custo estrutural, não lentidão real. Levantar contagem de Totens/chamados e medir, com acesso autorizado posterior, tempo de resposta de três chamadas repetidas às rotas funcionais de monitoramento e fila global em conjunto estável, além de registrar o número de consultas observável no debugger/trace disponível no plano Free. Comparar com a necessidade acadêmica real; se houver problema comprovado, abrir revisão de escopo antes de qualquer alteração Xano. Nenhum índice, cache, paginação ou consulta nova é autorizado por esta change.

### 10. Funcionalidades futuras — backlog documental

`project-overview.md` descreve dashboards, administração de Lojas/Totens, aceite/rejeição pelo solicitante e fechamento automático como visão futura. Registrar a distinção nesta change, sem tratar ausência de implementação como defeito atual e sem criar tasks de código para essas capacidades. Uma futura implementação requer requisitos próprios e decisão quando houver conflito com specs atuais.

## Risks / Trade-offs

- [Consumidor externo desconhecido dos GETs genéricos] → revisar inventário e contrato antes do Apply do item 1; se existir consumidor legítimo, submeter a menor alternativa a revisão antes de restringir.
- [State antigo exposto por resposta assíncrona] → vincular aplicação da resposta à identidade/versão da sessão capturada e testar resposta tardia.
- [Divergência documental confundida com autorização de nova funcionalidade] → a decisão humana de 06/11/2026 escolhe as regras já presentes nas specs mais recentes; os deltas reconciliam textos antigos sem criar comando ou fluxo novo.
- [HTTP 422 divergente nos filtros inválidos] → a tentativa de header mais retorno produziu 200 e foi revertida; a resposta normal com header de status, autorizada separadamente e verificada por HTTP, corrigiu os três casos sem alterar as listas válidas.
- [HTTP 401 divergente nos guards técnicos] → usar a resposta normal com ramo autenticado isolado; confirmar 401 e corpo exato por HTTP sem executar heartbeat ou persistir telemetria.
- [Métrica de desempenho sem acesso runtime] → limitar a conclusão do item 9 ao inventário local até existir ambiente autorizado; não otimizar por contagem teórica.

## Migration Plan

Não há migração de dados. Cada item pode ser aplicado e revertido isoladamente. A restrição Xano do item 1 exige validação do XanoScript, `xano workspace push --dry-run`, revisão do diff completo e autorização humana para push real; após publicação, novo dry-run. O item 3 requer apenas conciliação documental das quatro decisões já implementadas. Itens 8 e 9 dependem de evidência runtime e não bloqueiam edições locais independentes.
