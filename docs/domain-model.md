# Modelo de Domínio — MIRA

## 1. Objetivo e escopo

Este documento descreve os conceitos fundamentais do domínio do MIRA, suas responsabilidades, relacionamentos e regras estruturais.

Ele representa a **visão de domínio aprovada para orientar as próximas changes do OpenSpec**. As changes já arquivadas permanecem como histórico e não devem ser reescritas. Quando uma regra deste modelo ainda não estiver refletida nas specs consolidadas ou na implementação atual, sua adoção deve ocorrer por uma nova change antes de qualquer alteração funcional.

Este documento **não define endpoints, payloads, códigos HTTP, detalhes físicos de tabelas, componentes de interface ou algoritmos de implementação**. Esses detalhes pertencem às specs, designs e changes do OpenSpec.

Registros históricos podem não possuir informações introduzidas por mudanças posteriores. O sistema não deve inventar valores históricos nem executar backfill sem uma change aprovada.

## 2. Visão conceitual

O MIRA acompanha uma rede de restaurantes que possui Totens de autoatendimento. Os Totens produzem telemetria, podem ficar indisponíveis e podem originar chamados de atendimento.

Os principais conceitos do domínio são:

```text
Loja
 ├── Usuário Gerente
 └── Totem
      ├── Telemetria
      └── Chamado
           ├── Categoria de Serviço
           ├── Solicitante
           ├── Técnico responsável, quando atribuído
           └── Interações / Histórico
```

O MIRA monitora somente **Totens**. O termo "ativo" pode aparecer na implementação e em registros existentes, mas, no domínio do projeto, todo ativo monitorado é um Totem.

## 3. Loja

### Descrição

Representa uma unidade da rede de restaurantes.

### Responsabilidade

Organizar os Totens, Gerentes e chamados vinculados à unidade e permitir análises operacionais por Loja e região.

### Informações conceituais

- identificação;
- nome;
- localização/endereço;
- região;
- situação da unidade.

### Relacionamentos

- uma Loja pode possuir vários Totens;
- uma Loja pode possuir usuários com perfil Gerente;
- cada Gerente pertence a uma Loja;
- cada chamado pertence à Loja em que seu Totem estava vinculado no instante da abertura (Loja histórica), conforme o histórico de vínculos da seção 5;
- indicadores podem ser agregados por Loja e região.

### Regras estruturais

- Gerentes só podem atuar sobre dados e chamados da própria Loja; para chamados, vale a Loja histórica, e chamado sem Loja histórica comprovada não pertence a nenhuma Loja para essa finalidade;
- o Administrador do Sistema pode cadastrar e manter Lojas;
- os dados obrigatórios do cadastro devem ser informados na criação, conforme a spec administrativa correspondente.

## 4. Usuário e papéis

### Descrição

Representa uma pessoa autorizada a utilizar o MIRA.

### Responsabilidade

Identificar quem acessa o sistema, seu papel e o escopo de atuação permitido.

### Informações conceituais

- identificação;
- nome;
- e-mail;
- papel de acesso;
- Loja, obrigatória quando o papel for Gerente.

### Relacionamentos

- um Gerente pertence a uma Loja;
- um usuário humano pode atuar como solicitante de chamados;
- somente usuários com perfil Técnico podem ser responsáveis por chamados;
- Diretoria e Administrador podem gerir atribuições, sem se tornarem responsáveis;
- usuários podem registrar interações conforme suas permissões.

### Regras estruturais

#### Gerente

- pertence obrigatoriamente a uma Loja;
- abre chamados manuais sobre Totens da própria Loja;
- consulta todos os chamados da própria Loja, inclusive históricos;
- não acessa chamados de outras Lojas;
- acompanha o status atual e os comentários de visibilidade geral dos chamados da própria Loja;
- pode registrar comentários de visibilidade geral em qualquer chamado da própria Loja, inclusive `Encerrado` e `Cancelado`;
- não visualiza comentários privados nem eventos operacionais da tratativa;
- não altera diretamente o status;
- não recebe permissões técnicas de tratativa, atribuição ou comentário privado;
- pode rejeitar a solução de Chamado `Resolvido` da própria Loja, com justificativa obrigatória, por operação específica que leva a `Solução Rejeitada` *(aprovada para a Sprint 3, condicionada à prova de segurança transacional; ainda não implementada)*; não recebe permissão genérica de alterar status.

