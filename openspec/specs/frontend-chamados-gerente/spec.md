## Purpose

Definir a jornada Reflex autenticada pela qual o Gerente consulta os chamados de sua Loja, abre um chamado manual e visualiza seu detalhe usando exclusivamente os contratos funcionais do Service Desk.

## Requirements

### Requirement: Reflex usa uma base dedicada ao Service Desk
O sistema DEVE (MUST) configurar o consumo do grupo `mira-service-desk` por uma URL base específica de Service Desk mantida fora do código. Essa base DEVE (MUST) ser independente de `XANO_AUTH_BASE_URL` e de `XANO_BASE_URL`, reutilizar o timeout configurado e enviar o token backend-only da sessão nas operações autenticadas.

#### Scenario: Requisição funcional autenticada
- **WHEN** o Reflex chama um contrato de chamados durante uma sessão válida
- **THEN** a requisição usa a base dedicada do Service Desk e envia o token no formato consolidado sem expô-lo ao navegador, à URL ou à interface

#### Scenario: Base ausente
- **WHEN** a URL base do Service Desk não está configurada
- **THEN** o Reflex falha explicitamente como configuração inválida sem tentar usar a base de autenticação ou um grupo interno diferente

#### Scenario: Bases de outros grupos
- **WHEN** `XANO_AUTH_BASE_URL` e `XANO_BASE_URL` apontam para seus respectivos grupos
- **THEN** os contratos de chamados continuam usando somente a base dedicada de `mira-service-desk`

### Requirement: Gerente possui listagem básica dos chamados da Loja
O sistema DEVE (MUST) apresentar ao Gerente autenticado uma tabela construída a partir de `GET /gerente/chamados`, com número, título e ocorrência resumida, status, prioridade, Totem, Categoria, abertura e última atualização. A ocorrência DEVE (MUST) ser derivada no Reflex dos primeiros 80 caracteres de `descricao`, com `…` somente quando houver truncamento; ela não possui ordenação independente.

#### Scenario: Listagem carregada
- **WHEN** o Gerente acessa sua página inicial com sessão revalidada e o Xano retorna chamados
- **THEN** o Reflex apresenta a tabela com somente os itens fornecidos pelo contrato da Loja e permite abrir o detalhe de cada item

#### Scenario: Loja sem chamados
- **WHEN** o contrato retorna uma coleção vazia
- **THEN** o Reflex apresenta um estado vazio explícito e mantém disponível a ação de criar chamado

#### Scenario: Chamado legado com dado ausente
- **WHEN** o contrato da lista retorna um timestamp funcional ausente em registro histórico
- **THEN** o Reflex não infere `created_at` nem apresenta data aproximada; a resposta é incompatível com a jornada operacional aprovada

#### Scenario: Datas funcionais da lista
- **WHEN** a lista contém chamado válido
- **THEN** o Reflex apresenta `criado_em` e `ultima_atualizacao_em` recebidos do contrato, sem fallback para `created_at` ou outra data técnica

#### Scenario: Ocorrência com até 80 caracteres
- **WHEN** a descrição possui no máximo 80 caracteres
- **THEN** o Reflex a apresenta integralmente como ocorrência sem reticências

#### Scenario: Ocorrência truncada
- **WHEN** a descrição possui mais de 80 caracteres
- **THEN** o Reflex apresenta somente os primeiros 80 caracteres seguidos de `…`

### Requirement: Gerente possui formulário de abertura manual
O sistema DEVE (MUST) oferecer ao Gerente autenticado um formulário com seleção de ativo, seleção de categoria, seleção de prioridade e campos de título e descrição. As opções de ativo e categoria DEVEM (MUST) vir respectivamente de `GET /gerente/ativos` e `GET /gerente/categorias`, e as únicas prioridades apresentadas DEVEM (MUST) ser `Baixa`, `Média`, `Alta` e `Urgente`.

#### Scenario: Formulário carregado
- **WHEN** o Gerente acessa a abertura manual com sessão revalidada e os catálogos respondem com sucesso
- **THEN** o Reflex apresenta somente os ativos e categorias retornados pelo Xano e os cinco dados funcionais exigidos

#### Scenario: Envio válido
- **WHEN** o Gerente envia ativo, categoria, prioridade, título e descrição preenchidos
- **THEN** o Reflex transmite somente esses cinco dados a `POST /gerente/chamados`, apresenta a confirmação de sucesso e permite consultar o detalhe retornado

#### Scenario: Envio em processamento
- **WHEN** uma submissão ainda está sendo processada
- **THEN** o Reflex indica carregamento e impede o reenvio concorrente do mesmo formulário

#### Scenario: Nova submissão posterior
- **WHEN** o Gerente conclui uma abertura e depois submete novamente um formulário válido
- **THEN** o Reflex envia uma nova requisição sem aplicar deduplicação local

### Requirement: Gerente pode consultar o detalhe básico do chamado
O sistema DEVE (MUST) fornecer uma página de detalhe que consulte `GET /gerente/chamados/{chamados_id}` e apresente identificação, título, descrição, status, prioridade, origem, abertura, última atualização, SLA aplicado, ativo, categoria, solicitante e técnico quando houver. A página DEVE (MUST) consultar e apresentar separadamente os comentários públicos autorizados do chamado, sem oferecer edição do chamado, mudança de status, atribuição, diagnóstico, solução ou resolução nesta capacidade.

