# MIRA

Plataforma acadêmica de **Service Desk + Observabilidade** para totens de autoatendimento.

O MIRA combina monitoramento técnico dos totens com abertura e tratamento de chamados, permitindo acompanhar falhas, disponibilidade e indicadores operacionais.

## Principais funcionalidades

- Recebimento de telemetria dos totens.
- Detecção de indisponibilidade por heartbeat.
- Abertura manual de chamados pelo gerente.
- Criação automática de incidentes pelo Xano.
- Fila técnica com atribuição e tratamento de chamados.
- Histórico de interações e work logs.
- SLA configurável por categoria de serviço.
- Dashboards de disponibilidade, incidentes, MTTD, MTTR e SLA.
- Filtros combináveis para a fila técnica, incluindo **Atribuídos a mim** e **Não atribuídos**.

## Tecnologias

- **Reflex** — frontend
- **Xano / XanoScript** — backend, banco de dados e regras de negócio
- **Python** — Simulator e Fiscal
- **OpenSpec** — especificação e evolução das funcionalidades
- **Codex + Xano Developer MCP** — apoio ao desenvolvimento e validação de XanoScript
- **Xano CLI** — sincronização entre os arquivos locais e o workspace Xano
- **GNU Make** — automação de comandos do ambiente

## Arquitetura resumida

```text
Gerente / Técnico / Diretoria
             |
           Reflex
             |
             | REST
             v
            Xano
        /           \
 Simulator          Fiscal
 telemetria      verificar-falhas
```

O **Simulator** apenas gera telemetria.  
O **Fiscal** apenas chama periodicamente `GET /verificar-falhas`.  
As regras de negócio, persistência e criação automática de incidentes ficam no **Xano**.

## Heartbeat

- Telemetria normal: a cada **7 minutos por ativo**.
- Mais de **15 minutos sem telemetria**: ativo marcado como `Offline`.
- Se não existir incidente aberto para a mesma falha, o Xano cria um chamado `Novo/Urgente`.
- Chamados duplicados para a mesma indisponibilidade devem ser evitados.

## Service Desk

O gerente pode abrir chamados para problemas físicos ou operacionais que não são necessariamente detectados pela telemetria.

O técnico pode consultar a fila, assumir chamados, registrar diagnóstico, work logs, solução e resolver o atendimento.

As categorias de serviço classificam os chamados e armazenam o parâmetro de SLA em `sla_horas`.


## OpenSpec e Codex

O projeto utiliza **Spec-Driven Development**.

Mudanças relevantes de regra de negócio, API ou banco devem passar pelo OpenSpec antes da implementação.

Fluxo:

```text
explore -> propose -> revisão -> apply -> archive
```

A configuração do Codex e do Xano Developer MCP fica versionada em:

```text
.codex/config.toml
```

As especificações ficam em:

```text
openspec/
```