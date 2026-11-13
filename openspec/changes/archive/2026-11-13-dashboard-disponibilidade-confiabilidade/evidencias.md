# Evidências do Apply (12/11/2026)

## Decisões e implementação

- Acesso exclusivo da Diretoria, período inicial de 30 dias civis e série diária, conforme decisão da responsável. As referências internas “2” e “D4” não integram este Apply.
- Online sem timestamp da telemetria referenciada fica fora da média de MTTR. Sua inconsistência entra no total, no dia civil de `detectado_em` e na Loja historicamente comprovada nesse instante. Transferência posterior não desloca a contagem; nenhum timestamp é estimado.
- O recorte por Loja inclui apenas Totens cujo vínculo histórico cruza o período consultado. A série usa dias civis em `America/Sao_Paulo`; totais e pontos diários calculam médias próprias.
- Dois defeitos encontrados na primeira execução nativa foram corrigidos antes do fechamento: durações omitidas dos objetos de eventos e série diária vazia. A rodada final nativa e o E2E publicado passaram.

## Validação

| Verificação | Estado | Evidência |
| --- | --- | --- |
| Testes Python e compilação Reflex (`make check`) | Passou | 671 testes passaram; compilação concluiu. Os 39 pulados incluem os quatro E2E desta change quando executados sem credenciais. |
| E2E HTTP desta change com conta de Diretoria | Passou | `tests/test_e2e_indicadores_diretoria.py`: 4 testes passaram. Login, catálogo e indicadores responderam 200; série com 30 dias e período confirmado; anônimo 401; período e Loja inválidos 400; recorte Loja+Totem 200 com filtros confirmados. Nenhuma credencial ou token foi registrada. |
| Tempo de resposta em dado real | Passou | Uma consulta filtrada Loja+Totem respondeu em 0,83 s. É uma medição pontual, não um compromisso de latência. |
| Testes nativos das funções de Indicadores | Passou | Xano CLI: 31 IDs de teste distintos executados, 0 falhas. Cobrem autorização por perfil com mocks, corte histórico, primeira telemetria, Offline aberto, transferência de Loja, ponderação `92/1.560 = 94,10%`, histórico inválido, MTTD 19 min, MTTR 51 min, recuperação antes de `t0`, inconsistência Online sem timestamp e total sem média das médias diárias. |
| Sintaxe XanoScript | Passou | Xano Developer MCP validou os nove arquivos afetados, 0 erros e 0 avisos. |
| Publicação seletiva e reconciliação | Passou | Antes do push, o dry-run mostrou somente dois índices de tabela, cinco funções e duas rotas desta change. Push autorizado publicou os nove documentos no workspace 152692. O dry-run seletivo final retornou `No changes to push`. |
| OpenSpec strict | Passou | `openspec validate dashboard-disponibilidade-confiabilidade --strict`. |
| Integridade do diff | Passou | `git diff --check`. |

## Validações não executadas

- Os 35 E2E anteriores que exigem contas dos quatro perfis permaneceram pulados por falta das demais credenciais. Os quatro E2E específicos da Diretoria foram executados separadamente e passaram.
- A resposta HTTP 403 com contas reais de Gerente, Técnico e Administrador não foi testada por falta dessas credenciais. A negação desses perfis foi verificada nos testes nativos das funções; os contratos usam `accessdenied` no Xano.

## Refinamento de apresentação

- A composição foi refeita com cabeçalho contextual, faixa compacta de filtros, quatro cartões executivos, gráfico principal e painel lateral de leitura, seguindo a hierarquia visual do `DESIGN.md` e da referência de Diretoria. O quarto cartão usa a contagem de Totens com observação já retornada pelo contrato; nenhuma métrica ou ação ilustrativa da imagem foi incorporada.
- Cartões, legenda, painel lateral e tabela explicam MTTD como tempo médio de detecção e MTTR como tempo médio de recuperação do Totem. O painel esclarece os marcos de telemetria e que o chamado não define a duração. Contagens de elegibilidade, inconsistência e tempo observado permanecem visíveis.
- Validação local do refinamento: 14 testes de `tests/test_indicadores_diretoria.py` passaram, compilação Reflex passou, OpenSpec strict passou e `git diff --check` passou.
- Inspeção visual no Browser: bloqueada por ferramenta nesta sessão (`browser access host is unavailable`).

## Atalhos de período

- “Últimos 30 dias” e “Hoje” aparecem no cabeçalho como controle segmentado; o período personalizado continua acessível no mesmo controle. Cada clique usa `America/Sao_Paulo`, preserva Loja e Totem e inicia uma única consulta. Nenhum temporizador ou atualização automática foi introduzido.
- `tests/test_indicadores_diretoria.py`: 15 testes passaram, incluindo limites de Hoje e 30 dias, preservação de Loja/Totem, uma consulta por clique e período personalizado. A compilação Reflex, o OpenSpec strict e `git diff --check` passaram.

## Visão horária de Hoje (13/11/2026)