#### Solicitante

- é o usuário humano associado a um Chamado pelo vínculo de solicitante e pode ter qualquer um dos quatro perfis oficiais;
- acompanha, somente para leitura e em interface própria, os Chamados aos quais está associado, independentemente da Loja atual;
- o vínculo não concede acesso a outros Chamados, inclusive aos da Loja anterior;
- a interface própria não apresenta telemetria do Totem nem oferece comentário, aceitação ou rejeição de solução;
- Chamados automáticos não possuem solicitante humano.

#### Técnico

- possui escopo global sobre os chamados;
- consulta chamados atribuídos, não atribuídos e atribuídos a outros Técnicos;
- pode atribuir (inclusive a si mesmo), reatribuir e liberar chamados não terminais pelo Save operacional;
- pode alterar o status de chamados não terminais;
- pode registrar comentários gerais ou privados;
- pode consultar e filtrar chamados por critérios definidos nas respectivas specs.

#### Diretoria

- possui as mesmas capacidades operacionais do Técnico;
- possui escopo global;
- consulta e interage com dashboards e indicadores consolidados.

#### Administrador do Sistema

- possui todas as capacidades dos demais papéis;
- possui escopo global;
- cadastra e mantém Lojas, Totens e usuários;
- ao cadastrar um Gerente, deve associá-lo a uma Loja;
- a política de criação e troca inicial de senha será definida em change própria.

Filtros escolhidos em listas são preferências do usuário e devem persistir entre sessões até que o próprio usuário execute a ação de limpar filtros. Os detalhes de cada filtro e de sua apresentação pertencem às specs das respectivas telas.

## 5. Totem

### Descrição

Representa o equipamento de autoatendimento monitorado pelo MIRA.

### Responsabilidade

Ser o elemento monitorado pelo sistema e o ponto de associação entre Loja, telemetria, disponibilidade e chamados.

### Informações conceituais

- identificação;
- nome;
- Loja onde está instalado atualmente;
- histórico de vínculos com Lojas;
- status operacional atual.

### Relacionamentos

- cada Totem pertence a uma Loja em cada momento; o histórico de vínculos registra desde quando;
- um Totem pode possuir muitos eventos de telemetria;
- um Totem pode possuir eventos de disponibilidade materializados pelo Xano;
- um Totem pode possuir vários chamados ao longo do tempo.

### Regras estruturais

- todo ativo monitorado pelo MIRA é um Totem;
- os estados operacionais considerados são `Online` e `Offline`;
- todo novo chamado do MIRA está relacionado a exatamente um Totem;
- quando o mesmo problema afetar vários Totens, deve existir um chamado para cada Totem afetado;
- registros históricos anteriores à formalização dessas regras podem permanecer incompletos, sem backfill automático;
- um Totem já `Offline` não deve gerar nova ação automática de indisponibilidade apenas pela continuidade da ausência de heartbeat;
- o recebimento posterior de telemetria pode permitir que o Totem volte a `Online`.

### Histórico de vínculos com Lojas

- cada vínculo comprova que, a partir de um instante, o Totem pertence a uma Loja; os tipos são `criacao` (cadastro do Totem), `transferencia` (mudança de Loja pelo Administrador) e `marco`;
- um `marco` é registrado quando um chamado novo é criado para Totem sem nenhum vínculo e com Loja atual: comprova essa Loja somente a partir do instante do chamado;
- a abertura manual exige que o Totem tenha Loja atual; sem ela, é rejeitada e não cria marco;
- o heartbeat pode criar incidente automático para Totem sem Loja atual, mas não cria marco; a Loja histórica desse incidente permanece nula e o Gerente não o acessa;
- a Loja de um chamado é a do vínculo mais recente até o instante de sua abertura; sem vínculo até esse instante, a Loja histórica é nula;
- chamados anteriores a qualquer vínculo não recebem vínculo retroativo, não são reconstruídos e não usam a Loja atual como substituta;
- consequência: chamados legados sem vínculo ficam fora da jornada do Gerente; Técnico, Diretoria, Administrador e solicitante continuam acessando conforme suas regras, com a Loja apresentada como não informada;
- estado em 2026-11-07: comportamento publicado no Xano; regularização no repositório em andamento pela change `regularizar-loja-historica-totem`; a tabela de vínculos estava vazia.

