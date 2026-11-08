# Tasks

A ordem de execução, as dependências e os pontos de aprovação estão no Migration Plan de [design.md](./design.md).

## 1. Revisão humana e gates antes do Apply

- [x] 1.1 Solicitante transferido de Loja: decidido — mantém a rejeição pelo vínculo, com interface própria restrita aos chamados associados e validação no Xano.
- [x] 1.2 Autor no histórico público: decidido — nome de exibição e perfil do autor humano; `Sistema` para evento automático; sem e-mail, IDs ou dados desnecessários.
- [x] 1.3 `alteracao_status`: aprovado conceitualmente como decisão documental. Nenhuma alteração de schema, dado ou workspace Xano nesta etapa.
- [x] 1.4 G1–G4: decididos — `resumo_totem = null` e sem drawer no solicitante; rotas `/chamados/solicitados` e `/chamados/solicitados/[chamado_id]` com item de menu para todos os perfis oficiais; lista ordenada por `ultima_atualizacao_em` decrescente sem filtros, preferências ou paginação; autor sem perfil reconhecido como `{nome, perfil: null}`.
- [ ] 1.5 Obter a aprovação formal do Apply antes de iniciar qualquer tarefa das seções 2 a 7.
- [ ] 1.6 **Gate E0.3** — antes de qualquer tarefa que dependa de rollback (3.2 e 4.3), consultar a documentação oficial do Xano e o Xano Developer MCP sobre `db.transaction` no plano Free e o efeito de erro, `precondition` e `throw` sobre escritas anteriores. Evidência: registro separando comportamento documentado, comportamento observado e hipótese. Se o rollback não for confirmado, interromper e apresentar alternativas para decisão, sem reordenar escritas e sem declarar atomicidade.

## 2. Backend Xano — status `Reaberto`

- [ ] 2.1 Substituir `Solução Rejeitada` por `Reaberto` como destino canônico e manter `Solução Rejeitada` como legado de leitura em `validar_save_tratativa_chamado.xs` (status atual aceito; destinos `Reaberto` e `Solução Rejeitada` rejeitados). Evidência: testes XanoScript de Save para destino `Reaberto`, destino `Solução Rejeitada`, saída de `Reaberto` e saída de `Solução Rejeitada`.
- [ ] 2.2 Incluir `Reaberto` na normalização e validação de Status de `listar_chamados_gerente.xs`, `listar_chamados_tecnico.xs`, `salvar_preferencia_filtros_gerente.xs` e `salvar_preferencia_fila_tecnica.xs`, preservando o legado. Evidência: testes de filtro e preferência com `Reaberto`, `reaberto` e `Solução Rejeitada`.
- [ ] 2.3 Incluir `Reaberto` nas listas de status aceitos de `assumir_chamado_tecnico.xs` e na deduplicação de `verificar_falhas_GET.xs`. Evidência: teste de atribuição em `Reaberto` sem mudança de status e harness de heartbeat com incidente `Reaberto`.

## 3. Backend Xano — histórico público

- [ ] 3.1 Após a aprovação do Apply, acrescentar o valor aditivo `alteracao_status` ao enum `tipo_evento` de `xano/table/interacoes_chamado.xs`, sem alterar registros existentes. Evidência: validação XanoScript e diff do dry-run limitado ao enum; push somente com aprovação do diff.
- [ ] 3.2 Somente após 1.6 confirmado e após o merge do Reflex compatível (6.5, 6.6) na `main`: gravar no Save, na mesma transação e apenas quando houver mudança efetiva de status, evento `alteracao_status` público com somente o par anterior/resultante, mantendo a auditoria interna `alteracao_chamado`. Evidência: testes de Save com e sem mudança de status e de falha do evento.
- [ ] 3.3 Criar a consulta de histórico público do Gerente autorizada pela Loja, filtrando `alteracao_status` + `publica`, com DTO `id`, `status_anterior`, `status_resultante`, `criado_em` e `autor`: `{nome, perfil}` com rótulo oficial; `{nome, perfil: null}` para usuário existente sem perfil reconhecido; `{nome: "Sistema", perfil: null}` quando `usuarios_id` é nulo; `null` quando `usuarios_id` está preenchido e o usuário não é encontrado. Evidência: testes de Loja própria, outra Loja, inexistente, perfil não Gerente, lista vazia, autor humano (Técnico e Gerente), autor sem perfil reconhecido, evento automático como `Sistema`, usuário não encontrado e ausência de e-mail, IDs, Loja do autor e `alteracoes` bruto.
- [ ] 3.4 Restringir `listar_comentarios_publicos_gerente.xs` a `tipo_evento` nulo ou `comentario`. Evidência: teste com evento público de status no mesmo chamado não retornado como comentário.

