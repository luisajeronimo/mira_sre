# Spec Delta

## ADDED Requirements

### Requirement: Gerente ou solicitante rejeita solução pelo detalhe do chamado
O Reflex DEVE (MUST) apresentar no detalhe do Gerente a ação específica "Rejeitar solução" somente quando o status do detalhe for `Resolvido`. Como o detalhe só é retornado para chamado da Loja do Gerente, a ação é oferecida a esse Gerente, sendo ou não o solicitante, inclusive em chamado automático. A interface DEVE (MUST) exigir justificativa não vazia após trim antes do envio, transmitir somente a justificativa e o `ultima_atualizacao_em` do detalhe confirmado, e NÃO DEVE (MUST NOT) enviar autor, Loja, status, visibilidade ou timestamp funcional. A condição visual e a validação local NÃO DEVEM (MUST NOT) ser tratadas como autorização. A interface DEVE (MUST) apresentar carregamento, sucesso e erro sem simular a transição.

#### Scenario: Rejeição confirmada
- **WHEN** o Gerente envia justificativa válida para chamado `Resolvido` e o Xano confirma
- **THEN** o Reflex apresenta sucesso, atualiza o detalhe com o status `Reaberto` retornado pelo backend, apresenta a justificativa entre os comentários e o evento no histórico, e limpa a justificativa

#### Scenario: Justificativa vazia não é enviada
- **WHEN** a justificativa está vazia ou contém somente espaços
- **THEN** o Reflex informa a validação e não chama o contrato; o Xano continua aplicando a mesma validação a chamadas diretas

#### Scenario: Ação indisponível fora de Resolvido
- **WHEN** o detalhe apresenta qualquer status diferente de `Resolvido`
- **THEN** o Reflex não oferece a ação de rejeição

#### Scenario: Rejeição em andamento
- **WHEN** a solicitação de rejeição está em andamento
- **THEN** o Reflex impede envio duplicado e informa o carregamento

#### Scenario: Rejeição recusada pelo Xano
- **WHEN** o Xano rejeita por autorização, justificativa, status ou detalhe desatualizado
- **THEN** o Reflex não apresenta sucesso, não altera o status localmente, preserva a justificativa e apresenta erro sanitizado; em conflito, informa a atualização e recarrega o detalhe

### Requirement: Detalhe do Gerente apresenta histórico público de status
O Reflex DEVE (MUST) consultar o contrato de histórico público de status e apresentá-lo em seção própria, distinta dos comentários públicos, com status anterior, status resultante, data e autor, do mais recente ao mais antigo. O autor DEVE (MUST) ser apresentado como nome e perfil retornados pelo Xano, somente pelo nome quando `perfil` for nulo, como `Sistema` quando o backend assim o identificar, ou como autor não informado quando `autor` for nulo, sem que a interface infira autoria ou perfil. A interface NÃO DEVE (MUST NOT) consumir a timeline técnica nem combinar comentários e eventos em uma coleção derivada no cliente. A falha do histórico NÃO DEVE (MUST NOT) impedir a apresentação do detalhe nem dos comentários.

#### Scenario: Histórico carregado
- **WHEN** o contrato retorna eventos
- **THEN** o Reflex apresenta as transições na seção de histórico, separadas dos comentários

#### Scenario: Autor no histórico
- **WHEN** o histórico contém evento de autor humano e evento automático
- **THEN** o Reflex apresenta nome e perfil para o primeiro e `Sistema` para o segundo

#### Scenario: Autor sem perfil reconhecido
- **WHEN** o evento retorna `autor` com nome e `perfil` nulo
- **THEN** o Reflex apresenta somente o nome, sem rotular como `Sistema`

#### Scenario: Histórico vazio
- **WHEN** o contrato retorna lista vazia
- **THEN** o Reflex informa que não há transições registradas e que eventos anteriores à implantação do histórico não são exibidos

#### Scenario: Falha do histórico
- **WHEN** a consulta do histórico falha por motivo diferente de autenticação
- **THEN** o Reflex apresenta erro sanitizado na seção de histórico e mantém detalhe e comentários

