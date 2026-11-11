# Desempenho das listas do Gerente (achado M-3, 2026-11-08)

Análise sem alteração de código. Nenhuma medição foi feita no Xano (sem autorização de execução); os custos abaixo são contagens de operações por chamada.

## Situação

| Função | Leituras por chamada | Paginação |
|---|---|---|
| `service_desk/listar_chamados_gerente` (publicada) | 1 consulta de todos os chamados (com joins) + 1 consulta ao histórico por chamado (`resolver_loja_totem_no_instante`) | Não; devolve `{items, total}` completo |
| `service_desk/listar_ativos_historicos_gerente` (publicada) | 1 consulta de todos os Totens + 1 consulta `exists` ao histórico por Totem | Não |
| `service_desk/listar_chamados_loja_historica_gerente` (C-1, não publicada) | 1 consulta de todos os chamados + 1 consulta ao histórico por chamado com Totem e `criado_em` | Não (o contrato genérico não tem entrada) |

O custo é linear no total de chamados (ou Totens) do sistema, não no volume da Loja do Gerente. A autorização está correta em todas.

## Otimização segura proposta (não aplicada)

**Pré-filtro por Totens candidatos.** Antes do laço, uma única consulta:
`historico_vinculos_totem_loja` com `loja_destino_id == $usuario.lojas_id`, projetando `ativos_referencia_id` (Totens que alguma vez foram vinculados à Loja). No laço, o resolvedor só é chamado quando `$candidatos|in:$chamado.ativos_referencia_id`; os demais são descartados sem consulta.

**Equivalência (sem falso negativo nem falso positivo).** O resolvedor devolve `loja_destino_id` do vínculo mais recente com `efetivado_em <= criado_em`. Se esse valor é a Loja do Gerente, existe um vínculo do Totem com `loja_destino_id` igual à Loja, logo o Totem é candidato. Contrapositiva: Totem não candidato nunca resolve para a Loja do Gerente. Para candidatos, a decisão continua sendo do resolvedor, inalterada. O conjunto devolvido é idêntico.

**Ganho esperado.** De `1 + N` para `2 + K` consultas, em que `K` é o número de chamados de Totens que já passaram pela Loja. Para `listar_ativos_historicos_gerente`, a consulta `exists` por Totem é substituída pela mesma consulta única, com custo `2` consultas.

**O que não resolve.** A leitura de todos os chamados continua (filtrar a consulta por lista de Totens exige operador de pertença em `where`, cuja sintaxe não foi validada no MCP). Paginação mudaria o contrato de `GET gerente/chamados` e do Reflex e não é proposta aqui.

## Plano

1. Validar no Xano Developer MCP a sintaxe do pré-filtro (e, se existir, do operador de pertença em `where`).
2. Aplicar nas três funções, acrescentando o mock da consulta de candidatos em cada teste nativo existente e um teste novo em que o Totem não é candidato (resolvedor não chamado).
3. Teste local de equivalência com o modelo de referência (`tests/test_c1_gets_genericos_loja_historica.py` já contém o modelo da regra).
4. Publicação seletiva autorizada, com testes nativos e medição de tempo antes e depois em dados de teste.
