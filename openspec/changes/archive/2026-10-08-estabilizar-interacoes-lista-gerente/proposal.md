# Proposal

## Problema

Após a lista operacional do Gerente já carregada, interações consecutivas que
solicitam nova consulta podem deixar a interface em estado de indisponibilidade.
A mensagem exibida não distinguia falha de transporte do canal de eventos,
limite transitório, erro do contrato ou expiração real da sessão. O diagnóstico
local disponível registra falhas de `ws://localhost:8000/_event/` e não fornece
evidência sanitizada de HTTP 429; portanto 429 não é assumido como causa única.

## Objetivo

Tornar determinístico o ciclo de consulta da lista do Gerente: uma consulta em
andamento não abre outra equivalente, uma intenção posterior não perde o
estado mais recente, falhas transitórias finalizam o loading e uma nova ação
consegue recuperar os dados. Somente uma resposta real de autenticação pode
limpar a sessão.

## O que muda

- classificar HTTP 429 separadamente, preservando `Retry-After` sanitizado;
- evitar que cada ordenação repita a carga do catálogo de ativos;
- coalescer intenções concorrentes de filtro/ordenação sem retry agressivo;
- manter a lista válida quando uma consulta secundária de catálogo falhar;
- cobrir recuperação após falha transitória, concorrência e múltiplas
  interações;
- preservar integralmente o contrato de ordenação já consolidado (texto
  case-insensitive, número numérico e datas cronológicas).

## Fora de escopo

- alteração do contrato de ordenação ou do Xano;
- alteração de autenticação, schema, records ou rotas;
- retry automático agressivo, `sleep` artificial ou debounce visual;
- mudanças em detalhes, comentários, abertura de chamados ou paginação;
- correção de falhas do ambiente local do servidor Reflex fora do ciclo do
  State.

## Impacto

O cliente HTTP centralizado e `ChamadosGerenteState` passam a distinguir limite
transitório de contrato inválido e a controlar concorrência. O backend Xano e o
modelo de dados permanecem intactos.