## 4. Backend Xano — rejeição de solução

- [ ] 4.1 Criar a função e o endpoint funcional único de rejeição (fora do prefixo `/gerente/`) com identidade de `$auth.id`, entrada `justificativa` e `ultima_atualizacao_em`, e autorização por Gerente da Loja ou solicitante associado, sem consultar a Loja ou o perfil atual do solicitante. Evidência: testes de Gerente da Loja proprietária (solicitante e não solicitante), Gerente de outra Loja, Gerente sem Loja, solicitante associado, solicitante transferido de Loja, solicitante transferido tentando outro chamado da Loja antiga, usuário sem vínculo, Técnico/Diretoria/Administrador e chamado automático.
- [ ] 4.2 Validar justificativa após trim (422), status `Resolvido` (409), `ultima_atualizacao_em` (409) e existência (404) antes de qualquer escrita. Evidência: um teste por erro, verificando ausência de escrita.
- [ ] 4.3 Somente após 1.6 confirmado: implementar a unidade de escrita em `db.transaction` com releitura do chamado e da identidade e revalidação da autorização, do status `Resolvido` e de `ultima_atualizacao_em`, seguida de exatamente quatro escritas na ordem aprovada (atualização do chamado para `Reaberto` com `ultima_atualizacao_em`; comentário público; evento `alteracao_status` público; auditoria `alteracao_chamado` interna), preservando responsável, prioridade, Categoria e SLA. Leituras de confirmação não são escritas. Evidência: teste de sucesso verificando a atualização do chamado, os três registros de interação distintos e os campos preservados; testes de autorização perdida e de status alterado na releitura sem nenhuma escrita.
- [ ] 4.4 Registrar no relatório do Apply o resultado de 1.6 aplicado à rejeição e ao Save existente, incluindo a ausência de prova de isolamento. Se o resultado não sustentar a unidade de escrita, parar para revisão.

## 4A. Backend Xano — consulta do solicitante

- [ ] 4A.1 Criar contratos de lista, detalhe, comentários públicos e histórico público do solicitante, autorizados somente por `solicitante_id == $auth.id`, sem depender da Loja ou do perfil atual. Comentários e histórico reutilizam os DTOs e filtros públicos do Gerente; o detalhe reutiliza os campos funcionais do Gerente com `resumo_totem = null`, sem alterar o detalhe do Gerente; a lista é ordenada por `ultima_atualizacao_em` decrescente, sem filtros, preferências ou paginação. Evidência: testes de solicitante associado, solicitante transferido de Loja, usuário sem vínculo (inclusive da mesma Loja), usuário sem chamados (lista vazia), chamado inexistente, ordenação, `resumo_totem = null`, detalhe do Gerente inalterado e ausência de comentários internos, auditoria e timeline técnica.

## 5. Segurança — interações privadas

- [ ] 5.1 Negar o perfil Gerente em `interacoes_chamado_GET.xs` e `interacoes_chamado_id_GET.xs`, preservando os demais perfis. Evidência: testes XanoScript de Gerente da mesma Loja recebendo 403 para interação pública e interna, e de Técnico mantendo o acesso atual.
- [ ] 5.2 Reverificar que nenhum outro endpoint acessível ao Gerente ou ao solicitante retorna interações internas, `alteracoes` ou telemetria indevida (contratos `gerente/*`, `solicitante/*`, CRUDs genéricos de `chamados`). Evidência: inventário registrado na revisão do Apply.

## 6. Interface Reflex

