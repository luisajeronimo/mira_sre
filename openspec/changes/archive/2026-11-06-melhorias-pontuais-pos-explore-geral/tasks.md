# Tasks

## 1. Acesso do Gerente às interações

- [x] 1.1 Verificar integrações externas declaradas que consumam os dois GETs genéricos e registrar o resultado; se houver incompatibilidade com a matriz confirmada em `design.md`, submeter o caso à revisão antes de editar. A ausência de consumidor local não encerra esta verificação.
- [x] 1.2 Retirar somente o acesso do Gerente nos dois GETs genéricos `interacoes_chamado`; verificar por teste XanoScript focado que Gerente é negado em coleção e ID, Técnico permanece autorizado, Diretoria/Administrador não ganham permissão e o GET funcional do Gerente continua público/sanitizado.
- [x] 1.3 Validar os dois XanoScripts alterados, revisar `xano workspace push --dry-run` e registrar diff exato; push real exige autorização humana explícita e, se ocorrer, novo dry-run e HTTP negativo do item 8. Não concluir 1.2 apenas por mock local.

Evidência de 1.1: busca nos consumidores e documentos locais não encontrou chamada aos dois GETs genéricos; o usuário informou em 06/11/2026 que não conhece integração externa consumidora. Isso não prova ausência absoluta de consumidor fora do repositório; se surgir um, a incompatibilidade volta para revisão antes de publicação.

Evidência de 1.2/1.3: teste focal `test_gets_genericos_de_interacoes_negam_gerente_sem_alterar_consulta_publica` passou; Xano Developer MCP validou os dois arquivos (2 válidos, 0 inválidos). Em 06/11/2026, após autorização humana explícita, o dry-run seletivo do workspace 152692 listou exatamente `interacoes_chamado GET` e `interacoes_chamado/{interacoes_chamado_id} GET` como UPDATE; o push interativo publicou 2 documentos; o novo dry-run seletivo retornou `No changes to push`. Com as contas E2E autorizadas, Gerente recebeu HTTP 403 na coleção e por ID, Técnico recebeu HTTP 200 em ambos, e a rota funcional do Gerente retornou HTTP 200 com DTO limitado a `id`, `conteudo`, `criado_em` e `autor.nome`. A negação de Diretoria/Administrador permanece verificada no XanoScript local, sem sessão E2E desses perfis. A divergência 400/422 identificada na matriz foi corrigida e validada no item 8.

## 2. Isolamento do State do Gerente

- [x] 2.1 Adicionar limpeza local do contexto de `ChamadosGerenteState` na saída e guarda de identidade/versão de sessão na entrada e retorno das cargas, sem refatorar `AuthState`; verificar teste de logout, outro Gerente, novo login do mesmo Gerente, preferência relida e resposta tardia sem repopulação.

Evidência de 2.1: `tests/test_gerente_lista_state.py`, `tests/test_gerente_comments.py` e `tests/test_sidebar_global.py` passaram (67 testes). Casos focados cobrem logout, troca para outro Gerente, nova sessão do mesmo Gerente, releitura da preferência e resposta tardia após saída.

## 3. Conflitos de regra de negócio

- [x] 3.1 Registrar a decisão humana explícita de manter, em cada conflito da matriz, a regra do trecho de spec mais recente; verificar a origem temporal e que não houve alteração funcional por inferência.
- [x] 3.2 Reconciliar os trechos anteriores em deltas de spec e no modelo de domínio, mantendo o comportamento atual; verificar coerência entre specs, modelo, contratos e testes, sem misturar correções de outros itens.

Evidência de 3.1: decisão do usuário em 06/11/2026; `git blame` dos trechos mostrou tratativa operacional de 16/10 posterior à regra do Gerente de 07/10 para comentário interno, acompanhamento do Gerente de 17/10 posterior ao frontend de 07/10 para comentário em terminal, e tratativa de 16/10 posterior ao modelo de domínio de 27/09 para terminais e `Solução Rejeitada`. Código local já segue as quatro decisões; nenhuma função de negócio foi editada nesta trilha.

Evidência de 3.2: delta `MODIFIED` preserva todos os cenários anteriores de última atualização e adiciona o caso de comentário interno; delta de frontend permite envio público em terminal. `docs/domain-model.md` distingue comentários em terminal, Save operacional para `Solução Rejeitada` e fluxo futuro de aceite/rejeição pelo solicitante. `openspec validate --strict`, `git diff --check` e 98 testes focados de Gerente/Técnico passaram. Nenhum XanoScript ou fluxo Reflex de negócio foi alterado para resolver estes conflitos.

## 4. Teste de filtros múltiplos

- [x] 4.1 Corrigir apenas a asserção do tipo de transporte em `tests/test_lista_operacional_gerente.py` para `text ativo_ids?`, preservando `int[]` na função; verificar teste focado de JSON array, ausência de filtro e rejeição local de não-array sem alterar cliente ou XanoScript.

