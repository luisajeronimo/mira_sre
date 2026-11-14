# autorização por perfis Specification

## Purpose

Definir a autorização aplicada pelo Xano aos perfis oficiais do MIRA, incluindo o isolamento dos dados da unidade associada ao Gerente.

## Requirements

### Requirement: Autorização é aplicada no Xano
O sistema DEVE (MUST) autorizar cada requisição destinada a usuários no Xano, utilizando a identidade autenticada e o perfil oficial, independentemente do que o Reflex exibir ou ocultar.

#### Scenario: Interface oculta uma ação proibida
- **WHEN** um usuário tenta chamar diretamente uma operação que seu perfil não autoriza
- **THEN** o Xano rejeita a operação mesmo que a chamada não tenha sido originada pela interface do Reflex

#### Scenario: Operação autorizada
- **WHEN** um usuário autenticado solicita uma operação explicitamente permitida ao seu perfil e ao seu escopo
- **THEN** o Xano permite que a operação prossiga

### Requirement: Negação por padrão
O sistema DEVE (MUST) negar qualquer consulta técnica global destinada a usuário que não esteja explicitamente autorizado para o perfil e escopo autenticados. Administrador possui acesso global à fila e ao detalhe nesta capacidade, além das permissões administrativas já definidas. `admin`, `bot_fiscalizacao` e valores não oficiais não recebem permissões humanas.

#### Scenario: Operação sem permissão definida
- **WHEN** um usuário autenticado solicita consulta técnica global sem permissão definida para seu perfil
- **THEN** o Xano rejeita a operação sem expor dados

