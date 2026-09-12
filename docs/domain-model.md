# Modelo de Domínio — MIRA

## 1. Objetivo

Este documento descreve os conceitos fundamentais do domínio do MIRA e os relacionamentos entre eles.

O objetivo é permitir que pessoas e agentes de IA compreendam **quais elementos existem no sistema e como se relacionam**, sem transformar este arquivo em um modelo físico do banco de dados ou em uma documentação de API.

## 2. Visão conceitual

O MIRA organiza uma rede de restaurantes que possui totens de autoatendimento. Esses ativos produzem telemetria, podem ficar indisponíveis e podem estar relacionados a chamados de atendimento.

Os usuários do sistema atuam conforme seu perfil:

- **Gerente** acompanha os ativos da unidade, abre chamados manuais e acompanha a tratativa;
- **Técnico** trabalha na fila de chamados, assume atendimentos, registra informações da tratativa e resolve chamados;
- **Diretoria** consulta dashboards e indicadores consolidados.

A relação central do domínio pode ser resumida assim:

```text
Loja
 └── Ativo
      ├── Telemetria
      └── Chamado
           ├── Categoria de Serviço
           └── Interações

Usuário
 ├── abre/acompanha Chamados
 ├── pode assumir/tratar Chamados
 └── registra Interações
```

## 3. Loja

Representa uma unidade da rede de restaurantes.

### Responsabilidade

Organizar os ativos e permitir análises operacionais por unidade e região.

### Principais informações conceituais

- identificação da unidade;
- nome;
- localização/endereço;
- região;
- situação da unidade.

### Relacionamentos

- uma loja pode possuir vários ativos;
- chamados relacionados a um ativo podem ser associados à respectiva loja por meio desse ativo;
- indicadores podem ser agregados por loja e região.

## 4. Usuário

Representa uma pessoa autorizada a utilizar o MIRA.

### Responsabilidade

Identificar quem acessa o sistema e qual papel essa pessoa exerce no fluxo operacional.

### Principais informações conceituais

- identificação;
- nome;
- e-mail;
- perfil de acesso.

### Perfis

#### Gerente

- visualiza os ativos da unidade;
- abre chamados manuais para problemas físicos ou operacionais;
- acompanha o andamento dos chamados.

#### Técnico

- visualiza a fila de atendimento;
- assume chamados;
- consulta informações do ativo e da telemetria;
- registra diagnóstico e work logs;
- registra solução e resolve chamados.

#### Diretoria

- consulta dashboards e indicadores consolidados;
- acompanha disponibilidade, SLA, MTTD, MTTR, incidentes e recorrência.

### Autenticação

A autenticação e a autorização são responsabilidades do Xano.

### Relacionamentos

- um usuário pode abrir chamados como solicitante;
- um usuário técnico pode assumir chamados;
- um usuário pode registrar interações em chamados.

## 5. Ativo

Representa um totem de autoatendimento cadastrado no sistema.

### Responsabilidade

Ser o elemento monitorado pelo MIRA e o ponto de associação entre telemetria, disponibilidade e chamados.

### Principais informações conceituais

- identificação do ativo;
- nome;
- tipo;
- loja onde está instalado;
- status atual.

### Relacionamentos

- cada ativo pertence a uma loja;
- um ativo pode possuir muitos eventos de telemetria;
- um ativo pode possuir vários chamados ao longo do tempo.

## 6. Telemetria

Representa um evento técnico produzido por um ativo.

### Responsabilidade

Registrar informações de saúde e comunicação do totem para acompanhamento operacional e detecção de indisponibilidade.

### Principais informações conceituais

- ativo de origem;
- uso de CPU;
- uso de memória;
- temperatura;
- status de rede;
- `evento_timestamp`.

### Regras estruturais

- cada evento de telemetria pertence a um ativo existente;
- `evento_timestamp` é a referência temporal do evento;
- o Simulator produz telemetria para ativos já cadastrados;
- a telemetria é persistida no Xano.

## 7. Categoria de Serviço

