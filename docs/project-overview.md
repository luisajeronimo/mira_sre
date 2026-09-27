# Project Overview — MIRA

## 1. Visão geral

O MIRA é uma plataforma acadêmica de **Service Desk e observabilidade** voltada ao acompanhamento de totens de autoatendimento de uma rede de restaurantes.

O sistema reúne telemetria, disponibilidade dos totens, abertura e tratamento de chamados, histórico de atendimento e indicadores operacionais. Seu objetivo é integrar monitoramento técnico e atendimento em um único fluxo, permitindo acompanhar tanto falhas detectadas automaticamente quanto problemas físicos ou operacionais identificados pelas lojas.

Todos os ativos monitorados pelo MIRA são **totens de autoatendimento**.

Este documento apresenta a visão global e relativamente estável do projeto. Ele não substitui as especificações do OpenSpec e não deve ser usado como evidência de que uma funcionalidade já foi implementada. O comportamento já consolidado do sistema é representado por `openspec/specs/`, e novas evoluções devem ser realizadas por changes.

---

## 2. Problema

Totens de autoatendimento podem apresentar indisponibilidade técnica, problemas físicos ou falhas operacionais que prejudicam o funcionamento das lojas.

Nem todos esses problemas podem ser identificados automaticamente apenas pela telemetria. Por isso, o MIRA combina dois mecanismos complementares:

- monitoramento automático da comunicação e da saúde dos totens;
- abertura manual de chamados para problemas físicos ou operacionais percebidos na loja.

Os chamados são acompanhados pelo Service Desk, tratados pelos perfis autorizados e utilizados como fonte para indicadores operacionais e gerenciais.

---

## 3. Objetivos

O MIRA tem como objetivos:

- acompanhar a saúde e a disponibilidade dos totens;
- receber, persistir e consultar telemetria;
- identificar ausência prolongada de comunicação;
- criar incidentes automáticos quando uma indisponibilidade elegível é detectada;
- permitir que o gerente registre manualmente problemas da própria loja;
- organizar a fila e a tratativa dos chamados;
- manter histórico das ações, comentários e mudanças relevantes;
- controlar SLA conforme a categoria do chamado;
- permitir acompanhamento dos chamados por diferentes perfis, respeitando seus escopos;
- fornecer dashboards e indicadores para acompanhamento da operação da rede.

---

## 4. Público-alvo e perfis de usuário

### 4.1 Gerente

O Gerente está obrigatoriamente associado a uma loja.

Suas principais responsabilidades são:

- acompanhar os totens da própria loja;
- abrir chamados manuais relacionados aos totens da própria loja;
- consultar todos os chamados da própria loja, inclusive históricos;
- acompanhar status, atualizações e comentários visíveis;
- comentar em chamados nos quais atua como solicitante;
- rejeitar uma resolução quando o problema persistir, informando obrigatoriamente o motivo.

O Gerente não deve visualizar chamados pertencentes a outras lojas e não altera diretamente o status dos chamados.

### 4.2 Técnico

O Técnico possui escopo global sobre os chamados.

Suas principais responsabilidades são:

- consultar todos os chamados;
- utilizar filtros e busca por número do chamado;
- visualizar chamados não atribuídos, próprios ou atribuídos a outros Técnicos;
- assumir chamados não atribuídos;
- retirar sua própria atribuição;
- atribuir ou reatribuir chamados a outros Técnicos quando permitido;
- alterar o status dos chamados não terminais;
- registrar comentários e atualizações;
- tratar e resolver chamados;
- consultar informações do Totem, da loja e da telemetria relacionadas ao atendimento.

A assunção de um chamado não inicia automaticamente o atendimento. A mudança para `Em Atendimento` é uma ação explícita.

### 4.3 Diretoria

A Diretoria possui escopo global.

Ela possui as capacidades operacionais do Técnico para consulta e edição de chamados e, adicionalmente, acesso aos dashboards e indicadores consolidados da rede, com filtros e visões gerenciais.

