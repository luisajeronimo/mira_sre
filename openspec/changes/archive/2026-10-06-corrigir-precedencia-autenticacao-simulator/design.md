# Design

## Context

Ver `proposal.md` para a motivação e a delta de `autenticacao-automacoes` para o contrato observável. No Xano, campos declarados como obrigatórios no bloco `input` são validados antes do `stack`. Como o guard de `X-MIRA-Simulator-Key` está no `stack`, uma requisição sem campos obrigatórios não o alcança.

## Goals / Non-Goals

**Goals:**

- Fazer o guard técnico decidir a requisição antes da validação funcional de presença da telemetria.
- Preservar o contrato de erro público 401 e o fluxo atual de telemetria válida.
- Manter a rejeição de payload incompleto depois de uma credencial válida, sem escrita.

**Non-Goals:**

- Alterar o formato bem-sucedido da telemetria, dados persistidos, headers, URL, método, Fiscal ou regras de heartbeat.
- Resolver as demais lacunas de validação runtime da Sprint 1.

## Decisions

### Declarar a presença da telemetria como opcional na fronteira

Os campos atuais permanecerão com seus tipos de telemetria, mas serão opcionais no `input`. Isso elimina a rejeição automática por ausência antes do `stack`, sem alterar o payload aceito quando completo. Logo após o guard válido, o endpoint aplicará uma pré-condição única que exige a presença de todos os campos funcionais antes de consultar o ativo ou persistir a telemetria.

Alternativa descartada: criar endpoint paralelo ou alterar a estrutura do payload. Ambas quebrariam o contrato de URL/formato ou ampliariam a superfície pública sem necessidade.

### Manter o guard no endpoint público

O guard continuará no próprio `POST /telemetria_equipamentos`, antes de qualquer acesso a `$input` funcional, consulta ou escrita. Ele preserva comparação de finalidade, falha fechada para configuração ausente e a resposta HTTP 401 pública exata.

Alternativa descartada: mover autenticação para componente novo. Não é necessária para a precedência de campos ausentes e adicionaria recursos fora do escopo/Free.

### Tratar presença como validação funcional posterior

A nova pré-condição de presença ocorre somente após autenticação válida e devolve erro funcional de entrada. A validação de tipo nativa do Xano permanece a responsabilidade da fronteira de API; esta change cobre o defeito runtime comprovado de campos ausentes/incompletos e não muda a semântica de valores completos válidos.

## Risks / Trade-offs

- [Pré-condição incompleta] → Cobrir todos os campos atuais e testar que não existe persistência quando faltar qualquer campo.
- [Regressão de payload válido] → Manter tipos, URL, método e resposta de sucesso; executar ciclo autenticado seguro após o push.
- [Exposição de detalhes antes do guard] → Testar em runtime chave ausente e inválida com payload incompleto, exigindo apenas o corpo público 401.
- [Recurso incompatível com Free] → A solução usa apenas `input`, condicionais e pré-condições já utilizados no endpoint; validar com MCP/parser antes do push.

## Migration Plan

1. Validar XanoScript e executar testes locais antes do preview.
2. Revisar `xano workspace push --dry-run`; ele deve conter somente o endpoint do Simulator.
3. Publicar somente após o preview coerente autorizado.
4. Executar chamadas runtime sem chave, com chave inválida, com chave válida/payload incompleto e com chave válida/payload válido, sem registrar a chave.
5. Se a regressão aparecer, interromper a validação e reverter pelo fluxo humano de mudança, sem alterar records.