#### Scenario: Detalhe carregado
- **WHEN** o Xano retorna um chamado autorizado da Loja
- **THEN** o Reflex apresenta seus dados funcionais, incluindo ativo, categoria, solicitante, técnico quando houver e última atualização, sem usar `created_at` como abertura

#### Scenario: Técnico ainda não atribuído
- **WHEN** o detalhe retorna técnico nulo
- **THEN** o Reflex apresenta a ausência de atribuição sem oferecer ação para atribuir ou assumir

#### Scenario: Comentários públicos carregados
- **WHEN** a consulta de comentários públicos do chamado é aceita
- **THEN** o Reflex apresenta somente os comentários retornados, do mais recente ao mais antigo

### Requirement: Reflex permite comentar chamado autorizado com rascunho descartável
O Reflex DEVE (MUST) oferecer ao Gerente autenticado envio de comentário para o contrato funcional específico e descarte exclusivamente local do rascunho. A interface NÃO DEVE (MUST NOT) enviar autor, Loja, visibilidade, timestamp ou status como dados sob controle do cliente.

#### Scenario: Envio de comentário público
- **WHEN** o Gerente envia conteúdo de comentário não vazio em chamado não terminal autorizado
- **THEN** o Reflex chama o contrato específico, apresenta o comentário retornado e atualiza a visualização sem inventar dados locais

#### Scenario: Descarte do rascunho
- **WHEN** o Gerente descarta comentário ainda não enviado
- **THEN** o Reflex limpa somente o conteúdo local sem executar requisição nem alterar o chamado

#### Scenario: Chamado terminal
- **WHEN** o detalhe informa status `Encerrado` ou `Cancelado`
- **THEN** o Reflex mantém os comentários públicos visíveis e não oferece envio de novo comentário

### Requirement: Jornada possui estados seguros de carregamento e falha
O sistema DEVE (MUST) concluir o estado de carregamento da lista em sucesso,
erro, cancelamento lógico ou redirecionamento. Uma nova ordenação ou filtro
enquanto houver consulta em andamento NÃO DEVE (MUST NOT) abrir uma tempestade
de requisições equivalentes nem permitir que resposta obsoleta sobrescreva uma
consulta mais recente. Uma intenção posterior DEVE (MUST) ser coalescida em no
m máximo uma nova consulta após sucesso da atual.

#### Scenario: Consulta concorrente de lista
- **WHEN** o Gerente dispara duas interações de lista antes da primeira resposta
- **THEN** o State mantém somente uma consulta em andamento e, após sucesso,
  executa no máximo uma nova consulta usando os critérios atuais

#### Scenario: Sessão expirada durante operação
- **WHEN** um contrato funcional responde 401
- **THEN** o Reflex limpa a sessão local e redireciona para `/login` sem
  tentar renovar o token

#### Scenario: Operação não autorizada
- **WHEN** um contrato funcional responde 403
- **THEN** o Reflex mantém a sessão autenticada e apresenta a negação sem
  exibir os dados solicitados

#### Scenario: Recurso não encontrado
- **WHEN** a consulta de detalhe responde 404
- **THEN** o Reflex informa que o chamado não foi encontrado sem encerrar a
  sessão

#### Scenario: Entrada ou resposta incompatível
- **WHEN** a criação responde 422 ou uma resposta não corresponde ao formato
  funcional esperado
- **THEN** o Reflex apresenta erro de validação ou contrato sem publicar dados
  inconsistentes

#### Scenario: Serviço indisponível
- **WHEN** ocorre timeout, falha de conexão ou resposta 5xx
- **THEN** o Reflex informa indisponibilidade temporária e oferece nova
  tentativa segura quando aplicável

#### Scenario: Falha transitória recuperável
- **WHEN** uma consulta de lista falha por timeout, conexão, 5xx ou limite 429
- **THEN** o loading termina, a sessão confirmada permanece válida, a mensagem
  é sanitizada e uma nova ação explícita consegue consultar novamente

#### Scenario: Limite de requisições
- **WHEN** o Xano responde 429 com ou sem `Retry-After`
- **THEN** o cliente classifica a resposta como indisponibilidade transitória,
  não limpa a sessão e não inicia retry agressivo

#### Scenario: Catálogo secundário indisponível
- **WHEN** `GET /gerente/ativos` falha durante a carga inicial mas
  `GET /gerente/chamados` retorna sucesso
- **THEN** os chamados e contadores permanecem visíveis, sem invalidar a sessão

#### Scenario: Falha real de autenticação
- **WHEN** uma consulta funcional responde 401
- **THEN** o State limpa a sessão e redireciona para login, preservando a
  distinção entre autenticação e indisponibilidade