## 6. Telemetria

### Descrição

Representa um evento técnico produzido por um Totem.

### Responsabilidade

Registrar informações de saúde e comunicação usadas para acompanhamento operacional e detecção de indisponibilidade.

### Informações conceituais

- Totem de origem;
- uso de CPU;
- uso de memória;
- temperatura;
- status de rede;
- momento do evento (`evento_timestamp`).

### Relacionamentos

- cada evento pertence a um Totem existente;
- vários eventos formam o histórico técnico do Totem.

### Regras estruturais

- `evento_timestamp` é a referência temporal do evento;
- o Simulator produz telemetria somente para Totens já cadastrados;
- a telemetria é persistida no Xano;
- um Totem que nunca enviou telemetria permanece sem alteração automática de disponibilidade até que exista uma primeira telemetria válida.

## 7. Monitoramento de heartbeat e disponibilidade

### Descrição

O heartbeat é uma regra operacional baseada na sequência temporal da telemetria e não uma entidade independente.

### Responsabilidade

Detectar ausência de comunicação de um Totem e iniciar o fluxo automático de indisponibilidade quando aplicável.

### Informações conceituais

- última telemetria conhecida;
- momento da detecção;
- estado operacional do Totem;
- categoria usada pelo incidente automático.

### Relacionamentos

- depende da Telemetria do Totem;
- pode alterar o estado operacional do Totem;
- pode originar um Chamado automático.

As transições efetivas são preservadas como fatos específicos de disponibilidade,
relacionados ao Totem e à telemetria que fundamentou a decisão. Cada fato
registra o instante de detecção e o limite de heartbeat aplicado; não armazena
indicadores derivados nem altera dados históricos anteriores.

### Regras estruturais

- o Fiscal apenas dispara periodicamente a verificação;
- o Xano decide sobre indisponibilidade e criação de chamado;
- mais de 15 minutos sem telemetria caracteriza indisponibilidade para um Totem que estava `Online`;
- um Totem que já está `Offline` não deve gerar novo chamado apenas porque continua sem heartbeat;
- antes de criar um chamado automático, o sistema verifica se já existe chamado equivalente para o mesmo Totem e a mesma Categoria;
- chamados `Encerrado` ou `Cancelado` não bloqueiam a criação de um novo incidente equivalente;
- os status não terminais vigentes bloqueiam a criação de outro incidente equivalente;
- o retorno da telemetria pode levar o Totem de volta a `Online`, mas **não resolve, cancela nem encerra o chamado automaticamente**;
- após a recuperação técnica do Totem, a tratativa do chamado continua dependendo de ação humana.

## 8. Categoria de Serviço

### Descrição

Representa a classificação funcional de um chamado.

### Responsabilidade

Organizar os tipos de atendimento, distinguir Incidentes e Requisições e fornecer o parâmetro de SLA aplicável.

### Informações conceituais

- nome;
- classificação: `Incidente` ou `Requisição`;
- parâmetro de SLA em horas;
- elegibilidade para abertura manual.

### Relacionamentos

- uma Categoria pode classificar vários chamados;
- cada Chamado possui uma Categoria.

### Regras estruturais

- uma Categoria pode permitir ou impedir abertura manual;
- a Categoria fornece o SLA aplicável no momento da criação do Chamado;
- para análises de causa e recorrência, a Categoria é a classificação de referência do MIRA.

## 9. Chamado

### Descrição

Representa um Incidente ou uma Requisição tratada pelo Service Desk do MIRA.

### Responsabilidade

Registrar e acompanhar uma necessidade de atendimento relacionada a um Totem.

### Informações conceituais

- identificação/número;
- título;
- descrição;
- origem;
- criador de sistema, quando aplicável;
- status;
- prioridade;
- solicitante;
- Loja;
- Totem relacionado;
- Categoria de Serviço;
- Técnico responsável, quando houver;
- momento de criação;
- momento da última atualização;
- momento da atribuição, quando houver;
- SLA aplicado no momento da criação.

### Relacionamentos