#### Scenario: Perfil não oficial
- **WHEN** uma requisição está associada a `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `bot_fiscalizacao` ou qualquer outro valor não oficial
- **THEN** o Xano não atribui permissões de um perfil oficial à requisição

### Requirement: Gerente acessa somente sua unidade
O sistema DEVE (MUST) restringir o Gerente à unidade à qual ele estiver associado e aos dados relacionados a essa unidade, incluindo seus ativos e chamados que o Gerente esteja autorizado a acompanhar. Para chamados, a unidade DEVE (MUST) ser a Loja resolvida pelo vínculo histórico do Totem no `criado_em` do chamado, conforme `vinculo-historico-totem-loja`; chamado sem Loja resolvida NÃO DEVE (MUST NOT) ser tratado como pertencente à unidade de nenhum Gerente.

#### Scenario: Gerente consulta a própria unidade
- **WHEN** um Gerente autenticado consulta dados pertencentes à sua unidade associada
- **THEN** o Xano retorna somente os dados permitidos dessa unidade

#### Scenario: Gerente informa outra unidade diretamente
- **WHEN** um Gerente autenticado tenta consultar ou alterar dados de uma unidade diferente da sua associação
- **THEN** o Xano rejeita a operação sem retornar dados da outra unidade

#### Scenario: Gerente sem unidade associada
- **WHEN** um Gerente autenticado solicita uma operação dependente de unidade e não possui uma associação válida com uma Loja
- **THEN** o Xano rejeita a operação sem ampliar seu escopo de acesso

#### Scenario: Chamado de Totem transferido depois da abertura
- **WHEN** o Totem de um chamado foi transferido para a Loja do Gerente depois do `criado_em` do chamado
- **THEN** o chamado pertence à Loja vigente na abertura e o Xano rejeita o acesso do Gerente da nova Loja

#### Scenario: Chamado sem Loja histórica
- **WHEN** um Gerente consulta chamado cuja Loja resolvida é nula
- **THEN** o Xano rejeita o acesso como não autorizado, sem usar a Loja atual do Totem

### Requirement: CRUDs genéricos não ampliam permissões
O sistema NÃO DEVE (MUST NOT) permitir que endpoints CRUD genéricos contornem as regras de autorização ou concedam operações administrativas e destrutivas não previstas para os perfis oficiais. A criação de usuário administrativo DEVE permanecer no contrato funcional específico autorizado apenas a Administrador. As consultas genéricas de `interacoes_chamado`, por lista ou por identificador, NÃO DEVEM (MUST NOT) atender o Gerente e DEVEM (MUST) negá-lo antes de ler qualquer interação; o Gerente lê interações exclusivamente pelos contratos funcionais de comentários públicos e de histórico público de status. Os demais perfis mantêm o comportamento vigente dessas consultas.

#### Scenario: Acesso direto a mutação genérica
- **WHEN** um usuário autenticado chama diretamente um endpoint genérico de criação, alteração ou exclusão sem permissão funcional correspondente
- **THEN** o Xano rejeita a operação sem modificar os dados

#### Scenario: Consulta genérica fora do escopo
- **WHEN** uma consulta genérica poderia retornar dados além do escopo autorizado ao usuário
- **THEN** o Xano aplica o filtro de escopo no backend ou rejeita a consulta sem expor esses dados

#### Scenario: Gerente lista interações pelo CRUD genérico
- **WHEN** um Gerente autenticado chama `GET /interacoes_chamado`
- **THEN** o Xano responde como não autorizado sem retornar comentários públicos, comentários internos ou eventos operacionais

#### Scenario: Gerente consulta interação por identificador no CRUD genérico
- **WHEN** um Gerente autenticado chama `GET /interacoes_chamado/{interacoes_chamado_id}` para interação de chamado da própria Loja, comentário público, comentário interno, evento operacional ou identificador inexistente
- **THEN** o Xano responde como não autorizado sem ler nem retornar a interação

#### Scenario: Demais perfis preservados
- **WHEN** Técnico, Diretoria ou Administrador utiliza as consultas genéricas de `interacoes_chamado`
- **THEN** o resultado permanece o mesmo vigente antes desta change

### Requirement: Automações permanecem fora desta autorização de usuários
O sistema NÃO DEVE (MUST NOT) alterar, nesta capacidade, o acesso utilizado pelo Simulator para envio de telemetria nem pelo Fiscal para disparo da verificação de heartbeat.

#### Scenario: Aplicação da change
- **WHEN** esta change for implementada
- **THEN** os contratos de acesso usados pelo Simulator e pelo Fiscal permanecem com o comportamento anterior à change

### Requirement: Autorização central considera troca obrigatória pendente
O sistema DEVE (MUST) aplicar centralmente o estado de troca obrigatória antes da autorização de operações funcionais normais. A sessão pendente somente DEVE passar para a consulta da própria identidade e para a operação autenticada de troca de senha.

#### Scenario: Autorização de operação normal com pendência
- **WHEN** uma sessão pendente alcança a autorização de uma operação funcional normal
- **THEN** o sistema a rejeita antes de executar a regra funcional da operação

#### Scenario: Operação permitida durante pendência
- **WHEN** uma sessão pendente consulta a própria identidade ou envia sua nova senha ao contrato de primeiro acesso
- **THEN** o sistema permite a operação autenticada correspondente

### Requirement: Técnico consulta fila e detalhe globais
O sistema DEVE (MUST) autorizar Técnico a consultar globalmente fila e detalhe e a executar a tratativa definida: editar Responsável, Status, Prioridade e Categoria em chamado não terminal e adicionar comentários Público ou Interno, inclusive em terminal. A autorização DEVE (MUST) ser aplicada no Xano.

#### Scenario: Técnico salva tratativa global
- **WHEN** um Técnico autenticado envia Save válido para chamado global não terminal
- **THEN** o Xano autoriza a operação conforme o contrato de tratativa

#### Scenario: Técnico altera chamado terminal
- **WHEN** um Técnico tenta editar campo funcional de chamado Encerrado ou Cancelado
- **THEN** o Xano rejeita a alteração sem impedir comentário permitido

#### Scenario: Técnico consulta dados da fila
- **WHEN** um Técnico autenticado consulta fila, detalhe ou catálogo necessário à tratativa
- **THEN** o Xano retorna somente os dados globais previstos pelos contratos funcionais

#### Scenario: Técnico solicita operação administrativa
- **WHEN** um Técnico autenticado solicita operação administrativa ou destrutiva fora da tratativa documentada
- **THEN** o Xano rejeita a operação sem executá-la

### Requirement: Diretoria consulta fila e detalhe globais
O sistema DEVE (MUST) autorizar Diretoria a consultar globalmente fila e detalhe e a executar a mesma tratativa operacional do Técnico em chamados não terminais, além de adicionar comentários Público ou Interno inclusive em terminal. Essa autorização NÃO DEVE (MUST NOT) conceder CRUD genérico.

#### Scenario: Diretoria salva tratativa global
- **WHEN** usuário da Diretoria autenticado envia Save válido para chamado não terminal
- **THEN** o Xano autoriza a operação no escopo global

#### Scenario: Diretoria usa CRUD genérico
- **WHEN** usuário da Diretoria tenta alterar chamado por CRUD genérico
- **THEN** o Xano rejeita a requisição sem modificar dados

#### Scenario: Diretoria consulta dados globais
- **WHEN** usuário da Diretoria autenticado solicita consulta global prevista pelo MIRA
- **THEN** o Xano autoriza a consulta sem restringi-la a uma única Loja

#### Scenario: Diretoria tenta alterar dados operacionais
- **WHEN** usuário da Diretoria solicita alteração operacional fora da tratativa documentada
- **THEN** o Xano rejeita a operação sem executá-la

### Requirement: Gerente não acessa a fila técnica global
O sistema NÃO DEVE (MUST NOT) conceder ao Gerente acesso à fila ou ao detalhe técnico global; sua jornada autorizada permanece separada.

#### Scenario: Gerente tenta consultar jornada técnica global
- **WHEN** um Gerente autenticado solicita a fila ou o detalhe técnico global
- **THEN** o Xano responde HTTP 403 sem expor chamados fora dos contratos próprios do Gerente

### Requirement: Administrador possui tratativa operacional global
O sistema DEVE (MUST) autorizar Administrador a consultar globalmente fila e detalhe e a executar a mesma tratativa operacional do Técnico em chamados não terminais, além de adicionar comentários Público ou Interno inclusive em terminal. As permissões administrativas existentes permanecem separadas desse contrato funcional.

#### Scenario: Administrador salva tratativa global
- **WHEN** Administrador autenticado envia Save válido para chamado não terminal
- **THEN** o Xano autoriza a operação no escopo global

#### Scenario: Administrador comenta chamado terminal
- **WHEN** Administrador autenticado envia comentário Interno não vazio para chamado terminal
- **THEN** o Xano cria o comentário sem reabrir nem editar campos funcionais

### Requirement: Consulta de monitoramento possui contrato global autorizado
O Xano DEVE (MUST) fornecer contrato dedicado de consulta de monitoramento de
Totens somente para Técnico, Diretoria e Administrador autenticados. O contrato
DEVE (MUST) aplicar a identidade da sessão no backend e NÃO DEVE (MUST NOT)
alterar o contrato existente de ativos genéricos.

#### Scenario: Perfil global consulta monitoramento
- **WHEN** Técnico, Diretoria ou Administrador autenticado solicita o contrato
  dedicado de monitoramento
- **THEN** o Xano retorna somente a coleção global prevista pelo contrato

#### Scenario: Gerente chama o contrato diretamente
- **WHEN** Gerente autenticado chama diretamente o contrato de monitoramento
- **THEN** o Xano responde HTTP 403 sem retornar dados globais

#### Scenario: Sessão ausente ou inválida
- **WHEN** a consulta de monitoramento não possui sessão válida
- **THEN** o Xano responde HTTP 401 sem retornar dados

#### Scenario: Contrato genérico de ativos preservado
- **WHEN** consumidor autorizado usa o contrato genérico de ativos existente
- **THEN** seu comportamento e escopo permanecem inalterados por esta capacidade

### Requirement: Leituras genéricas de interações não expõem registros internos ao Gerente
Os GETs genéricos de coleção e por ID de `interacoes_chamado` DEVEM (MUST) permitir Técnico, Diretoria e Administrador autenticados a receber o registro bruto. Gerente DEVE (MUST) consultar comentários pela rota funcional pública já autorizada; esses acessos NÃO DEVEM (MUST NOT) conceder mutações genéricas ou Gestão.

#### Scenario: Técnico consulta interação genérica
- **WHEN** Técnico autenticado chama o GET genérico de coleção ou de ID
- **THEN** o Xano mantém a leitura atualmente autorizada para Técnico

#### Scenario: Gerente consulta interação genérica
- **WHEN** Gerente autenticado chama qualquer um dos dois GETs genéricos de interações, mesmo para chamado de sua Loja
- **THEN** o Xano rejeita a consulta sem retornar comentário interno ou registro bruto

#### Scenario: Gerente consulta comentários públicos funcionais
- **WHEN** Gerente autenticado solicita os comentários de chamado autorizado por `GET /gerente/chamados/{chamados_id}/comentarios`
- **THEN** o contrato funcional continua retornando somente comentários públicos permitidos

#### Scenario: Outro perfil solicita GET genérico
- **WHEN** Diretoria ou Administrador chama um dos dois GETs genéricos de interações
- **THEN** o Xano autoriza a mesma leitura global permitida ao Técnico, sem conceder mutação genérica

### Requirement: Contratos administrativos específicos exigem Administrador
O Xano DEVE (MUST) autorizar somente Administrador autenticado e sem troca pendente a listar, consultar, criar, editar, transferir ou excluir Usuários, Lojas e Totens pelos contratos administrativos específicos. CRUDs genéricos DEVEM (MUST) continuar bloqueados.

#### Scenario: Chamada direta de outro perfil
- **WHEN** Gerente, Técnico ou Diretoria chama diretamente mutação administrativa
- **THEN** o Xano rejeita sem ler ou alterar o cadastro

#### Scenario: Administrador autorizado
- **WHEN** Administrador com sessão concluída chama contrato administrativo válido
- **THEN** o Xano executa somente a operação e os campos definidos nesse contrato

#### Scenario: Último Administrador protegido no backend
- **WHEN** cliente chama diretamente edição de perfil ou exclusão que deixaria zero Administradores
- **THEN** o Xano rejeita a mutação sem efeito parcial, mesmo se duas requisições ocorrerem ao mesmo tempo

### Requirement: Administrador abre chamado manual global
O Xano DEVE (MUST) permitir a Administrador criar chamado manual para Totem de qualquer Loja, derivando a Loja do Totem e o solicitante da sessão. A validação de título, descrição, Categoria, prioridade, SLA e demais regras de abertura manual DEVE (MUST) permanecer no backend.

#### Scenario: Abertura em outra Loja
- **WHEN** Administrador autenticado abre chamado válido para Totem de qualquer Loja
- **THEN** o Xano cria chamado manual com Loja do Totem e Administrador como solicitante humano

#### Scenario: Loja ou solicitante forjado
- **WHEN** cliente informa Loja ou solicitante diferente da relação e sessão autenticadas
- **THEN** o Xano ignora ou rejeita esses valores sem atribuir identidade ou Loja indevidas

### Requirement: Gerente usa Loja histórica comprovada do chamado
O Xano DEVE (MUST) autorizar o Gerente em lista, detalhe e comentários pela Loja comprovada na abertura de cada chamado, inclusive nos contratos genéricos de consulta de `chamados`. A Loja atual do Totem NÃO DEVE (MUST NOT) conceder acesso a chamado antigo de outra Loja. Sem Loja histórica demonstrável, o acesso do Gerente DEVE (MUST) falhar fechado.

#### Scenario: Totem transferido
- **WHEN** Gerente da Loja de destino solicita chamado anterior à transferência
- **THEN** o Xano rejeita sem expor o chamado ou suas interações

#### Scenario: Origem indeterminada
- **WHEN** a Loja histórica de um chamado legado não pode ser demonstrada
- **THEN** nenhum Gerente recebe acesso por inferência da Loja atual do Totem

#### Scenario: Lista genérica restrita à Loja histórica
- **WHEN** um Gerente autenticado solicita `GET /chamados`
- **THEN** o Xano devolve somente chamados cuja Loja comprovada na abertura é a Loja do Gerente, sem usar a Loja atual do Totem

#### Scenario: Detalhe genérico de chamado de outra Loja histórica
- **WHEN** um Gerente autenticado solicita `GET /chamados/{chamados_id}` de chamado cuja Loja comprovada na abertura é outra ou não pode ser demonstrada
- **THEN** o Xano rejeita a operação antes de ler e retornar o registro do chamado

#### Scenario: Consulta genérica global preservada
- **WHEN** Técnico ou Diretoria autenticados solicitam `GET /chamados` ou `GET /chamados/{chamados_id}`
- **THEN** o Xano mantém a consulta global, e Administrador e perfis não oficiais continuam negados nesses contratos

### Requirement: Consulta do solicitante é autorizada pelo vínculo com o chamado
O Xano DEVE (MUST) autorizar os contratos de consulta do solicitante somente quando ocorrerem cumulativamente: autenticação válida de `usuarios`; troca obrigatória de senha não pendente; perfil oficial Gerente, Técnico, Diretoria ou Administrador; `chamados.solicitante_id` não nulo; e `chamados.solicitante_id` igual à identidade autenticada. A autorização NÃO DEVE (MUST NOT) depender da Loja atual do usuário, e o vínculo NÃO DEVE (MUST NOT) conceder acesso a outros chamados, inclusive aos da Loja anterior do usuário. Chamado inexistente e chamado não associado ao usuário DEVEM (MUST) receber a mesma resposta de recurso não encontrado, sem revelar a existência do chamado. Identificadores, Loja ou perfil enviados pelo cliente NÃO DEVEM (MUST NOT) conceder autorização. Esses contratos são somente leitura e NÃO DEVEM (MUST NOT) conceder comentário, rejeição de solução, Save, atribuição ou acesso à fila e ao detalhe técnicos.

#### Scenario: Solicitante associado
- **WHEN** um usuário com perfil oficial consulta chamado do qual é o solicitante
- **THEN** o Xano autoriza a consulta

#### Scenario: Solicitante de outra Loja
- **WHEN** o solicitante pertence hoje a Loja diferente da Loja do Totem do chamado
- **THEN** o Xano autoriza a consulta pelo vínculo, sem considerar a Loja atual

#### Scenario: Perfil global como solicitante
- **WHEN** Técnico, Diretoria ou Administrador consulta pelo contrato do solicitante chamado do qual é o solicitante
- **THEN** o Xano autoriza a consulta somente desse chamado

#### Scenario: Chamado de outra pessoa
- **WHEN** um usuário com perfil oficial consulta pelo contrato do solicitante chamado cujo solicitante é outro usuário, inclusive da mesma Loja ou da Loja anterior do usuário
- **THEN** o Xano responde como recurso não encontrado, sem retornar dados

#### Scenario: Chamado inexistente
- **WHEN** o identificador não corresponde a chamado existente
- **THEN** o Xano responde com a mesma resposta de recurso não encontrado dada a chamado de outra pessoa

#### Scenario: Chamado sem solicitante humano
- **WHEN** o chamado possui `solicitante_id` nulo
- **THEN** nenhum usuário é autorizado pelo contrato do solicitante e a resposta é de recurso não encontrado

#### Scenario: Perfil não oficial
- **WHEN** um usuário autenticado sem perfil oficial usa o contrato do solicitante, ainda que seja o solicitante do chamado
- **THEN** o Xano responde como não autorizado sem consultar chamados

#### Scenario: Troca de senha pendente
- **WHEN** um usuário com troca obrigatória pendente usa o contrato do solicitante
- **THEN** o Xano responde como não autorizado sem consultar chamados

#### Scenario: Identificador inválido
- **WHEN** o identificador do chamado é ausente, não numérico ou menor que 1
- **THEN** o Xano rejeita a entrada antes de qualquer consulta

### Requirement: Rejeição de solução é autorizada somente ao Gerente da Loja do chamado
O Xano DEVE (MUST) autorizar a rejeição de solução somente ao usuário autenticado, sem troca de senha pendente, com perfil Gerente e Loja associada igual à Loja do Totem do chamado resolvida pelo vínculo histórico no `criado_em` do chamado (`vinculo-historico-totem-loja`). Técnico, Diretoria, Administrador e usuários sem perfil oficial NÃO DEVEM (MUST NOT) receber essa permissão. A permissão de rejeitar NÃO DEVE (MUST NOT) conceder ao Gerente Save operacional, mudança direta de status, atribuição, comentário interno ou acesso à fila e ao detalhe técnicos. Identificador, Loja ou perfil enviados pelo cliente e a visibilidade da ação no Reflex NÃO DEVEM (MUST NOT) conceder autorização.

#### Scenario: Gerente da Loja
- **WHEN** um Gerente rejeita chamado ligado a Totem da própria Loja
- **THEN** o Xano autoriza a operação

#### Scenario: Gerente de outra Loja
- **WHEN** um Gerente tenta rejeitar chamado de outra Loja
- **THEN** o Xano nega a operação sem retornar nem alterar dados

#### Scenario: Gerente sem Loja
- **WHEN** um Gerente sem Loja associada tenta rejeitar
- **THEN** o Xano nega a operação

#### Scenario: Perfil operacional
- **WHEN** Técnico, Diretoria ou Administrador usa a operação de rejeição
- **THEN** o Xano nega a operação

#### Scenario: Gerente tenta alterar status pelo Save
- **WHEN** um Gerente chama o Save operacional ou um endpoint genérico de alteração
- **THEN** o Xano continua negando a operação

### Requirement: Perfis operacionais compartilham os mesmos acessos
Técnico, Diretoria e Administrador DEVEM (MUST) ter os mesmos acessos operacionais, incluindo SLA na fila/detalhe, indicadores, monitoramento, abertura manual global e escopos de consulta. Gestão administrativa e seus contratos de Usuários, Lojas e Totens DEVEM (MUST) continuar exclusivos do Administrador. Autenticação e primeiro acesso continuam obrigatórios.

#### Scenario: Matriz operacional comum
- **WHEN** qualquer um dos três perfis operacionais consulta uma funcionalidade operacional com sessão concluída
- **THEN** recebe os mesmos contratos e ações, sujeitos às mesmas validações

#### Scenario: Gestão continua exclusiva
- **WHEN** Técnico ou Diretoria tenta acessar Gestão ou contratos administrativos diretamente
- **THEN** o acesso é negado; somente Administrador tem essa permissão

#### Scenario: Acesso não muda elegibilidade de responsável
- **WHEN** Diretoria ou Administrador abre um chamado ou consulta atribuições
- **THEN** continua podendo selecionar apenas Técnicos como responsáveis; o perfil da sessão não é reescrito

#### Scenario: Leituras genéricas operacionais
- **WHEN** um perfil operacional consulta Loja, Totem, telemetria ou interações pelos contratos de leitura existentes
- **THEN** recebe o mesmo escopo global dos outros perfis operacionais, sem ganhar mutações genéricas

### Requirement: Preferências operacionais são isoladas por identidade e escopo
O Xano DEVE (MUST) autorizar leitura e escrita de preferências da fila global
somente para Técnico, Diretoria e Administrador autenticados, usando o usuário
da sessão como único dono do registro. Gerente não possui esse contrato;
Os três perfis podem usar `Todos` e `Atribuídos a mim`, com preferência própria por usuário e escopo.

#### Scenario: Identificador de usuário forjado
- **WHEN** cliente tenta indicar outro usuário ao ler ou salvar preferência
- **THEN** o contrato ignora ou rejeita o identificador e usa exclusivamente a
  identidade autenticada, sem expor preferência alheia

#### Scenario: Perfil autorizado usa a própria preferência
- **WHEN** Técnico, Diretoria ou Administrador autenticado usa escopo permitido
- **THEN** o Xano lê ou grava somente o registro pertencente àquela identidade

#### Scenario: Escopo pessoal acessível aos perfis operacionais
- **WHEN** Diretoria ou Administrador solicita `Atribuídos a mim`
- **THEN** a consulta e a preferência são autorizadas para a própria identidade; sem atribuições correspondentes, a consulta retorna vazia

#### Scenario: Gerente tenta preferência global
- **WHEN** Gerente autenticado chama leitura ou save de preferências globais
- **THEN** o Xano responde HTTP 403 sem expor ou alterar registro
