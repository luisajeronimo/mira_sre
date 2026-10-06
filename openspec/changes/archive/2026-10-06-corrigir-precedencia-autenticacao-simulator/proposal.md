# Proposal

## Why

A validação runtime comprovou que `POST /telemetria_equipamentos` valida campos obrigatórios do payload antes de executar o guard de `X-MIRA-Simulator-Key`. Assim, requisições sem chave ou com chave inválida e payload incompleto retornam HTTP 400, contrariando o contrato consolidado de rejeição uniforme HTTP 401 sem expor detalhes funcionais.

## What Changes

- Reestruturar exclusivamente a entrada do endpoint do Simulator para que a autenticação técnica seja avaliada antes da validação de presença dos campos funcionais da telemetria.
- Preservar a resposta pública exata `{"error":"Não autenticado."}` com HTTP 401 para chave ausente, inválida ou configuração ausente, inclusive quando o payload estiver incompleto.
- Manter, após autenticação válida, a rejeição funcional de payload incompleto e o fluxo atual de persistência para telemetria válida.
- Adicionar regressões locais, validação XanoScript e evidência runtime segura para as ordens de validação autenticada e não autenticada.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `autenticacao-automacoes`: explicitar que a autenticação técnica do Simulator precede a validação funcional de presença do payload.

## Impact

- XanoScript: somente `POST /telemetria_equipamentos` e testes estritamente relacionados.
- Runtime: preserva URL, método, formato de telemetria válida, ciclo do Simulator e o contrato do Fiscal.
- Fora de escopo: heartbeat, incidentes, dados persistidos, frontend, perfis humanos, autenticação do Fiscal, frequência operacional e demais pendências da validação da Sprint 1.