### 4.4 Administrador do Sistema

O Administrador possui escopo global e reúne as capacidades dos demais perfis.

Além das operações de atendimento e acompanhamento, é responsável pelos cadastros administrativos necessários ao funcionamento do sistema, incluindo:

- usuários;
- lojas;
- totens.

No cadastro de usuário, o perfil Gerente exige associação a uma loja. Os demais perfis humanos não exigem vínculo obrigatório com uma loja.

---

## 5. Escopo

O escopo global do MIRA compreende:

- autenticação e autorização conforme perfil;
- administração de usuários, lojas e totens;
- recepção e persistência de telemetria;
- acompanhamento do estado Online/Offline dos totens;
- fiscalização de heartbeat;
- abertura manual de chamados;
- criação automática de incidentes por ausência de heartbeat;
- consulta, atribuição, reatribuição e liberação de chamados;
- ciclo de vida e tratativa dos chamados;
- comentários e histórico de atendimento;
- controle de SLA;
- filtros e busca nas filas e listagens;
- dashboards e indicadores operacionais e gerenciais.

Os dados mestres permanecem persistidos no Xano. O Simulator não recria lojas ou totens a cada execução.

---

## 6. Principais funcionalidades

### 6.1 Telemetria e observabilidade

O Simulator em Python gera telemetria para totens já cadastrados.

A telemetria inclui informações como:

- uso de CPU;
- uso de memória;
- temperatura;
- status de rede;
- `evento_timestamp`.

Os eventos são enviados ao Xano, onde são persistidos e utilizados para acompanhamento operacional e para os cálculos e indicadores definidos pelo projeto.

### 6.2 Heartbeat e disponibilidade

O Fiscal em Python dispara periodicamente a verificação de heartbeat.

A decisão sobre disponibilidade pertence ao Xano.

A regra global é de **15 minutos sem telemetria** para caracterizar a ausência de heartbeat utilizada na avaliação de indisponibilidade.

Um Totem que nunca enviou telemetria permanece sem alteração até que exista uma primeira telemetria válida.

A automação de indisponibilidade considera Totens que estavam Online. Um Totem já considerado Offline não deve gerar repetidamente novos incidentes apenas pela continuidade da ausência de heartbeat.

Quando necessário, o Xano pode marcar o Totem como Offline e criar um incidente automático.

Para evitar duplicidade, um novo incidente automático não deve ser criado quando já existir chamado da mesma categoria para o mesmo Totem em estado não terminal. Chamados `Encerrados` e `Cancelados` não bloqueiam a criação de um novo incidente futuro.

Quando a telemetria retorna, o Totem pode voltar a Online, mas isso **não resolve, cancela nem encerra automaticamente o chamado**. A continuidade da tratativa depende de ação humana.

### 6.3 Chamados manuais

O Gerente pode abrir chamado para um problema físico ou operacional relacionado a um Totem da própria loja, independentemente de o Totem continuar enviando telemetria.

Todo novo chamado manual deve possuir:

- título;
- descrição;
- Totem relacionado;
- categoria;
- prioridade;
- loja;
- solicitante.

Essas informações não podem ficar ausentes em um novo chamado manual.

Quando o mesmo problema afeta vários Totens, deve existir um chamado separado para cada Totem afetado.

### 6.4 Chamados automáticos

Um incidente automático é criado pelo sistema em resposta às condições de heartbeat definidas pelo projeto.

O solicitante de um chamado automático é um **ator de sistema**, representado pelo Bot de Fiscalização, e não um usuário humano autenticável.

Incidentes automáticos de heartbeat utilizam prioridade `Urgente`.

### 6.5 Categorias, prioridade e SLA

Uma categoria de serviço possui conceitualmente:

- nome;
- classificação como `Incidente` ou `Requisição`;
- parâmetro de SLA;
- indicação de elegibilidade para abertura manual.

As prioridades oficiais do projeto são:

- `Baixa`;
- `Média`;
- `Alta`;
- `Urgente`.

Na abertura manual, a prioridade é escolhida diretamente pelo Gerente. O projeto não utiliza matriz de impacto × urgência nem níveis P1/P2/P3/P4 como regra oficial de priorização.

No momento da criação do chamado, o SLA aplicável é obtido da categoria e preservado no próprio chamado. Alterações posteriores da categoria não modificam retroativamente o SLA já aplicado ao chamado.

A contagem de SLA continua nos estados de espera. `Resolvido`, `Encerrado` e `Cancelado` interrompem a contagem conforme as regras do projeto. O comportamento de retomada do SLA quando uma solução é rejeitada deverá ser formalizado na especificação correspondente antes da implementação dessa etapa.

### 6.6 Atribuição e tratativa

Um chamado pode existir sem Técnico responsável.

Quando um Técnico assume um chamado:

- a atribuição é registrada;
- o momento da atribuição é registrado;
- o status não é alterado automaticamente;
- repetir a mesma assunção pelo mesmo Técnico não cria uma nova atribuição.

Chamados não atribuídos podem ser assumidos por um Técnico. Técnicos, Diretoria e Administrador também podem atribuir ou reatribuir chamados a outro Técnico, desde que o chamado não esteja em estado terminal.

Um Técnico pode retirar sua própria atribuição. Nesse caso, o chamado volta a ficar sem Técnico responsável e mantém o status atual.

Toda atribuição, reatribuição ou liberação deve fazer parte do histórico do chamado.

### 6.7 Ciclo de vida dos chamados

Os status previstos para o domínio do MIRA são:

- `Novo`;
- `Em Atendimento`;
- `Aguardando Solicitante`;
- `Aguardando Mudança`;
- `Resolvido`;
- `Solução Rejeitada`;
- `Encerrado`;
- `Cancelado`.

O solicitante não altera diretamente o status.

Técnico, Diretoria e Administrador podem alterar o status de chamados não terminais. Toda alteração de status exige uma atualização registrada no histórico.

`Cancelado` é terminal: depois do cancelamento, o chamado não pode ser reaberto nem editado.

`Encerrado` também é terminal. Se o problema voltar após o encerramento, deve ser criado um novo chamado.

`Resolvido` e `Encerrado` representam fases distintas:

- `Resolvido`: a solução técnica foi aplicada e o serviço foi considerado restaurado;
- `Encerrado`: a resolução foi aceita ou o prazo de fechamento automático expirou.

Após três dias em `Resolvido`, o sistema pode alterar automaticamente o chamado para `Encerrado`, desde que a solução não tenha sido rejeitada.

Quando um solicitante humano entende que o problema persiste, pode rejeitar a resolução. A rejeição exige comentário obrigatório e altera o status para `Solução Rejeitada`, sem alterar automaticamente os demais dados do chamado.

O status `Aguardando Solicitante` é definido por Técnico, Diretoria ou Administrador e exige comentário público. O comentário posterior do solicitante atualiza o chamado, mas não muda automaticamente seu status.

O status `Aguardando Mudança` também é definido pelos perfis com permissão de tratativa e permanece até que um desses perfis altere o estado.

### 6.8 Comentários e histórico

O chamado possui uma linha do tempo única de acompanhamento.

Comentários registram, conceitualmente:

- autor;
- data e hora;
- conteúdo;
- visibilidade.

Comentários feitos pelo solicitante são visíveis às partes autorizadas do atendimento.

Comentários feitos por Técnico, Diretoria ou Administrador podem ser:

- gerais, visíveis também ao solicitante;
- privados, visíveis apenas a Técnico, Diretoria e Administrador.

Mudanças relevantes, como alteração de status, atribuição, reatribuição e liberação, devem gerar eventos estruturados no histórico, mesmo quando apresentados ao usuário na mesma linha do tempo de comentários.

Toda inclusão de comentário atualiza a data de última atualização do chamado.