### Requirement: Solicitante possui interface própria de acompanhamento e rejeição
O Reflex DEVE (MUST) oferecer ao usuário autenticado uma interface própria com a lista e o detalhe dos chamados em que ele é o solicitante associado, construída exclusivamente pelos contratos do solicitante, independentemente de sua Loja atual. A lista DEVE (MUST) estar em `/chamados/solicitados` e o detalhe em `/chamados/solicitados/[chamado_id]`, sem alterar as rotas canônicas existentes. O item de menu "Chamados solicitados" DEVE (MUST) ser visível a todos os perfis oficiais; sua visibilidade NÃO DEVE (MUST NOT) ser tratada como autorização, que permanece no Xano pelo vínculo com o chamado. A lista DEVE (MUST) apresentar a ordem retornada pelo backend (`ultima_atualizacao_em` decrescente) e, nesta Sprint, NÃO DEVE (MUST NOT) oferecer filtros, preferências salvas ou paginação. O detalhe DEVE (MUST) apresentar dados funcionais, comentários públicos e histórico público, e oferecer a ação de rejeitar solução nas mesmas condições e estados da ação do detalhe do Gerente; ele NÃO DEVE (MUST NOT) oferecer o botão Detalhe do Totem nem o drawer de telemetria. A interface NÃO DEVE (MUST NOT) oferecer comentário, Save, atribuição nem timeline técnica.

#### Scenario: Solicitante transferido acompanha e rejeita
- **WHEN** um usuário hoje associado a outra Loja abre, pela interface do solicitante, chamado `Resolvido` que solicitou
- **THEN** o Reflex apresenta detalhe, comentários públicos e histórico, e permite rejeitar com justificativa pelo contrato único de rejeição

#### Scenario: Chamado sem vínculo
- **WHEN** o usuário acessa diretamente pela interface do solicitante um chamado do qual não é solicitante
- **THEN** o Reflex apresenta a negação retornada pelo Xano sem exibir dados do chamado

#### Scenario: Lista vazia
- **WHEN** o usuário não é solicitante de nenhum chamado
- **THEN** o Reflex informa que não há chamados solicitados

#### Scenario: Menu para todos os perfis oficiais
- **WHEN** Gerente, Técnico, Diretoria ou Administrador autenticado visualiza o menu lateral
- **THEN** o item "Chamados solicitados" está disponível e leva a `/chamados/solicitados`

#### Scenario: Detalhe sem telemetria
- **WHEN** o solicitante abre `/chamados/solicitados/[chamado_id]`
- **THEN** o Reflex não apresenta botão Detalhe do Totem, drawer nem dados de telemetria

### Requirement: Publicação de comentário confirma gravação independentemente da atualização do detalhe
Após o contrato de criação confirmar a persistência de comentário público, o Reflex DEVE (MUST) apresentar confirmação visual explícita, preservar na lista o DTO retornado pelo Xano e limpar o rascunho. Uma falha posterior ao consultar novamente o detalhe NÃO DEVE (MUST NOT) ser apresentada como falha da publicação já confirmada; o resultado da atualização do detalhe DEVE (MUST) ser comunicado separadamente.

#### Scenario: Publicação confirmada
- **WHEN** a criação do comentário público retorna sucesso confirmado pelo Xano
- **THEN** o Reflex apresenta confirmação visual, inclui o comentário retornado pelo servidor e limpa o rascunho

#### Scenario: Publicação não confirmada
- **WHEN** a criação do comentário público falha ou não retorna confirmação válida
- **THEN** o Reflex não apresenta sucesso nem descarta o rascunho e apresenta erro sanitizado da publicação

#### Scenario: Falha ao atualizar detalhe após publicação confirmada
- **WHEN** a publicação foi confirmada e a consulta posterior do detalhe falha
- **THEN** o Reflex mantém o comentário retornado e a confirmação de publicação e informa separadamente que o detalhe não foi atualizado