- cada novo Chamado pertence a exatamente uma Loja;
- cada novo Chamado pertence a exatamente um Totem;
- cada Chamado possui uma Categoria;
- um Chamado possui um solicitante humano ou de sistema;
- um Chamado pode não possuir Técnico responsável;
- um Chamado pode possuir muitas Interações ao longo do tempo.

### Regras estruturais

#### Origem

Um Chamado possui uma origem funcional:

- `manual`: aberto por um Gerente;
- `automático`: criado pelo sistema a partir do monitoramento.

Origem classifica como o chamado surgiu; ela não identifica, por si só, quem o
criou.

#### Solicitante e criador de sistema

`solicitante_id` referencia exclusivamente um usuário humano quando aplicável.
Em chamados automáticos de heartbeat, ele permanece ausente. O
`criador_sistema` opcional registra o ator lógico que criou o chamado: nesta
automação, `bot_fiscalizacao` representa o **Bot de Fiscalização**, sem relação
com `usuarios`, login, senha, sessão, token ou permissão humana.

#### Abertura manual

Todo novo Chamado manual deve possuir:

- título;
- descrição;
- Totem;
- Categoria;
- prioridade;
- Loja;
- usuário solicitante.

Um Chamado manual não pode ser criado com ausência dessas informações.

#### Abertura automática

- é criada pelo sistema quando a regra de heartbeat determina a necessidade;
- mantém solicitante humano ausente e registra o **Bot de Fiscalização** como
  criador de sistema;
- o Bot de Fiscalização não é um usuário autenticável;
- utiliza prioridade `Urgente`;
- respeita a regra de prevenção de duplicidade do heartbeat.

#### Prioridade

Os valores canônicos são:

- `Baixa`;
- `Média`;
- `Alta`;
- `Urgente`.

Na abertura manual, o Gerente escolhe diretamente a prioridade. O MIRA não utiliza matriz de impacto × urgência como regra de priorização.

#### SLA aplicado

- o SLA da Categoria é copiado para o Chamado no momento da criação;
- o Chamado preserva esse valor durante toda a sua existência;
- alterações posteriores no SLA da Categoria não modificam retroativamente Chamados existentes;
- a contagem inicia na criação do Chamado;
- a contagem é feita em tempo corrido;
- `Aguardando Solicitante` e `Aguardando Mudança` não pausam o SLA;
- `Resolvido` interrompe a contagem;
- ao entrar em `Solução Rejeitada`, a contagem retoma a partir do saldo acumulado imediatamente antes de `Resolvido`;
- o período em `Resolvido` não consome SLA;
- `Encerrado` e `Cancelado` interrompem a contagem sem retomada.

#### Atribuição

- um Chamado pode existir sem Técnico responsável;
- somente um usuário com perfil `Técnico` pode ser responsável por um Chamado;
- Diretoria e Administrador podem atribuir, reatribuir e liberar o Técnico responsável, mas não se tornam responsáveis pelo Chamado;
- a mudança de responsável ocorre exclusivamente pelo campo Responsável do Save operacional; não há comandos imediatos de assumir, atribuir, reatribuir ou liberar na jornada operacional;
- definir um Técnico em Chamado sem responsável é atribuição; trocar de Técnico é reatribuição; definir `Não atribuído` é liberação;
- atribuição e reatribuição registram o Técnico e o momento da atribuição; liberação limpa ambos;
- Técnico, Diretoria e Administrador podem selecionar qualquer Técnico ou `Não atribuído` em Chamados não `Encerrado` e não `Cancelado`, inclusive quando o responsável atual é outro Técnico;
- salvar o mesmo responsável já persistido não cria nova atribuição nem altera a última atualização;
- mudança de responsável não altera o status, inclusive quando estiver `Novo` ou `Em Atendimento`;
- toda atribuição, reatribuição ou liberação deve gerar registro no histórico.

## 10. Ciclo de vida do Chamado

### Descrição

Representa os estados funcionais utilizados para acompanhar a evolução de um Chamado.

### Responsabilidade

Permitir que o Service Desk represente o momento operacional de cada atendimento e preserve seu histórico de evolução.

### Informações conceituais

Os status aprovados para o domínio são:

