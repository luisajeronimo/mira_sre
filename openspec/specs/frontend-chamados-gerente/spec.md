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
O sistema DEVE (MUST) apresentar ao Gerente autenticado uma listagem básica construída a partir de `GET /gerente/chamados`, incluindo para cada item identificação, título, status, prioridade, origem, abertura, ativo e categoria. A interface NÃO DEVE (MUST NOT) restringir a lista ao usuário solicitante nem implementar filtros avançados nesta capacidade.

#### Scenario: Listagem carregada
- **WHEN** o Gerente acessa sua página inicial com sessão revalidada e o Xano retorna chamados
- **THEN** o Reflex apresenta somente os itens fornecidos pelo contrato da Loja e permite abrir o detalhe de cada item

#### Scenario: Loja sem chamados
- **WHEN** o contrato retorna uma coleção vazia
- **THEN** o Reflex apresenta um estado vazio explícito e mantém disponível a ação de abrir chamado

#### Scenario: Chamado legado com dado ausente
- **WHEN** a lista contém um chamado legado com origem, descrição, abertura ou SLA aplicado nulo
- **THEN** o Reflex representa o dado como não informado sem inferir ou fabricar seu valor

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

#### Scenario: Última atualização legada não informada
- **WHEN** o detalhe retorna `ultima_atualizacao_em` nulo
- **THEN** o Reflex apresenta `Não informado`, sem substituir o valor por `created_at` ou outra data aproximada

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
O sistema DEVE (MUST) apresentar estados explícitos de carregamento, vazio, sucesso e erro nas consultas e na criação. Falhas 401 DEVEM (MUST) encerrar a sessão conforme a capacidade consolidada; falhas 403 DEVEM (MUST) preservar a sessão e informar negação; falhas 404 DEVEM (MUST) informar recurso não encontrado; falhas 422 ou respostas incompatíveis DEVEM (MUST) ser tratadas como contrato inválido; e timeout, conexão ou 5xx DEVEM (MUST) ser tratados como indisponibilidade temporária.

#### Scenario: Sessão expirada durante operação
- **WHEN** um contrato funcional responde 401
- **THEN** o Reflex limpa a sessão local e redireciona para `/login` sem tentar renovar o token

#### Scenario: Operação não autorizada
- **WHEN** um contrato funcional responde 403
- **THEN** o Reflex mantém a sessão autenticada e apresenta a negação sem exibir os dados solicitados

#### Scenario: Recurso não encontrado
- **WHEN** a consulta de detalhe responde 404
- **THEN** o Reflex informa que o chamado não foi encontrado sem encerrar a sessão

#### Scenario: Entrada ou resposta incompatível
- **WHEN** a criação responde 422 ou uma resposta não corresponde ao formato funcional esperado
- **THEN** o Reflex apresenta erro de validação ou contrato sem publicar dados inconsistentes

#### Scenario: Serviço indisponível
- **WHEN** ocorre timeout, falha de conexão ou resposta 5xx
- **THEN** o Reflex informa indisponibilidade temporária e oferece nova tentativa segura quando aplicável

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
