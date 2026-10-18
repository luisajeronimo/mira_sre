# Proposal: filtros persistentes e ordenação de chamados

## Problema

A fila global perde filtros e ordenação fora do ciclo local do State e ainda
usa somente a ordenação fixa por número decrescente. Isso obriga cada usuário
a reconstruir a mesma consulta ao retornar ao sistema.

## Objetivo

Persistir no Xano, por usuário autenticado e escopo permitido, os filtros
operacionais aplicados e a ordenação da fila global. Permitir ordenação
server-side, estável e validada, sem mudar a jornada, os dados ou as permissões
de chamados.

## Escopo

- Técnico mantém preferências independentes para `Todos` e `Atribuídos a mim`.
- Diretoria e Administrador usam e persistem somente `Todos`.
- Persistir número, status, Totem, período, Prioridade e ordenação; rascunhos
  permanecem locais.
- Estender a consulta global para ordenação whitelistada no Xano.
- Normalizar Status sem diferenciar maiúsculas/minúsculas e persistir o valor
  canônico.

## Fora do escopo

- Jornada do Gerente, rotas, timeline, tratativa, paginação, busca avançada,
  infraestrutura adicional, recursos pagos e mudança de autorização de
  chamados.
- Persistir a seleção do escopo rápido: cada login inicia em `Todos`.