Mudanças para `Resolvido`, `Aguardando Solicitante` e `Cancelado` exigem comentário público.

### 6.9 Consulta, busca e filtros

As listagens de chamados devem permitir filtros compatíveis com o escopo de cada perfil.

Entre os critérios previstos estão:

- número do chamado;
- status;
- Totem;
- data de abertura;
- data da última atualização.

Técnicos podem visualizar todos os chamados e filtrá-los independentemente de estarem atribuídos a eles.

Gerentes podem consultar e filtrar todos os chamados pertencentes à própria loja.

Os filtros selecionados pelo usuário funcionam como preferência persistente: permanecem aplicados entre navegações e sessões até que o próprio usuário execute a ação de **Limpar filtros**.

O detalhamento técnico de armazenamento dessas preferências pertence à especificação da funcionalidade correspondente.

### 6.10 Dashboards e indicadores

A Diretoria terá visões consolidadas e interativas para acompanhamento da operação.

Os dashboards previstos incluem:

- **Disponibilidade Geral da Rede** — acompanhamento do tempo em que os Totens permaneceram Online e Offline;
- **Evolução de MTTD versus MTTR**;
- **Volumetria de Chamados por Status**;
- **Termômetro de SLA**, para acompanhamento do consumo do prazo e risco de violação;
- **Top 5 Lojas com Maior Volume de Incidentes**;
- **Maiores Causas de Indisponibilidade**, utilizando a categoria do chamado como referência de causa;
- **Análise de Recorrência**, considerando repetição de chamados com base na categoria.

Para viabilizar esses indicadores, o domínio precisa preservar informações temporais e relacionamentos suficientes para identificar, conforme cada métrica:

- Totem;
- Loja;
- categoria;
- status do chamado;
- prioridade;
- data de criação;
- data de última atualização;
- SLA aplicado;
- eventos de mudança de status;
- momento de detecção da indisponibilidade;
- retorno do Totem a Online;
- períodos de disponibilidade.

O cálculo exato e os recortes de cada indicador devem ser formalizados nas specs das respectivas funcionalidades de dashboard, evitando antecipar detalhes desnecessários no contexto global.

---

## 7. Requisitos e restrições importantes

- `evento_timestamp` é a referência temporal dos eventos de telemetria.
- A ausência de heartbeat é avaliada com limite de 15 minutos.
- O Fiscal apenas dispara a verificação; as decisões de indisponibilidade e criação de incidente pertencem ao Xano.
- O Simulator apenas gera telemetria para Totens existentes.
- O retorno da telemetria não encerra automaticamente um chamado.
- A abertura manual permanece necessária para problemas físicos ou operacionais não representados adequadamente pela telemetria.
- Cada novo chamado está relacionado a exatamente um Totem.
- Um mesmo problema que afeta vários Totens gera um chamado por Totem.
- O SLA aplicado deve ser preservado no chamado.
- O projeto não utiliza matriz de impacto × urgência como regra de prioridade.
- `Encerrado` e `Cancelado` são estados terminais.
- Registros históricos podem não possuir informações introduzidas em evoluções posteriores do projeto.
- Dados históricos não devem ser inventados, preenchidos retroativamente ou alterados por backfill sem uma change aprovada.
- O projeto deve utilizar somente funcionalidades disponíveis no plano Free do Xano, salvo decisão humana explícita em contrário.

---

## 8. Arquitetura tecnológica

### 8.1 Reflex

Responsável pela aplicação web, incluindo:

- autenticação e navegação visual;
- Service Desk;
- formulários e listagens;
- páginas de dashboards;
- interação dos usuários com os dados expostos pelo backend.

A interface não substitui mecanismos de autorização do backend.

### 8.2 Xano

Responsável por:

- backend;
- persistência;
- autenticação e autorização;
- APIs;
- agregações;
- regras de negócio.

As decisões críticas de domínio e autorização devem permanecer no backend.

### 8.3 Python Simulator

Responsável por gerar e enviar telemetria simulada para Totens já cadastrados.