## 5. Periodicidade do Simulator

- [x] 5.1 Ajustar somente o laço de `simulator/simulator.py` para agendar o próximo início pelo relógio monotônico e dormir o saldo positivo, sem ciclos sobrepostos; verificar com relógio falso inícios a 300 s no caso normal e início após conclusão no caso demorado, mantendo envio sequencial e intervalo entre Totens.

## 6. URL do Fiscal

- [x] 6.1 Remover o fallback remoto de `XANO_BASE_URL` em `fiscal/fiscal.py` e falhar antes de request quando ausente/vazia; verificar testes focados com ambiente sem URL e com URL explícita, preservando endpoint, header e demais configurações.

## 7. Interface e acessibilidade

- [x] 7.1 Acrescentar rótulos persistentes aos campos existentes de criação de usuário e primeiro acesso em `app/pages/administracao.py`, inclusive Loja condicional; verificar associação semântica e presença do rótulo com campo preenchido, sem mudança de payload ou validação.
- [x] 7.2 Remover de `app/components/layout.py` os títulos de rota da topbar compartilhada para todos os perfis, conforme reprovação visual explícita do usuário; preservar identidade, saída, sidebar e rotas, atualizar o delta de `navegacao-lateral-perfis` e `DESIGN.md`, e validar compilação Reflex e testes focados.

Evidência local de 7.1/7.2: o teste dos rótulos confere associação `html_for`/`id` em todos os campos, inclusive Loja condicional e primeiro acesso; os rótulos continuam nós independentes dos valores e não houve mudança de payload. A primeira versão da topbar com títulos de rota compilou, mas o usuário a reprovou após conferência visual e determinou a remoção em todos os perfis. A função `_contexto_pagina` e o texto foram removidos do único componente compartilhado da topbar; identidade e saída permanecem. O teste que exigia os títulos foi retirado. Após a remoção, `reflex compile --dry`, 31 testes focados de Administração/casca e OpenSpec strict passaram; a nova versão não foi aberta em navegador pelo agente.

## 8. Evidência HTTP negativa

- [x] 8.1 Com sessões de API já autorizadas, executar a matriz mínima de `design.md` para JSON não-array, filtro proibido, perfil indevido e os dois GETs genéricos; registrar código/corpo sanitizado e ausência de dados internos, distinguindo passou, falhou e não executado. Sem sessões, marcar bloqueado por acesso autorizado e não construir login de teste.
- [x] 8.2 Executar o caso de Loja alheia somente se houver sessão Gerente e IDs apropriados já existentes; verificar rejeição sem alteração de dados ou registrar explicitamente a dependência como não executada.
- [x] 8.3 Investigar um mecanismo de HTTP 422 comprovadamente funcional no Xano para os três ramos inválidos identificados, antes de propor outra correção localizada; preservar o contrato aprovado e não repetir a tentativa de header seguido de retorno que produziu 200. Qualquer novo push exige revisão do diff e autorização humana específica.
- [x] 8.4 Corrigir pontualmente os guards de `verificar-falhas` e `telemetria_equipamentos` para responder 401 com corpo público exato pela resposta normal, sem executar lógica operacional sem chave; preservar o caminho autenticado e verificar testes focados e XanoScript.
- [x] 8.5 Revisar o diff e dry-run seletivo dos dois endpoints técnicos antes de push autorizado; após publicação, verificar HTTP 401 e corpo exato sem chave nos dois, ausência de execução operacional pelo fluxo do código e novo dry-run sem mudanças. Não executar o caminho com chave válida sem credencial autorizada.

Evidência de 8.1/8.2: com as contas E2E fornecidas pelo usuário, sem gravar a senha ou tokens, as consultas somente leitura confirmaram 403 no contrato Técnico chamado pelo Gerente e nos dois GETs genéricos de interações chamados pelo Gerente; os dois GETs genéricos responderam 200 ao Técnico. Um chamado já existente com Loja diferente da Loja retornada por `/me` do Gerente respondeu 403 sem campos do chamado. A rota funcional de comentários do Gerente respondeu 200 com um comentário e DTO público restrito. Inicialmente, `status={}` em `gerente/chamados` e `tecnico/chamados`, e `loja_ids=1` proibido em `gerente/chamados`, responderam 400, embora a matriz e as specs exijam 422. Uma primeira sequência rápida recebeu 429; a segunda sequência espaçada concluiu os casos de autorização. A documentação XanoScript do Xano Developer MCP define `inputerror` como HTTP 400. A tentativa de `util.set_header` seguido de `return` retornou 200 com corpo de erro; foi reprovada e revertida localmente e no workspace. Em nova correção pontual, os dois GETs funcionais passaram a usar `util.set_header` com resposta normal, sem retorno antecipado. Após autorização específica, o dry-run seletivo mostrou exatamente dois UPDATEs, o push publicou dois documentos e o dry-run posterior retornou `No changes to push`. Requisições HTTP E2E espaçadas confirmaram **422 nos três casos inválidos**, com corpo JSON contendo apenas `code`, `message` e `payload`, sem dados de chamados; as duas listas válidas permaneceram **200** com `items` e `total`. Nenhuma senha, token ou corpo protegido foi registrado.