### Requirement: Filtro de Status do Gerente apresenta Reaberto
A lista de opções de Status do filtro do Gerente DEVE (MUST) incluir `Reaberto` e manter o legado `Solução Rejeitada` enquanto o backend o aceitar, sem que a interface decida a validade do filtro.

#### Scenario: Opção Reaberto
- **WHEN** o Gerente abre o filtro de Status
- **THEN** `Reaberto` está entre as opções e aplicá-lo consulta o backend com esse valor

## MODIFIED Requirements

### Requirement: Gerente pode consultar o detalhe básico do chamado
O sistema DEVE (MUST) fornecer uma página de detalhe que consulte `GET /gerente/chamados/{chamados_id}` e apresente identificação, título, descrição, status, prioridade, origem, abertura, última atualização, SLA aplicado, ativo, Loja, categoria, solicitante e técnico quando houver. A página DEVE (MUST) oferecer botão Detalhe do Totem que abre drawer lateral direito, com superfície própria, largura adequada e rolagem interna, fechável por X, com o resumo autorizado do Totem. A telemetria NÃO DEVE (MUST NOT) duplicar-se no corpo do chamado. A página DEVE (MUST) consultar e apresentar separadamente os comentários públicos autorizados e o histórico público de status do chamado, sem oferecer edição do chamado, mudança de status, atribuição, diagnóstico, solução ou resolução nesta capacidade, com a única exceção da ação específica de rejeitar solução em chamado `Resolvido`.

#### Scenario: Detalhe carregado
- **WHEN** o Xano retorna um chamado autorizado da Loja
- **THEN** o Reflex apresenta seus dados funcionais, incluindo ativo, Loja, categoria, solicitante, técnico quando houver e última atualização, sem usar `created_at` como abertura

#### Scenario: Drawer do Totem
- **WHEN** o Gerente aciona Detalhe do Totem
- **THEN** o Reflex abre drawer à direita com Totem, Loja, estado, valores e
  timestamp da última telemetria autorizada, sem navegar para `/monitoramento`

#### Scenario: Telemetria ausente
- **WHEN** o resumo do Totem retorna telemetria nula
- **THEN** o drawer informa a ausência sem exibir valores inventados

#### Scenario: Técnico ainda não atribuído
- **WHEN** o detalhe retorna técnico nulo
- **THEN** o Reflex apresenta a ausência de atribuição sem oferecer ação para atribuir ou assumir

#### Scenario: Comentários públicos carregados
- **WHEN** a consulta de comentários públicos do chamado é aceita
- **THEN** o Reflex apresenta somente os comentários retornados, do mais recente ao mais antigo

#### Scenario: Sem ações técnicas
- **WHEN** o detalhe está em qualquer status
- **THEN** o Reflex não oferece Save operacional, mudança direta de status, atribuição ou comentário interno ao Gerente

### Requirement: Reflex permite comentar chamado autorizado com rascunho descartável
O Reflex DEVE (MUST) oferecer ao Gerente autenticado envio de comentário para o contrato funcional específico e descarte exclusivamente local do rascunho. A interface NÃO DEVE (MUST NOT) enviar autor, Loja, visibilidade, timestamp ou status como dados sob controle do cliente.

#### Scenario: Envio de comentário público
- **WHEN** o Gerente envia conteúdo de comentário não vazio em chamado autorizado da própria Loja, inclusive em chamado `Encerrado` ou `Cancelado`
- **THEN** o Reflex chama o contrato específico, apresenta o comentário retornado e atualiza a visualização sem inventar dados locais

#### Scenario: Descarte do rascunho
- **WHEN** o Gerente descarta comentário ainda não enviado
- **THEN** o Reflex limpa somente o conteúdo local sem executar requisição nem alterar o chamado

#### Scenario: Chamado terminal
- **WHEN** o detalhe informa status `Encerrado` ou `Cancelado`
- **THEN** o Reflex mantém os comentários públicos e o histórico visíveis e oferece envio de comentário público pelo contrato autorizado, sem reabrir ou editar o chamado
