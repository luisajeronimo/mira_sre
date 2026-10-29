# Tasks

## 1. Filtros e preferências no Xano

- [x] 1.1 Estender a preferência existente e os contratos de lista/salvamento com período da última atualização e, na fila global, Loja; validar XanoScript para filtros combinados, dados legados nulos, escopos existentes e 422 de critério inválido.
- [x] 1.2 Implementar os contratos exclusivos do Gerente para os cinco filtros básicos e limitar Totem/consulta à própria Loja; verificar leitura ausente, save, limpeza, retorno após login e 403 de outro perfil.

## 2. Fila e detalhe no Reflex

- [x] 2.1 Atualizar cliente, States e filtros das duas filas: básicos iguais, filtros globais extras preservados, Loja/última atualização persistidos e coluna Loja global; cobrir restauração, aplicar, limpar e isolamento de Loja nos testes focados de lista.
- [x] 2.2 Enriquecer o catálogo global de Totens com Loja e derivar suas opções sem endpoint novo; cobrir DTO e filtro Loja server-side em testes do cliente e da fila técnica.
- [x] 2.3 Fazer o botão global navegar para `/monitoramento?totem=<id>` e restaurar/carregar esse detalhe após recarga; cobrir parâmetro válido, inválido e não autorizado nos testes de Monitoramento.
- [x] 2.4 Retornar resumo autorizado do Totem no detalhe do Gerente e apresentá-lo apenas em drawer nativo fechável; cobrir abertura, fechamento, telemetria ausente e negação por Loja sem liberar `/monitoramento`.
- [x] 2.5 Tornar Loja ordenável na fila global, incluindo whitelist/ordenação no Xano, preferência por usuário+escopo, cabeçalho e teste de alternância ASC/DESC com desempate por ID.
- [x] 2.6 Corrigir a composição do drawer nativo do Gerente com direção direita, portal, overlay, superfície e rolagem interna; cobrir X, telemetria com timestamp e ausência sem liberar `/monitoramento`.
- [x] 2.7 Manter a whitelist de ordenação do contrato Reflex alinhada à preferência Xano, aceitando `loja` persistida em ASC e DESC; cobrir a regressão sem alterar os demais campos.

## 3. Verificações focadas

- [x] 3.1 Executar somente testes alterados de lista do Gerente, fila técnica, cliente/detalhe e Monitoramento, incluindo persistência e navegação; confirmar SLA e ordenação existentes preservados.
- [x] 3.2 Executar compilação Reflex, validação dos recursos Xano alterados, OpenSpec strict, `git diff --check` e `xano workspace push --dry-run`; registrar recursos pendentes sem publicar.
- [x] 3.3 Executar testes focados das duas correções, compilação Reflex, validação Xano, OpenSpec strict, `git diff --check` e dry-run sem publicar; registrar os recursos Xano pendentes.