- `Novo`;
- `Em Atendimento`;
- `Aguardando Solicitante`;
- `Aguardando Mudança`;
- `Resolvido`;
- `Solução Rejeitada`;
- `Encerrado`;
- `Cancelado`.

Estado atual: `Solução Rejeitada` integra a lista canônica do Save operacional, das listagens, dos filtros e das preferências e permanece como status canônico resultante da rejeição. A operação de rejeição descrita abaixo ainda não existe.

`Aguardando Terceiro` não faz parte do ciclo de vida pretendido do MIRA e deverá ser retirado do comportamento vigente por change própria, sem alteração do histórico de changes arquivadas.

### Relacionamentos

- cada Chamado possui um status atual;
- alterações de status geram Interações estruturadas no histórico.

### Regras estruturais

- o solicitante não altera o status diretamente;
- Técnico, Diretoria e Administrador podem alterar o status de Chamados não terminais;
- nenhuma alteração de status ocorre automaticamente ao atribuir um responsável ao Chamado;
- o Técnico deve definir manualmente `Em Atendimento` quando iniciar efetivamente a tratativa;
- toda alteração de status exige comentário associado;
- alterações para `Resolvido`, `Aguardando Solicitante` e `Cancelado` exigem comentário de visibilidade geral;
- `Aguardando Solicitante` é definido por Técnico, Diretoria ou Administrador; o solicitante visualiza o novo status, mas não recebe notificação obrigatória pelo domínio;
- comentário posterior do solicitante não altera automaticamente `Aguardando Solicitante`; Técnico, Diretoria ou Administrador decide quando retornar a `Em Atendimento`;
- `Aguardando Mudança` é definido por Técnico, Diretoria ou Administrador e somente sai desse estado por nova alteração manual de um desses papéis;
- `Cancelado` é terminal: não volta a estado não terminal nem recebe edições funcionais; comentários permanecem permitidos conforme as specs vigentes;
- `Encerrado` é terminal: não volta a estado não terminal nem recebe edições funcionais; comentários permanecem permitidos conforme as specs vigentes;
- `Resolvido` significa que a solução técnica foi aplicada e o serviço foi considerado restaurado;
- enquanto `Resolvido`, o Gerente da Loja à qual o Chamado pertence pode rejeitar a solução; o solicitante permanece somente leitura;
- a aceitação explícita da solução não está definida: não há regra aprovada sobre quem aceita;
- se não houver rejeição durante 72 horas corridas após a entrada em `Resolvido`, o sistema deve alterar automaticamente o Chamado para `Encerrado`, registrando comentário público de sistema;
- Chamados que já estavam `Resolvido` antes do início de vigência do encerramento automático não são encerrados automaticamente; continuam sujeitos ao encerramento manual pelos perfis operacionais;
- um job ou script periódico apenas dispara a verificação; o Xano avalia a elegibilidade e efetiva o encerramento;
- o retorno de telemetria não participa do encerramento automático;
- Técnico, Diretoria e Administrador podem selecionar `Solução Rejeitada` no Save de chamado não terminal, com comentário humano obrigatório de visibilidade Pública ou Interna; aceite e rejeição pelo solicitante são fluxos futuros;
- essa transição operacional segue as regras gerais do Save: outras diferenças funcionais só são persistidas quando também forem informadas e autorizadas; o comentário e a última atualização são registrados;
- para rejeitar uma resolução, o Gerente da Loja deve registrar justificativa obrigatória, validada no backend e registrada como comentário público; o sistema altera então o status para `Solução Rejeitada` e registra a transição no histórico;
- a rejeição não altera atribuição, prioridade, Categoria ou demais dados funcionais do Chamado; o comentário e a última atualização são registrados;
- rejeição e encerramento automático estão aprovados para a Sprint 3 e ainda não estão implementados; suas gravações dependem de prova verificável de segurança transacional no Xano;
- se um problema reaparecer depois de `Encerrado` ou `Cancelado`, deve ser aberto um novo Chamado.

O domínio não impõe uma matriz rígida de transições intermediárias além das restrições acima. Técnico, Diretoria e Administrador podem escolher o status operacional adequado para Chamados não terminais.

## 11. Interação e histórico do Chamado

### Descrição

Representa uma entrada na linha do tempo do Chamado, incluindo comentários e eventos operacionais relevantes.

