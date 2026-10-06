# Tasks

## 1. Diagnóstico e contrato

- [x] 1.1 Reproduzir de forma segura a rejeição atual de chave ausente e inválida com payload incompleto, registrando somente status e corpo sanitizado para confirmar o defeito runtime.
- [x] 1.2 Confirmar no endpoint, na documentação Xano e na spec que a obrigatoriedade declarada em `input` antecede o `stack`, e verificar que a solução proposta permanece compatível com o plano Free.
- [x] 1.3 Manter a delta spec, proposal e design coerentes com a correção exclusiva de precedência, verificando `openspec validate corrigir-precedencia-autenticacao-simulator --strict`.

## 2. Correção do endpoint e regressões locais

- [x] 2.1 Tornar os campos funcionais da telemetria opcionais na entrada e exigir sua presença somente após o guard técnico, verificando que nenhuma leitura ou escrita antecede o guard.
- [x] 2.2 Preservar a resposta HTTP 401 com corpo público exato para chave ausente, inválida ou configuração ausente e payload incompleto, cobrindo o contrato em testes locais.
- [x] 2.3 Preservar a validação funcional de payload incompleto após chave válida, sem persistência e sem resposta 401, cobrindo a regressão em testes locais.
- [x] 2.4 Preservar URL, método e telemetria válida do Simulator, cobrindo o fluxo normal em testes locais sem registrar credenciais.
- [x] 2.5 Executar regressão do Fiscal e confirmar que sua autenticação, resposta 401 e contrato operacional não foram alterados.

## 3. Validação Xano e publicação controlada

- [x] 3.1 Validar o XanoScript alterado com Xano Developer MCP/parser e confirmar que somente recursos Free existentes foram usados.
- [x] 3.2 Executar `xano workspace push --dry-run`, revisar que o preview contém somente o endpoint do Simulator e parar diante de qualquer recurso inesperado.
- [x] 3.3 Publicar a alteração estrutural somente após preview coerente e repetir o dry-run, verificando `No changes to push` sem usar records, delete, env ou sync.

## 4. Evidência runtime e encerramento

- [x] 4.1 Validar em runtime chave ausente e inválida com payload incompleto, confirmando HTTP 401 e corpo público exato sem registrar chaves ou dados operacionais.
- [x] 4.2 Validar em runtime chave válida com payload incompleto, confirmando erro funcional sem persistência, e chave válida com payload completo, confirmando sucesso normal com telemetria de Totem existente.
- [x] 4.3 Confirmar em runtime que Fiscal continua rejeitando chave ausente e inválida com HTTP 401 e corpo público exato.
- [x] 4.4 Executar suíte completa, Reflex dry compile, OpenSpec strict, `git diff --check`, dry-run Xano, status e diff final, verificando ausência de mudança fora do escopo.
- [x] 4.5 Delegar revisão read-only ao mira-reviewer, verificando precedência de autenticação, contratos de erro, regressão do Fiscal, escopo, Free e ausência de segredos.
- [x] 4.6 Arquivar a change após aprovação do reviewer, sincronizando somente a delta de `autenticacao-automacoes` e validando as specs consolidadas.