### Requirement: Autorização permanece no Xano
O frontend DEVE (MUST) reutilizar a sessão e a identidade consolidadas para navegação e apresentação, mas NÃO DEVE (MUST NOT) usar `lojas_id`, perfil oculto, lista filtrada ou proteção visual como prova de autorização. Toda consulta e criação DEVE (MUST) ser autorizada novamente pelo Xano.

#### Scenario: Identificador manipulado no navegador
- **WHEN** um usuário altera diretamente uma rota ou identificador de chamado ou ativo
- **THEN** o Reflex envia a operação autenticada e respeita a decisão do Xano sem conceder acesso localmente

### Requirement: Detalhe do Gerente apresenta criador de sistema sem ampliar a listagem
O Reflex DEVE (MUST) mostrar no detalhe existente do chamado para Gerente
`Criado por: Bot de Fiscalização` quando o contrato retornar
`criador_sistema = "bot_fiscalizacao"`, e manter a origem apresentada
separadamente como `Origem: Automático`. Quando a autoria de sistema for nula,
a interface NÃO DEVE (MUST NOT) inferir ou apresentar o Bot. Esta capacidade
NÃO DEVE (MUST NOT) criar uma coluna de autoria na listagem, redesenhar a tela
ou alterar a jornada de abertura manual.

#### Scenario: Detalhe de chamado automático atual da Loja
- **WHEN** um Gerente autorizado abre o detalhe de um chamado de heartbeat com
  `origem = "automatico"` e `criador_sistema = "bot_fiscalizacao"`
- **THEN** a interface mostra `Criado por: Bot de Fiscalização` e
  `Origem: Automático` como informações distintas

#### Scenario: Detalhe de chamado manual
- **WHEN** um Gerente autorizado abre o detalhe de chamado manual com
  `criador_sistema = null`
- **THEN** a interface mantém a apresentação do chamado manual e não exibe o
  Bot como criador

#### Scenario: Detalhe de chamado legado
- **WHEN** um Gerente autorizado abre o detalhe de chamado sem autoria de
  sistema persistida
- **THEN** a interface mantém o registro legível e não deduz autoria a partir
  da origem ou de outro dado histórico

### Requirement: Reflex controla filtros, ordenação e contadores da lista
O State DEVE (MUST) reutilizar o catálogo de ativos já carregado ao aplicar
ordenação, filtros ou limpeza. Essas interações DEVEM (MUST) consultar o
endpoint de chamados e NÃO DEVEM (MUST NOT) repetir consultas auxiliares
desnecessárias que possam gerar request storm.

#### Scenario: Ordenações consecutivas
- **WHEN** o Gerente alterna a ordenação várias vezes após o catálogo de ativos
  ter sido carregado
- **THEN** cada consulta de lista mantém a sessão e não dispara nova consulta
  de ativos

#### Scenario: Aplicação e limpeza de filtros
- **WHEN** o Gerente aplica ou limpa critérios de filtro
- **THEN** o State consulta novamente a lista, preserva a ordenação
  selecionada e apresenta os critérios efetivamente aplicados

#### Scenario: Ordenação de coluna
- **WHEN** o Gerente escolhe uma coluna ordenável e direção
- **THEN** o Reflex solicita a ordenação autorizada ao backend, sem ordenar
  somente a coleção local

#### Scenario: Falha de consulta não encerra sessão confirmada
- **WHEN** uma consulta de lista, filtro ou ordenação falha por
  indisponibilidade, timeout ou contrato incompatível
- **THEN** o Reflex apresenta erro sanitizado de serviço e preserva a
  identidade já confirmada; somente falha real de autenticação pode
  redirecionar ao login

#### Scenario: Contadores da consulta atual
- **WHEN** a lista responde a uma consulta com ou sem filtros
- **THEN** a interface apresenta o total filtrado e o tamanho atual de
  `items`

### Requirement: Formulário de abertura possui ações locais distintas
O formulário de abertura DEVE (MUST) oferecer Salvar, Limpar, Descartar e Voltar para a lista. Limpar remove somente o rascunho e permanece na tela; Descartar abandona o rascunho e retorna à lista; Voltar somente navega; nenhuma dessas três ações DEVE (MUST NOT) criar, cancelar, excluir ou alterar chamado.

#### Scenario: Limpar formulário
- **WHEN** o Gerente escolhe Limpar antes de salvar
- **THEN** os campos editáveis retornam ao estado inicial sem requisição de criação

#### Scenario: Descartar formulário
- **WHEN** o Gerente escolhe Descartar antes de salvar
- **THEN** o Reflex abandona o rascunho e retorna à lista sem requisição de criação

#### Scenario: Voltar para lista
- **WHEN** o Gerente escolhe Voltar para a lista
- **THEN** o Reflex navega sem executar operação backend sobre o rascunho

### Requirement: Sucesso de abertura permanece observável
Após criação manual aceita, o Reflex DEVE (MUST) apresentar confirmação de sucesso por tempo suficiente para ser percebida antes ou durante a navegação prevista, sem criar contrato backend apenas para mensagem visual.

#### Scenario: Criação bem-sucedida
- **WHEN** `POST /gerente/chamados` retorna sucesso
- **THEN** o Gerente percebe confirmação de abertura e continua podendo acessar o detalhe criado conforme a jornada existente