### Responsabilidade

Preservar comunicação, contexto e histórico auditável da tratativa.

### Informações conceituais

- Chamado relacionado;
- autor;
- momento do registro;
- conteúdo;
- visibilidade;
- natureza do evento, quando associada a uma alteração operacional;
- estado anterior e novo estado, quando a interação representar mudança de status.

### Relacionamentos

- cada Interação pertence a um Chamado;
- cada Interação possui um autor humano ou de sistema;
- um Chamado pode possuir várias Interações ordenadas no tempo.

### Regras estruturais

- todo comentário atualiza o momento da última atualização do Chamado;
- comentários do solicitante e do Gerente são sempre de visibilidade geral;
- Técnico, Diretoria e Administrador podem registrar comentários gerais ou privados;
- comentário geral pode ser visualizado pelo solicitante e pelos papéis internos autorizados;
- comentário privado é visível somente para Técnico, Diretoria e Administrador;
- a visibilidade (geral ou privada) é atributo exclusivo de comentários; eventos operacionais não possuem visibilidade, e quem os consulta é definido pelo tipo do evento e pelo contrato autorizado;
- eventos de status, atribuição, reatribuição e liberação aparecem na linha do tempo da tratativa para Técnico, Diretoria e Administrador e mantêm dados estruturados suficientes para auditoria;
- o Gerente e o solicitante recebem somente comentários de visibilidade geral e, pelo contrato de histórico, o par de status projetado; nenhum contrato, inclusive consultas genéricas, deve lhes retornar comentários privados ou os demais dados dos eventos operacionais da tratativa;
- histórico público de status *(contrato de leitura aprovado para a Sprint 3)*: o Gerente e o solicitante poderão consultar as transições de status projetadas, somente para leitura, do evento operacional que o Save registra a cada alteração funcional; a projeção expõe exclusivamente o status anterior, o resultante, o momento e o autor identificado pelo nome de exibição e pelo perfil (somente pelo nome quando o perfil não é reconhecido; `Sistema` quando não houver usuário), sem os demais dados do evento, e-mail, identificadores internos ou outros dados do autor;
- eventos sem transição de status são ignorados; sem transições, o histórico é vazio; transições anteriores à implantação do Save operacional e a criação do Chamado não são reconstruídas;
- a consulta do histórico não grava nem altera dados; a apresentação na interface está aprovada e será liberada após a validação de autorização, segurança e contrato (estado atual: contratos de leitura publicados no Xano em 07/11/2026; interface implementada localmente, não publicada e desligada até a validação desses contratos);
- a gravação de um evento de status de tipo próprio permanece bloqueada até comprovação verificável de segurança transacional no Xano e nova decisão humana; a projeção não depende dessa gravação e não comprova a segurança transacional do Save;
- alterações para `Resolvido`, `Aguardando Solicitante` e `Cancelado` não permitem comentário privado;
- Chamados `Encerrado` e `Cancelado` não recebem edições funcionais; comentários permanecem permitidos conforme as specs vigentes.

## 12. SLA

### Descrição

Representa o prazo de atendimento aplicável a um Chamado.

### Responsabilidade

Permitir acompanhamento do tempo consumido e identificação de risco de violação.

### Informações conceituais

- SLA aplicado ao Chamado;
- momento inicial da contagem;
- tempo contabilizado;
- situação de consumo do SLA.

### Relacionamentos

- deriva da Categoria no momento da criação;
- fica preservado no Chamado como valor aplicado.

### Regras estruturais

- a referência inicial é a criação do Chamado;
- a contagem é feita em tempo corrido, sem calendário de expediente;
- `Aguardando Solicitante` e `Aguardando Mudança` não pausam a contagem;
- `Resolvido` interrompe a contagem;
- ao entrar em `Solução Rejeitada`, a contagem retoma a partir do saldo acumulado imediatamente antes de `Resolvido`, sem contabilizar o período em `Resolvido`;
- `Encerrado` e `Cancelado` interrompem a contagem sem retomada;
- para o indicador de risco, o percentual consumido compara tempo contabilizado com o SLA aplicado;
- referência acadêmica inicial de visualização: abaixo de 70% = normal; de 70% a 90% = risco; acima de 90% = crítico; acima de 100% = violado;
- regras adicionais de apresentação ou comportamento devem ser definidas nas specs dos dashboards e da tratativa.

