# Proposal

## Why

O filtro de Totem da lista do Gerente oferece Totens que passaram historicamente pela Loja, mesmo quando hoje pertencem a outra. Isso cria uma opção indevida e contratos inconsistentes: um Totem externo pode ser selecionado e salvo, mas a leitura da preferência o rejeita.

## What Changes

- O catálogo de opções do filtro de Totem passa a conter somente Totens vinculados à Loja atual do Gerente.
- Consulta e gravação dos filtros recusam Totens que não pertencem atualmente à Loja do Gerente, inclusive se houver vínculo histórico.
- A leitura de preferência anterior que contém Totem transferido projeta apenas os Totens atualmente elegíveis, sem reescrever o registro persistido nem bloquear a lista.
- A autorização histórica dos chamados permanece baseada na Loja do Totem no instante da abertura; chamados antigos autorizados continuam na lista sem filtro.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `preferencias-filtros-gerente`: alinhar as opções, a validação e a restauração efetiva do filtro de Totem à Loja atual.
- `frontend-chamados-gerente`: apresentar no filtro somente as opções atuais autorizadas, inclusive após restauração de preferência anterior.

## Impact

- State Reflex da lista do Gerente e cliente do Service Desk.
- Catálogo de Totens, consulta de chamados com filtro e contratos Xano de leitura e gravação da preferência.
- Testes de escopo da Loja, transferência e preferência persistida. Nenhuma entidade, campo, backfill ou recurso pago novo.

## Decisões humanas

A regra de opções do filtro restritas à Loja atual foi definida pelo usuário. Não há decisão adicional pendente para o Apply.