- O atalho Hoje agora envia `[00h local, 00h do dia seguinte)` e `visao=hoje`; a apresentação indica 00h–23h59. O Xano captura `observado_ate` uma vez e limita os totais e a hora corrente a esse instante. A resposta mantém MTTD/MTTR do dia e acrescenta 24 posições de disponibilidade apenas nessa visão; horas futuras recebem percentual nulo e tempo observado zero. Os demais períodos seguem com série diária.
- Foram adicionados testes nativos sintéticos para período Hoje inválido, visão desconhecida, futuro fora de Hoje, hora parcial, Offline atravessando horas, transferência de Loja e histórico inválido localizado. **Não executados:** o Xano CLI executa testes da versão remota, e esta alteração ainda não foi publicada.
- `tests/test_indicadores_diretoria.py`: **19 passaram**, incluindo contrato tipado de 24 horas, rejeição de dado futuro, envio de `visao=hoje`, consulta ao clique e apresentação de 23h sem valor.
- `make check`: **676 passaram, 39 pulados**; Reflex compilou. `openspec validate dashboard-disponibilidade-confiabilidade --strict` e `git diff --check` passaram. O Xano Developer MCP validou os dois XanoScripts alterados, sem erros ou avisos.
- `xano workspace push --dry-run` seletivo: **passou** e apontou somente `UPDATE` da função `indicadores/consultar_disponibilidade_confiabilidade` e do `GET indicadores/disponibilidade-confiabilidade`. O pull remoto para `/tmp` confirmou que são os dois contratos existentes; nenhuma publicação foi feita nesta rodada.
- No fechamento da rodada local, os testes nativos e a publicação ainda não tinham ocorrido; o resultado da rodada publicada consta abaixo. A inspeção visual no Chrome permaneceu **bloqueada por ferramenta** (`browser access host is unavailable`).

### Publicação autorizada e verificação posterior

- A responsável autorizou a publicação em 13/11/2026. O dry-run imediatamente anterior listou somente a função e o endpoint GET desta change. O push seletivo publicou **2 documentos** no workspace 152692, e o dry-run seletivo posterior retornou `No changes to push`.
- Oito testes nativos novos da função publicada passaram: Hoje sem eventos, conjunto conhecido com hora parcial e Offline atravessando horas, transferência de Loja, histórico inválido localizado e quatro rejeições de entrada. Foram executados pelo Xano CLI, sem falha.
- A verificação HTTP autenticada e a medição real de latência/volume da visão Hoje continuam **não executadas**: a sessão não possui credenciais de teste da Diretoria. A inspeção visual no Chrome segue **bloqueada por ferramenta**.

## Ajuste visual dos gráficos (13/11/2026)

- O gráfico diário passou de linhas sem área para curvas com preenchimento suave, mantendo lacunas sem eventos sem interpolação. A legenda fixa agora distingue MTTD como tempo até detectar e MTTR como tempo até recuperar; os nomes e a unidade também aparecem no balão.
- Foi removida a largura mínima de 36 rem e a rolagem horizontal do gráfico diário. O balão passou a ficar limitado à área do gráfico, sem animação de posição; a visão horária usa o mesmo acabamento de área e balão.
- `make check`: **690 passaram, 39 pulados**, e Reflex compilou. OpenSpec strict e `git diff --check` passaram. O componente gerado usa `AreaChart`, preenchimento translúcido, `allowEscapeViewBox` falso e largura responsiva.
- O link direto do Figma e o Chrome não abriram nesta sessão; a referência visual consultada foi `docs/design/references/diretoria-dashboard.png`. A interação de hover na página renderizada permanece **bloqueada por ferramenta**.

## Refinamento da listagem diária (13/11/2026)

- A tabela passou a separar data, média de MTTD, detecções, média de MTTR e recuperações. Inconsistências aparecem somente quando existem, com contagem e rótulo textual; dias sem média permanecem explícitos. A ordem continua da data mais recente à mais antiga.
- Cabeçalho, divisórias e densidade das linhas foram aproximados da listagem da referência visual. Foi removida a altura máxima com rolagem vertical interna; a página acompanha todas as datas do período. Nenhum campo ou ação de chamado da imagem foi introduzido sem contrato.
- `make check`: **690 passaram, 39 pulados**, com compilação Reflex concluída. OpenSpec strict da change e `git diff --check` passaram. A inspeção visual renderizada segue bloqueada pela integração de navegador nesta sessão.

## Separação em abas (13/11/2026)

- A seção de disponibilidade foi colocada na aba própria da mesma rota, imediatamente abaixo do breadcrumb. Apenas os filtros de Loja e Totem, os três indicadores, o gráfico e o histórico diário aparecem nessa aba; a visão de Chamados/SLA ocupa a outra aba. O atalho de período permanece compartilhado.
- A troca de aba conserva os filtros e os resultados já consultados. A validação automatizada e a limitação da inspeção visual constam nas evidências de `dashboard-operacao-sla`.

## Fechamento para Archive (13/11/2026)

- A responsável autorizou arquivar esta change com as tarefas 6.4 e 6.5 ainda abertas, mantendo explícitas as verificações HTTP autenticadas e a medição real da visão Hoje não executadas por falta de credenciais de teste. A inspeção visual renderizada permaneceu bloqueada pela ferramenta de navegador. Nenhuma dessas verificações foi marcada como aprovada.
- Nesta rodada, `make check` passou com **691 testes e 39 pulados**, incluindo compilação Reflex. OpenSpec strict e `git diff --check` passaram. O Xano Developer MCP validou novamente a função e o endpoint da consulta, sem erro ou aviso.
- O dry-run seletivo atualizado comparou 16 documentos da área de indicadores e tabelas relacionadas no workspace 152692 e retornou `No changes to push`. Os testes nativos publicados e a publicação seletiva anterior constam acima; não houve novo push nesta rodada.
