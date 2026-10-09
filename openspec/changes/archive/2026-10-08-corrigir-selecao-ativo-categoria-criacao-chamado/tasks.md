# Tasks

## 1. Diagnóstico e contrato

- [x] 1.1 Rastrear seleção de ativo e categoria da UI ao State, validação e payload, documentando o contrato numérico já existente e verificando o fluxo com inspeção de código e testes direcionados.
- [x] 1.2 Confirmar que a correção não exige alteração de endpoint, schema, autorização ou records, verificando o cliente Xano e o diff dos arquivos afetados.

## 2. Implementação

- [x] 2.1 Manter catálogos de formulário com nome de apresentação e ID funcional separado, verificando que o formulário compile com os controles controlados pelo State.
- [x] 2.2 Fazer os eventos de seleção atualizarem as mesmas variáveis consumidas por `abrir_chamado` e converter IDs para inteiros positivos antes do payload, verificando o payload por teste unitário.
- [x] 2.3 Preservar rejeição de ativo/categoria ausentes ou inválidos sem request de criação, verificando os três cenários incompletos automatizados.

## 3. Validação e regressão

- [x] 3.1 Cobrir seleção completa, seleção incompleta, labels e payload numérico em `tests/test_gerente_lista_state.py`.
- [x] 3.2 Executar suíte completa, compilação Reflex, validações OpenSpec e `git diff --check`, registrando os resultados antes do Archive.
- [x] 3.3 Fazer revisão read-only da change e confirmar ausência de alterações em lista, ordenação, sessão, Xano, schema e records.
- [x] 3.4 Arquivar a change após todos os gates, verificar specs consolidadas e manter a aceitação manual final para a usuária.
