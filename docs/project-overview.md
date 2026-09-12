# Project Overview — MIRA

## 1. Visão geral

O MIRA é uma plataforma acadêmica de **Service Desk e observabilidade** voltada ao acompanhamento de totens de autoatendimento de uma rede de restaurantes.

O sistema reúne informações de telemetria dos totens, acompanhamento de disponibilidade, abertura e tratamento de chamados e indicadores operacionais. O objetivo é integrar observabilidade e atendimento técnico em um único sistema, permitindo que eventos técnicos e problemas percebidos pelos usuários da operação façam parte do mesmo fluxo de acompanhamento.

## 2. Problema

Totens de autoatendimento podem apresentar indisponibilidade técnica, problemas físicos ou falhas operacionais.

Nem todos esses problemas podem ser detectados automaticamente apenas pela telemetria. Por isso, o MIRA combina dois mecanismos:

- monitoramento automático da comunicação e saúde dos ativos;
- registro manual de problemas físicos ou operacionais pelo gerente da unidade.

Os chamados resultantes são tratados pela equipe técnica e alimentam indicadores para acompanhamento gerencial.

## 3. Objetivos

O MIRA tem como objetivos:

- acompanhar a saúde e a disponibilidade dos totens;
- receber e consultar telemetria dos ativos;
- detectar ausência prolongada de comunicação;
- criar incidente automático quando uma indisponibilidade é confirmada e não existe incidente equivalente aberto;
- permitir abertura manual de chamado pelo gerente;
- oferecer uma fila de atendimento para a equipe técnica;
- registrar informações da tratativa;
- apresentar dashboards e indicadores para acompanhamento da operação.

## 4. Usuários

### Gerente da Loja

Responsável por acompanhar os ativos da unidade, abrir chamados manuais para problemas físicos ou operacionais e acompanhar a tratativa.

### Técnico

Responsável por visualizar a fila, assumir chamados, consultar informações do ativo e sua telemetria, registrar diagnóstico e work logs, registrar a solução e resolver chamados.

### Diretoria

Responsável por consultar dashboards globais e indicadores de disponibilidade, SLA, MTTD, MTTR, incidentes e recorrência.

## 5. Escopo

O escopo do MIRA compreende:

- autenticação e acesso conforme perfil;
- consulta de lojas e ativos;
- recepção e persistência de telemetria;
- acompanhamento do status dos ativos;
- fiscalização de heartbeat;
- abertura manual de chamados;
- criação automática de incidente por indisponibilidade;
- fila e tratativa técnica;
- histórico de interações;
- dashboards Geral, de Loja e de Ativo;
- indicadores operacionais e ITSM.

Os cadastros mestres necessários ao funcionamento do projeto permanecem persistidos no Xano e não são recriados pelo Simulator a cada execução.

## 6. Principais funcionalidades

### Telemetria e observabilidade

O Simulator em Python gera telemetria para ativos já cadastrados. Os eventos possuem informações de CPU, memória, temperatura, rede e `evento_timestamp`.

A telemetria é enviada ao Xano, onde é persistida e utilizada pelas consultas e dashboards.

### Heartbeat

O Fiscal em Python dispara periodicamente a verificação de falhas.

A regra de negócio permanece no Xano: quando a última telemetria de um ativo ultrapassa 15 minutos, o ativo pode ser marcado como Offline. Antes de criar um incidente automático, o Xano verifica se já existe incidente equivalente aberto, evitando duplicidade.

### Chamado manual

O gerente pode abrir chamado para problemas físicos ou operacionais mesmo quando o ativo continua enviando telemetria.

O fluxo manual inclui a seleção da loja, do ativo e da categoria, além do registro das informações necessárias para relatar o problema.

### Tratativa técnica

O técnico possui uma fila de chamados e pode assumir o atendimento, consultar o ativo e sua telemetria, registrar diagnóstico e work logs, registrar solução e resolver o chamado.

### Dashboards e indicadores

O MIRA possui visões consolidadas para a Diretoria, para uma Loja e para um Ativo.