- [ ] 6.1 Cliente e DTOs em `app/services/service_desk.py` para rejeição, histórico público e contratos do solicitante, com payload mínimo e classificação tipada de 401/403/404/409/422/5xx; o State da rejeição usa mensagem própria para `XanoConflito`. Evidência: testes de cliente com respostas válidas, incompatíveis e cada erro.
- [ ] 6.2 Ação "Rejeitar solução" no detalhe do Gerente somente em `Resolvido`, com justificativa obrigatória, carregamento, sucesso, erro e recarga em conflito, sem simular transição. Evidência: testes de State e da página.
- [ ] 6.3 Seção de histórico público separada dos comentários, com autor (nome e perfil; somente nome quando `perfil` é nulo; `Sistema`; ou não informado quando `autor` é nulo), estados de carregamento, vazio (com aviso de histórico a partir da implantação) e erro isolado. Evidência: testes de State com autor humano, autor sem perfil, `Sistema` e autor nulo.
- [ ] 6.3A Interface própria do solicitante em `/chamados/solicitados` e `/chamados/solicitados/[chamado_id]` (`app/app.py`), com item "Chamados solicitados" para todos os perfis oficiais (`app/components/navegacao.py`); lista na ordem do backend, sem filtros, preferências ou paginação; detalhe com comentários públicos, histórico e rejeição, sem botão Detalhe do Totem, drawer, comentário, Save, atribuição ou timeline técnica. Evidência: testes de State, rotas e menu para solicitante transferido, chamado sem vínculo, lista vazia, menu nos quatro perfis e ausência do drawer.
- [ ] 6.4 Separar em `publicar_comentario` o tratamento do POST e do GET posterior do detalhe, com confirmação explícita. Evidência: testes de falha no POST e falha no GET posterior.
- [ ] 6.5 Reflex compatível (etapa E2): incluir `Reaberto` em `status_filtros` do Gerente, em `_STATUS_ATRIBUICAO_PERMITIDA` de `app/chamados/shared.py` e nas opções de filtro do Técnico, separando dos destinos do Save, que não oferecem `Reaberto` nem `Solução Rejeitada`. Evidência: testes de `test_chamados_shared.py`, `test_technical_state.py` e `test_lista_operacional_gerente.py`.
- [ ] 6.6 Reflex compatível (etapa E2): aceitar `alteracao_status` em `TIPOS_EVENTO_TIMELINE` e na normalização de `_evento_timeline`, e apresentá-lo na timeline técnica sem sugerir mudança duplicada. Evidência: teste do cliente com o tipo novo e teste do State técnico com evento público e auditoria da mesma mudança.
- [ ] 6.7 Obter aprovação explícita e realizar o merge de 6.5 e 6.6 na `main` antes de qualquer push Xano que grave `alteracao_status`. Evidência: referência do merge aprovado registrada antes do push 2.

## 7. Testes e validação integrada

- [ ] 7.0 Garantir cobertura explícita, rastreável aos cenários das specs, de: solicitante transferido de Loja (rejeição e consulta); solicitante sem vínculo com o chamado; Gerente da Loja proprietária; Gerente de outra Loja; revalidação da autorização dentro da unidade de escrita; autor humano no histórico (nome e perfil); autor sem perfil reconhecido; evento automático identificado como `Sistema`; usuário do evento não encontrado; `resumo_totem = null` no solicitante; e ausência de exposição de dados privados (comentários internos, auditoria, e-mail, IDs, telemetria) nos contratos do Gerente, do solicitante e nos GETs genéricos.
- [ ] 7.1 Executar testes XanoScript afetados via Xano Developer MCP e os testes Python focados; depois a suíte completa. Classificar cada resultado como passou, falhou, não executado, bloqueado por ambiente ou limitação aceita (por exemplo, ausência de `tzdata` no Windows).
- [ ] 7.2 Executar `reflex compile --dry` com o comando do projeto, `openspec validate acompanhamento-solicitante-rejeicao-solucao --strict` e `git diff --check`, incluindo arquivos não rastreados.
- [ ] 7.3 Para cada um dos dois lotes de push, executar `xano workspace push --dry-run` e revisar o diff completo; publicar somente com autorização humana explícita e repetir o dry-run após o push.

## 8. Documentação

- [ ] 8.1 Conferir que `docs/project-overview.md` e `docs/domain-model.md` refletem o comportamento implementado; registrar qualquer deriva encontrada no Apply.
- [ ] 8.2 Antes do Archive, consolidar os deltas em `openspec/specs/` após revisão independente.
