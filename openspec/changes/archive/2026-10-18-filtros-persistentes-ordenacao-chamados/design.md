# Design: filtros persistentes e ordenação de chamados

## Abordagem

O Xano guarda uma preferência canônica por `usuarios_id` autenticado e escopo
da fila: `todos` ou `atribuidos_a_mim`. O segundo escopo é válido somente para
Técnico. O registro contém apenas os filtros aplicados e `ordenar_por` /
`direcao`; não contém token, perfil, dados da fila nem a seleção atual do
escopo.

O Reflex mantém rascunhos locais. No login, seleciona sempre `Todos`, obtém a
preferência daquele escopo e só então carrega a lista. Ao trocar de escopo, o
Reflex carrega a preferência daquele escopo. Aplicar, limpar e ordenar formam
uma preferência candidata completa. Primeiro consulta a lista candidata
validada; somente se ela for bem-sucedida salva a preferência canônica. O
State e a lista só substituem os valores confirmados depois das duas etapas.
Falha de consulta não persiste; falha de save não confirma o resultado
candidato. Não há compensação de save, pois a política é last-valid-write-wins.

## Contratos

Uma consulta e um save específicos de preferências usam exclusivamente a
identidade autenticada no Xano; o cliente não envia `usuarios_id`. A ausência
de registro equivale aos padrões: filtros vazios, `numero` em `DESC`.

`GET /tecnico/chamados` recebe também `responsavel_id`, `ordenar_por` e `direcao`.
O filtro de responsável usa exclusivamente o identificador de um Técnico;
o valor `0` representa `Não atribuído`. O catálogo de Técnicos já disponível
no State é reutilizado pela interface, sem introduzir uma nova fonte de dados.
O Xano aceita
somente `numero`, `titulo`, `status`, `prioridade`, `totem`, `categoria`,
`responsavel`, `criado_em` e `ultima_atualizacao_em`; `numero` e os timestamps funcionais são
numéricos e os demais usam comparação textual sem distinção de caixa. Os dois
timestamps ordenam cronologicamente em `ASC` ou `DESC`. O Xano mapeia
internamente `numero` para `chamados.id` e usa `id` como desempate estável na
direção escolhida. A seleção inicial e persistida é `numero` em `DESC`; uma
nova coluna inicia em `ASC` e novo clique alterna a direção. `id` não é
parâmetro público nem coluna ordenável adicional.

`responsavel` ordena pelo nome do Técnico sem distinguir caixa. Chamados sem
responsável ficam sempre após qualquer responsável nomeado, tanto em `ASC`
quanto em `DESC`; `chamados.id` desempata na mesma direção solicitada.

Status recebido em filtro ou preferência é comparado sem distinção de caixa e
normalizado para o literal canônico antes de consulta e persistência. Prioridade
é validada contra os valores canônicos existentes.

## Segurança e limites

O Xano valida perfil, escopo, filtros e ordenação antes de ler ou escrever. O
registro só pode ser lido ou alterado pelo seu usuário autenticado. Cada save
válido substitui integralmente a preferência do mesmo usuário+escopo
(`last-valid-write-wins`). A seleção `Atribuídos a mim` continua protegida no
backend e não é persistida como seleção entre sessões.

Literal de escopo desconhecido ou combinação contraditória de escopo recebe
HTTP 422. Escopo enumerado, mas proibido ao perfil, recebe HTTP 403; isso inclui
Diretoria/Admin em `atribuidos_a_mim` e Gerente em qualquer contrato global.

O desenho usa tabela, funções e endpoints Xano compatíveis com o plano Free;
a sintaxe de chave única usuário+escopo será confirmada no Xano Developer MCP
antes do Apply. Não há migração, backfill ou alteração de registros de
chamados.