Estado atual: o cálculo do tempo contabilizado, do percentual consumido e da faixa existe localmente como função interna somente leitura do Xano, sem persistência do consumo e ainda não publicada. Uma linha do tempo de status que não reconstrói o status atual torna o SLA não calculável, sem estimativa. Onde o consumo será apresentado ainda não está decidido.

## 13. Dados necessários para indicadores

Esta seção registra somente os **conceitos e dados mínimos necessários** para viabilizar indicadores futuros. A composição visual, filtros e comportamento dos dashboards pertencem ao `project-overview.md` e às respectivas specs.

### Disponibilidade Geral da Rede

Deve ser possível determinar, por Totem e período, quanto tempo ficou `Online` e `Offline`, agregando depois por Loja e rede.

Dados mínimos:

- Totem;
- Loja;
- eventos de telemetria com timestamp;
- momentos em que a indisponibilidade é detectada e em que o Totem retorna a `Online`.

A disponibilidade representa a proporção do período observado em que o Totem esteve operacional.

### MTTD — Tempo Médio de Detecção

Deve ser possível medir o tempo entre o início operacionalmente identificável da indisponibilidade e sua detecção pelo MIRA.

Dados mínimos:

- última telemetria válida antes da indisponibilidade;
- momento em que a indisponibilidade é detectada;
- Totem e Loja.

A definição exata do marco inicial usado pelo MIRA deve ser consolidada na spec do indicador antes da implementação.

### MTTR — Tempo Médio de Recuperação

No MIRA, MTTR será tratado como **tempo médio de recuperação do Totem**, e não como tempo de encerramento do Chamado.

Dados mínimos:

- início da indisponibilidade;
- momento em que o Totem volta a `Online`;
- Totem e Loja.

O Chamado pode permanecer aberto mesmo após a recuperação do Totem.

### Volumetria de Chamados por Status

Dados mínimos:

- status atual;
- data de criação;
- data da última atualização;
- Loja;
- Categoria.

### Termômetro de SLA

Dados mínimos:

- data de criação;
- SLA aplicado;
- status atual;
- tempo contabilizado segundo as regras de SLA.

### Top 5 Lojas com Maior Volume de Incidentes

Dados mínimos:

- Loja;
- classificação da Categoria;
- data de criação do Chamado.

Somente Chamados classificados como `Incidente` participam dessa análise.

### Maiores Causas de Indisponibilidade — Pareto

No MIRA, a **Categoria do Chamado** é a referência para causa operacional nos dashboards.

Dados mínimos:

- Categoria;
- classificação;
- Totem;
- Loja;
- data de criação.

### Análise de Recorrência

A recorrência é analisada a partir da repetição de Chamados da mesma Categoria, podendo ser segmentada por Totem, Loja e período.

Dados mínimos:

- Categoria;
- Totem;
- Loja;
- data de criação;
- identificação do Chamado.

Critérios de janela temporal e apresentação devem ser definidos na spec do dashboard, sem necessidade de uma nova entidade de "causa" neste momento.

## 14. Relações consolidadas do domínio-alvo

```text
Loja 1 ─── N Gerente
Loja 1 ─── N Totem

Totem 1 ─── N Telemetria
Totem 1 ─── N Eventos de disponibilidade
Totem 1 ─── N Chamado

Categoria de Serviço 1 ─── N Chamado

Chamado 1 ─── 1 Solicitante humano ou de sistema
Chamado N ─── 0..1 Técnico responsável
Chamado 1 ─── N Interação

Usuário 1 ─── N Interação como autor
```

## 15. Evolução pelo OpenSpec

Este modelo expressa a visão de domínio aprovada para a evolução do MIRA.

As specs consolidadas continuam representando o comportamento efetivamente consolidado do sistema em cada momento. Quando este modelo introduzir uma regra ainda não implementada — como novo papel, novo status, novas permissões ou novos comportamentos de tratativa — a diferença deve ser formalizada em uma nova change antes de alterar código ou dados.

Changes arquivadas não devem ser reescritas para aparentar que decisões posteriores já existiam no passado.