Não cadastra Totens e não cria chamados.

### 8.4 Python Fiscal

Responsável por disparar periodicamente a verificação de heartbeat.

Não decide se um Totem está Offline e não cria incidentes diretamente.

### 8.5 OpenSpec e agentes de desenvolvimento

O desenvolvimento do projeto utiliza OpenSpec para organizar a evolução incremental do sistema.

O Codex e os agentes especializados definidos pelo projeto auxiliam planejamento, revisão e implementação conforme as instruções de `AGENTS.md` e `agents/`.

O Xano Developer MCP apoia consultas e validações relacionadas ao XanoScript, e o Xano CLI é utilizado nas atividades de sincronização operacional previstas pelo projeto.

---

## 9. Segurança, autorização e integridade

A autenticação e a autorização são responsabilidades do Xano.

Os perfis humanos do sistema são:

- Gerente;
- Técnico;
- Diretoria;
- Administrador do Sistema.

O Bot de Fiscalização é um ator de sistema utilizado como solicitante de chamados automáticos e não representa um perfil humano autenticável.

As permissões devem ser aplicadas no backend e não apenas por ocultação de componentes na interface.

O Gerente possui escopo restrito à própria loja.

Técnico, Diretoria e Administrador possuem escopo global conforme suas responsabilidades.

Credenciais e segredos não são tratados como dados comuns do domínio no frontend e devem seguir os mecanismos próprios de autenticação e configuração segura.

---

## 10. Princípios de desenvolvimento

O projeto adota os seguintes princípios:

- fornecer contexto suficiente antes de implementar;
- evoluir o sistema de forma incremental;
- especificar mudanças relevantes antes da implementação;
- utilizar OpenSpec como processo de evolução das funcionalidades;
- manter separadas as responsabilidades de Reflex, Xano, Simulator e Fiscal;
- evitar duplicação de regras de negócio;
- preservar integridade dos dados históricos;
- não inventar regras de negócio para preencher lacunas;
- manter o projeto compatível com as restrições acadêmicas e com o plano Free do Xano;
- evitar complexidade técnica que não traga benefício proporcional ao escopo acadêmico.

---

## 11. Estratégia de desenvolvimento

O projeto segue o ciclo:

```text
Contexto
   ↓
Explore
   ↓
Propose
   ↓
Review
   ↓
Apply
   ↓
Archive
   ↓
Próxima Change
```

Cada change deve representar uma evolução funcional ou técnica delimitada, revisável e verificável.

Mudanças no domínio global podem orientar as próximas evoluções do produto, mas não devem ser tratadas como funcionalidades já implementadas.

Changes arquivadas preservam o histórico das decisões tomadas naquele momento e não devem ser reescritas para representar decisões posteriores.

Quando uma nova definição do domínio exigir alteração do comportamento consolidado, a evolução deve ocorrer por uma nova change.

---

## 12. Fonte de verdade e documentação

Os documentos possuem responsabilidades diferentes:

- `docs/project-overview.md`: visão global do projeto, seu problema, objetivos, escopo, usuários, funcionalidades, restrições e arquitetura;
- `docs/domain-model.md`: conceitos fundamentais, relacionamentos e regras estruturais do domínio;
- `AGENTS.md`: regras operacionais para agentes de IA que trabalham no repositório;
- `agents/`: instruções especializadas por papel de agente;
- `openspec/config.yaml`: contexto curto e permanente fornecido aos workflows do OpenSpec;
- `openspec/specs/`: comportamento consolidado pelas changes concluídas;
- `openspec/changes/`: mudanças em planejamento ou implementação;
- `openspec/changes/archive/`: histórico das mudanças concluídas.

O Project Overview e o Domain Model descrevem a visão global adotada para orientar a evolução futura do MIRA.

Quando uma decisão global mais recente ainda não estiver implementada nas specs consolidadas, ela deve orientar a criação de uma nova change, e não a alteração retroativa das changes arquivadas.
