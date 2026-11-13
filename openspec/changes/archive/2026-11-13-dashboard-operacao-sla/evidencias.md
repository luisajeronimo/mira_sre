# Evidências do Apply — 13/11/2026

## Implementação local

- `GET /indicadores/operacao-sla` exige autenticação e Diretoria no Xano, recebe período, Loja, Categoria e a visão Hoje explícita. `GET /indicadores/operacao-sla/filtros` devolve Loja e Categoria, inclusive Categoria histórica inativa, sem dados brutos de chamados. Nenhum contrato recebe Prioridade.
- A função executiva consulta chamados persistidos e resolve a Loja comprovada no `criado_em`. A volumetria conta aberturas no período pelo status atual; conformidade usa a entrada no estado de parada vigente e o consumo individual consolidado; risco usa todos os chamados ainda em contagem no instante capturado, mesmo os anteriores ao período. Cancelados, não calculáveis e status não canônicos têm contagens próprias. O resumo dos consumos é feito no Xano, sem gravação de agregados.
- A página da Diretoria apresenta os três painéis e os escopos de período, Loja, Totem e Categoria. O cliente e o State validam a resposta, exibem valores recebidos e descartam resposta tardia. A seleção Hoje é o dia civil completo; os fatos de período param no instante observado da consulta.
- Dois índices de leitura foram adicionados para Categoria de chamado e transições por chamado/tipo/data/ID.

## Validações

| Verificação | Estado | Evidência |
| --- | --- | --- |
| Testes Python e compilação Reflex | Passou | `make check`: 690 passaram, 39 pulados; compilação Reflex concluiu. |
| Contrato e State de operação | Passou | `tests/test_indicadores_operacao.py`: contrato estrito, filtros, ausência de Prioridade/Totem no request, apresentação de agregados, falha e resposta tardia. |
| XanoScript | Passou | Xano Developer MCP validou 7 arquivos afetados, 0 erros e 0 avisos. |
| OpenSpec strict | Passou | `openspec validate dashboard-operacao-sla --strict`. |
| Integridade do diff | Passou | `git diff --check`. |
| Dry-run seletivo | Passou | Workspace 152692: 2 tabelas com somente índices novos, 3 funções novas e 2 endpoints novos; nenhuma remoção ou registro incluído. |
| Testes nativos Xano desta change | Passou | 27 testes distintos das três funções novas passaram na versão publicada. Cobrem autorização, entradas inválidas, Loja histórica e sem vínculo, volume por status, conformidade, risco e conjunto 8/10 = 80%. Os dois testes finais, `operacao sem vinculo global` e `operacao sem vinculo filtrada`, passaram após a última publicação. Os limites 70/90/100% são cobertos pelos testes nativos da função consolidada de consumo. |
| HTTP anônimo | Passou | Os dois endpoints novos responderam 401 sem sessão; não devolveram dados de chamados. |
| HTTP autenticado, volume e latência reais | Bloqueado por credencial | Não há credenciais de teste autorizadas da Diretoria ou dos outros perfis nesta sessão. Não houve medição de volume/latência nem demonstração HTTP com dados persistidos. Testes nativos com conjunto conhecido não substituem essa verificação. |
| Inspeção visual renderizada | Bloqueado por ferramenta | A integração com Chrome informou `browser access host is unavailable`. Compilação não substitui inspeção visual. |

## Publicação

- A responsável autorizou o Apply e a publicação após revisar o dry-run. Os sete documentos foram publicados seletivamente no workspace 152692: dois esquemas de tabela com somente índices adicionais, três funções e dois endpoints. Não foram incluídos registros, remoções ou sincronização integral.
- As funções de consulta e catálogo receberam uma atualização seletiva dos testes nativos, e a consulta recebeu outra para os dois cenários sem vínculo histórico. Cada push foi precedido de validação XanoScript e dry-run do recurso afetado. O dry-run seletivo final dos sete documentos retornou `No changes to push`.
- Permanecem pendentes somente as verificações HTTP autenticadas, de volume/latência reais e da página renderizada. As duas changes continuam ativas para Archive posterior pela responsável.

## Refinamento visual de Chamados e SLA (13/11/2026)

- A seção foi reorganizada em resumos de volume e conformidade, distribuição em rosca por status e termômetro de risco em quatro faixas. A legenda da rosca mostra nomes e contagens, inclusive status não classificados quando presentes; fatias de quantidade zero são omitidas apenas da visualização. Os agregados continuam vindo do Xano.
- A conformidade apresenta o percentual devolvido pelo backend, a relação de chamados dentro do SLA, uma barra proporcional a esse mesmo valor e contagens separadas de Cancelados e não calculáveis. Sem elegíveis, mostra ausência de percentual e mensagem própria. O risco mantém instante da consulta e explicita que inclui chamados antigos ainda em contagem.
- A referência visual consultada foi `docs/design/references/diretoria-dashboard.png`. O nó do Figma não abriu nesta sessão; a inspeção da página renderizada continua bloqueada pela integração de navegador.
- Após o refinamento, `make check` passou com **690 testes e 39 pulados** e a compilação Reflex concluiu. `openspec validate dashboard-operacao-sla --strict` e `git diff --check` passaram.

## Abas da página executiva (13/11/2026)

- A rota única passou a oferecer duas abas logo abaixo do breadcrumb: Disponibilidade e Chamados e SLA. Cada aba apresenta somente seu título, filtro específico, estado de erro e painéis. O período e a Loja permanecem compartilhados; Totem aparece apenas em Disponibilidade e Categoria apenas em Chamados e SLA.
- A troca de aba mantém os filtros e os resultados já consultados, sem chamada adicional, e fecha o calendário personalizado aberto. `tests/test_indicadores_diretoria.py` verifica a preservação dos filtros e a recusa de valor de aba inválido.
- `make check`: **691 passaram, 39 pulados**, e Reflex compilou. A validação visual renderizada permanece bloqueada pela integração de navegador nesta sessão.

## Fechamento para Archive (13/11/2026)

- A responsável autorizou arquivar esta change com as tarefas 5.1 e 5.2 ainda abertas, mantendo explícitas as verificações HTTP autenticadas dos perfis e a medição real de volume/latência não executadas por falta de credenciais de teste. A inspeção visual renderizada permaneceu bloqueada pela ferramenta de navegador. Nenhuma dessas verificações foi marcada como aprovada.
- Nesta rodada, `make check` passou com **691 testes e 39 pulados**, incluindo compilação Reflex. OpenSpec strict e `git diff --check` passaram. O Xano Developer MCP validou novamente a função e o endpoint da consulta, sem erro ou aviso.
- O dry-run seletivo atualizado comparou 16 documentos da área de indicadores e tabelas relacionadas no workspace 152692 e retornou `No changes to push`. Os testes nativos publicados e a publicação seletiva anterior constam acima; não houve novo push nesta rodada.