Entre os indicadores já definidos estão:

- disponibilidade;
- ativos Online e Offline;
- incidentes;
- SLA compliance;
- MTTD;
- MTTR;
- incidentes por ativo e por loja;
- volume de chamados por categoria;
- recorrência.

## 7. Regras e restrições importantes

- `evento_timestamp` é a referência temporal da telemetria.
- Mais de 15 minutos sem telemetria caracteriza a condição usada pelo Xano para marcar o ativo como Offline.
- A criação automática de incidente deve evitar duplicidade para a mesma falha enquanto houver incidente equivalente aberto.
- O Fiscal apenas dispara a verificação; a decisão de Offline e a criação do incidente permanecem no Xano.
- O Simulator apenas produz telemetria; ele não cadastra ativos e não cria chamados.
- A abertura manual de chamado permanece necessária para problemas que não dependem da telemetria.
- O SLA é configurado pela categoria de serviço por meio do parâmetro `sla_horas`.
- Não há tempos fixos de SLA por P1/P2/P3/P4 definidos como regra oficial.
- Não há matriz de impacto e urgência aprovada como regra atual.

## 8. Arquitetura tecnológica

### Reflex

Responsável pela aplicação web, incluindo:

- login e navegação;
- Service Desk;
- páginas de dashboards;
- interação do usuário com os dados fornecidos pelo Xano.

### Xano

Responsável por:

- backend;
- banco de dados;
- autenticação e autorização;
- APIs;
- persistência;
- agregações;
- regras de negócio.

### Python Simulator

Responsável por gerar e enviar telemetria simulada para ativos já cadastrados.

### Python Fiscal

Responsável por disparar periodicamente a verificação de heartbeat.

### OpenSpec e Codex

O desenvolvimento do projeto utiliza OpenSpec para organizar mudanças incrementais e Codex como agente de apoio à implementação.

O Xano Developer MCP apoia a consulta e validação de XanoScript, enquanto o Xano CLI é utilizado para sincronização operacional com o workspace Xano.

## 9. Autenticação e autorização

O login e o controle de acesso são responsabilidades do Xano.

Os usuários possuem perfis de Gerente, Técnico ou Diretoria, e o sistema utiliza esses perfis para direcionar a navegação e as permissões correspondentes.

A documentação histórica do projeto representou uma `senha` como campo do cadastro de usuários utilizando o tipo de password do Xano. Para a visão de projeto e de domínio, credenciais não são tratadas como informação de negócio manipulada pelo frontend. O detalhamento de autenticação deve seguir os mecanismos próprios do Xano.

## 10. Princípios de desenvolvimento

- fornecer contexto suficiente antes da implementação;
- desenvolver de forma incremental;
- especificar mudanças relevantes antes de implementá-las;
- manter as responsabilidades de Reflex, Xano, Simulator e Fiscal separadas;
- evitar duplicação de regras de negócio;
- preservar decisões já consolidadas quando a mudança atual não exigir alteração.

## 11. Estratégia de desenvolvimento

O projeto utiliza o ciclo do OpenSpec:

```text
Explore
  ↓
Propose
  ↓
Revisão
  ↓
Apply
  ↓
Archive
```

Cada mudança deve ser delimitada, revisável e verificável.

A documentação global apresenta a visão estável do sistema. Detalhes específicos de novas funcionalidades ou alterações devem ser tratados na change correspondente.

## 12. Fonte de verdade e documentação

Os documentos possuem responsabilidades diferentes:

- `docs/project-overview.md`: visão geral do projeto;
- `docs/domain-model.md`: conceitos e relacionamentos do domínio;
- `AGENTS.md`: regras de trabalho para agentes de IA;
- `openspec/config.yaml`: contexto curto e permanente dos workflows OpenSpec;
- `openspec/specs/`: comportamento consolidado por meio das changes concluídas;
- `openspec/changes/`: mudanças atualmente em planejamento ou implementação.

Quando houver conflito entre documentação histórica e uma decisão mais recente formalmente consolidada, deve prevalecer a decisão vigente mais recente do projeto.
