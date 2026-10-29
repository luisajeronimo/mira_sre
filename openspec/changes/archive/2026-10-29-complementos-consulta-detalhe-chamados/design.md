# Design: complementos da consulta e do detalhe de chamados

## Context

Veja `proposal.md`. Gerente possui quatro filtros locais sem preferência;
Técnico, Diretoria e Administrador compartilham fila com preferência, filtros
extras e ordenação persistida. A tabela existente já isola preferências por
usuário+escopo, mas não armazena Loja nem período de última atualização. A
fila global já junta Loja internamente, e o Monitoramento já possui detalhe
completo, porém sua seleção só vive no State e a rota não autoriza Gerente.

## Goals / Non-Goals

**Goals:**

- Reutilizar tabela, upsert, escopos e consulta candidata existentes.
- Acrescentar somente filtros e projeções exigidos, mantendo autorização no
  Xano e ordenação atual.
- Reutilizar a página de Monitoramento para perfis globais e `rx.drawer` para
  o resumo local do Gerente.

**Non-Goals:**

- Remover filtros globais já aprovados, persistir ordenação do Gerente, criar
  catálogo de Loja, rota de Monitoramento para Gerente, cálculo, gráfico ou
  histórico adicional de telemetria.

## Decisions

### Preferências absorvem os novos critérios sem alterar escopos

A tabela existente recebe somente `lojas_id`, `ultima_atualizacao_inicio` e
`ultima_atualizacao_fim`. Os contratos técnico existentes passam esses campos
no mesmo registro por usuário+escopo e preservam sua ordenação. Os dois
contratos exclusivos do Gerente usam seu registro `todos`, guardam apenas os
cinco filtros básicos e mantêm a ordenação local atual.

Aplicar e Limpar consultam a candidata antes do save. Ao entrar, navegar ou
autenticar novamente, o State recupera somente filtros confirmados. Intervalos
usam início inclusivo e fim exclusivo do dia seguinte, tanto para abertura
quanto para última atualização, e o Xano valida Totem/Loja antes de consultar
ou persistir.

### Loja global reaproveita catálogo e join já existentes

`listar_chamados_tecnico` já junta `lojas`; sua projeção/DTO passa a incluir
Loja, aceitar `loja_id` e filtrá-la no Xano. `GET /tecnico/ativos` passa a
projetar a Loja já relacionada a cada Totem, permitindo derivar opções únicas
no Reflex sem novo endpoint de catálogo. O filtro de Loja é válido para os
três perfis globais e é persistido no registro existente.

A ordenação global amplia a whitelist já persistida com `loja`. O Xano ordena
pelo nome de Loja normalizado para minúsculas e desempata por ID do chamado,
em ambas as direções; o Reflex apenas solicita e restaura essa preferência por
usuário+escopo, sem reordenar a coleção local. A validação do contrato do
cliente aceita a mesma whitelist da preferência retornada pelo Xano, incluindo
`loja`, para não rejeitar a persistência válida após a consulta.

### Detalhe do Totem usa a fronteira de autorização correta

Perfis globais recebem botão com URL `/monitoramento?totem=<id>`. No carregamento,
`MonitoramentoState` valida a URL, carrega a lista já autorizada e consulta o
detalhe daquele Totem; a URL permanece na recarga. Não há novo endpoint nem
duplicação de telemetria no detalhe do chamado.

O detalhe do Gerente recebe Loja e resumo atual do Totem já autorizado pelo
chamado: identificação, estado e última telemetria opcional. O botão controla
um `rx.drawer` nativo com direção direita, portal e overlay; o conteúdo tem
superfície, largura desktop e rolagem interna, com fechamento por X
sincronizado ao State. Ele exibe o timestamp já retornado da última
telemetria, sem chamar o endpoint global de Monitoramento nem expor
históricos, transições ou incidentes.

## Risks / Trade-offs

- [Preferência legada sem novos campos] → tratá-los como nulos, preservando
  filtros existentes e sem backfill.
- [URL `totem` inválida ou inacessível] → manter a lista e mostrar erro de
  detalhe, sem selecionar ou fabricar Totem.
- [Totem/Loja removido ou fora do escopo] → Xano recusa filtro/detalhe antes de
  retornar dados; o State não confirma a preferência candidata.
- [Drawer confundir-se com Monitoramento] → limitar o conteúdo ao resumo atual
  e manter histórico completo exclusivamente na rota autorizada.

## Migration Plan

1. Estender schema/contratos Xano de filtros e preferências, DTO da fila global
   e resumo do detalhe local, com testes XanoScript de escopo e ausência.
2. Atualizar cliente/States/páginas, consulta da URL e drawer; cobrir
   persistência, filtro Loja, recarga e autorização local.
3. Executar testes focados, compilação Reflex, validação Xano, OpenSpec strict,
   `git diff --check` e dry-run Xano antes de qualquer publicação autorizada.

Rollback remove os campos/controles novos; campos opcionais persistidos ficam
inertes para versões anteriores e não exigem exclusão.