Evidência inicial de 8.4/8.5: chamadas HTTP sem header técnico aos dois endpoints retornaram **200** com o corpo público `{"error":"Não autenticado."}`; o POST foi enviado com payload vazio, e o guard local precede validação de presença, leitura e escrita. A spec consolidada exige 401 nos dois. Nenhum segredo técnico foi usado ou registrado.

Evidência local de 8.4: os dois guards mantêm a comparação estrita de chave, iniciam `$resultado` com o erro público, configuram o status 401 somente no ramo sem chave e executam a lógica operacional somente no `else` autenticado; a resposta normal usa `$resultado`. Xano Developer MCP validou 2 arquivos (0 inválidos); 39 testes focados de automações/heartbeat e a suíte completa (`447 passed`) passaram. O diff não altera campos, funções de heartbeat, persistência ou payload de sucesso.

Evidência runtime de 8.5: o dry-run seletivo do workspace 152692 mostrou exatamente `telemetria_equipamentos POST` e `verificar-falhas GET` como UPDATE. Após a autorização do usuário para corrigir essas rotas, o push interativo publicou 2 documentos; o dry-run posterior retornou `No changes to push`. GET e POST sem chave retornaram **401** com o corpo exato `{"error":"Não autenticado."}`; com chaves aleatórias inválidas, ambos também retornaram **401** e o mesmo corpo. O POST usou payload vazio. A ausência de acesso à lógica operacional foi verificada pela posição do ramo `else` no XanoScript validado, não por trace remoto; nenhuma credencial técnica válida foi usada e o caminho positivo não foi executado.

## 9. Desempenho das consultas

- [x] 9.1 Registrar contagem estrutural de consultas e, quando houver acesso autorizado, volume do conjunto e três tempos de resposta por rota funcional de monitoramento/fila; verificar evidência reproduzível e classificar se há problema real. Não editar XanoScript por esta task; qualquer otimização exige revisão de escopo.

Evidência de 9.1: `service_desk/listar_ativos_monitoramento.xs` contém uma `db.query ativos_referencia` e, para cada ativo, uma `db.query telemetria_equipamentos` e uma `db.query historico_disponibilidade_totens`: custo estrutural de **1 + 2N** consultas para N ativos, sem contar funções auxiliares. Com 15 Totens retornados, isso sugere 31 consultas nesse trecho, **não uma contagem observada no trace**. `service_desk/listar_chamados_tecnico.xs` contém ramos alternativos e `db.get` para validar filtros; ocorrências estáticas não equivalem a consultas executadas. Três GETs espaçados e autenticados por rota responderam 200 com conjuntos estáveis: monitoramento de 15 Totens em **317, 463 e 228 ms**; fila técnica de 18 chamados em **316, 829 e 390 ms**. O trace de consultas executadas não estava disponível nesta validação; a amostra pequena não demonstra problema persistente e não autoriza otimização. Nenhuma consulta foi editada.

## 10. Funcionalidades futuras

- [x] 10.1 Confirmar no backlog desta change que dashboards, administração de Lojas/Totens, aceite/rejeição e fechamento automático não são defeitos atuais nem entregas desta change; verificar que nenhum arquivo de implementação ou delta spec dessas capacidades entrou no diff.

Evidência de 10.1: `proposal.md` e `design.md` registram as capacidades futuras separadamente; `git diff --name-only` e as specs delta desta change não incluem implementação ou contrato novo de dashboards, administração de Lojas/Totens, aceite/rejeição ou fechamento automático.

## Validação transversal do Apply local

- **Passou:** suíte Python completa após a remoção do título da topbar (`446 passed`; um teste que exigia o título foi retirado), `reflex compile --dry`, `openspec validate melhorias-pontuais-pos-explore-geral --strict` e `git diff --check`.
- **Passou:** validação XanoScript dos dois GETs funcionais (2 válidos, 0 inválidos), dry-run seletivo com exatamente dois UPDATEs, push autorizado de 2 documentos e dry-run posterior sem mudanças.
- **Passou:** matriz HTTP negativa de autorização, escopo e 422, DTO público, e três medições runtime por rota; ver evidências dos itens 8 e 9.
- **Passou:** correção dos guards técnicos com HTTP 401 e corpo público exato em quatro casos negativos; dry-run posterior sem mudanças. Caminho com chave válida não executado por ausência de credencial técnica autorizada.
- **Não executado pelo agente:** conferência visual da versão final em navegador, pois o usuário assumiu essa verificação; trace de consultas não disponível nesta validação. A versão anterior da topbar foi reprovada visualmente pelo usuário e removida.
