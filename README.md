# MIRA

Plataforma de ITSM e Observabilidade para monitoramento e gestão de totens de autoatendimento.

## Stack

- Reflex — Frontend
- Xano — Backend e banco de dados
- Grafana — Observabilidade
- Infinity — Integração Grafana → API REST do Xano
- Python — Simulação e fiscalização
- GNU Make — Automação
- Docker — Infraestrutura local

## Arquitetura

```text
Python Simulator
       |
       | POST /telemetria
       v
     Xano
       |
       +------------------+
       |                  |
       v                  v
    Reflex             Grafana
    ITSM              Observabilidade