Representa a classificação de um chamado.

### Responsabilidade

Organizar os tipos de atendimento e fornecer o parâmetro de SLA aplicável ao chamado.

### Principais informações conceituais

- nome da categoria;
- classificação ITIL utilizada pelo projeto;
- parâmetro de SLA em horas.

### Relacionamentos

- uma categoria pode classificar vários chamados;
- cada chamado referencia uma categoria para determinar a classificação e o SLA aplicável.

## 8. Chamado

Representa um incidente ou uma requisição tratada pelo Service Desk.

### Responsabilidade

Registrar e acompanhar uma necessidade de atendimento relacionada à operação dos totens.

### Origem funcional

Um chamado pode surgir de duas formas já previstas no MIRA:

- **manual**, quando o gerente identifica um problema físico ou operacional;
- **automática**, quando o Xano identifica uma indisponibilidade por ausência de heartbeat e cria um incidente quando não existe outro equivalente aberto.

A distinção funcional entre esses dois fluxos já existe. A forma de persistir essa origem deve seguir a especificação aprovada correspondente.

### Principais informações conceituais já consolidadas

- identificação;
- título;
- status;
- prioridade;
- solicitante;
- técnico responsável, quando atribuído;
- ativo relacionado;
- categoria de serviço;
- momento de criação.

A documentação também exige que o gerente descreva o problema durante a abertura manual, mas a persistência dessa descrição deve seguir a change que formalizar essa evolução do modelo.

### Relacionamentos

- um chamado pode estar relacionado a um ativo;
- um chamado possui uma categoria de serviço;
- um chamado possui um solicitante;
- um chamado pode possuir um técnico responsável;
- um chamado pode possuir várias interações.

## 9. Interação de Chamado

Representa um registro feito durante o acompanhamento ou a tratativa de um chamado.

### Responsabilidade

Preservar work logs e comunicação associados ao atendimento.

### Principais informações conceituais

- chamado relacionado;
- autor;
- conteúdo/mensagem;
- momento do registro.

### Relacionamentos

- cada interação pertence a um chamado;
- cada interação possui um autor;
- um chamado pode possuir várias interações ordenadas ao longo do tempo.

O técnico já possui como atividades registrar diagnóstico, work log e solução. A forma de persistir diagnóstico e solução além dos registros já existentes deve ser definida pela respectiva change antes de qualquer alteração do modelo.

## 10. Monitoramento de Heartbeat

O heartbeat não é uma entidade independente do domínio, mas uma regra operacional baseada nos eventos de telemetria.

O fluxo consolidado é:

1. o Simulator envia telemetria dos ativos cadastrados;
2. o Fiscal dispara periodicamente a verificação;
3. o Xano consulta a telemetria mais recente;
4. se houver mais de 15 minutos sem telemetria, o Xano pode marcar o ativo como Offline;
5. o Xano verifica se já existe incidente equivalente aberto;
6. quando necessário, cria um incidente `Novo/Urgente` sem duplicidade.

O Fiscal não decide o status do ativo e não cria o chamado diretamente.

## 11. SLA

O SLA é associado à categoria de serviço.

A categoria fornece o parâmetro `sla_horas`, e o chamado referencia sua categoria para determinar o SLA aplicável.

O projeto não possui tempos fixos de SLA por níveis P1/P2/P3/P4 definidos como regra oficial. Também não existe uma matriz de impacto e urgência aprovada no modelo atual.

## 12. Relações consolidadas

```text
Loja 1 ─── N Ativo

Ativo 1 ─── N Telemetria
Ativo 1 ─── N Chamado

Categoria de Serviço 1 ─── N Chamado

Usuário 1 ─── N Chamado como solicitante
Usuário 1 ─── N Chamado como técnico responsável

Chamado 1 ─── N Interação
Usuário 1 ─── N Interação como autor
```

Essas relações representam o domínio consolidado. Alterações futuras devem ser formalizadas por meio de uma change do OpenSpec antes de serem tratadas como parte do comportamento vigente.
