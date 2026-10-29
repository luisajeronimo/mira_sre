# Proposal: complementos da consulta e do detalhe de chamados

## Why

Os filtros diferem entre filas, não cobrem a última atualização e o Gerente
ainda perde seus critérios entre sessões. Além disso, o acesso ao contexto do
Totem a partir do chamado não leva os perfis globais ao detalhe persistente do
Monitoramento nem oferece ao Gerente uma consulta local autorizada.

## What Changes

- Padronizar em todas as filas os filtros básicos de número, Status, Totem,
  abertura e última atualização, persistindo os critérios confirmados por
  usuário até Limpar filtros. Os filtros globais adicionais, ordenação e
  escopos existentes são preservados.
- Incluir Loja como coluna, filtro server-side e ordenação alfabética na fila
  compartilhada de Técnico, Diretoria e Administrador, persistindo o critério
  e a ordenação por usuário e escopo; o Gerente continua limitado à própria
  Loja.
- Adicionar em detalhes globais um botão que navega para
  `/monitoramento?totem=<id>`, com o Totem selecionado mesmo após recarga.
- No detalhe do Gerente, substituir a telemetria no corpo por botão que abre
  drawer nativo com Totem, Loja, estado e última telemetria autorizados pela
  Loja; não concede acesso à rota global de Monitoramento.

## Capabilities

### New Capabilities

- `preferencias-filtros-gerente`: preferência durável dos filtros confirmados
  da lista local do Gerente.

### Modified Capabilities

- `chamados-abertura-manual`: filtros da Loja incluem última atualização e o
  detalhe local fornece o resumo do Totem necessário ao drawer.
- `chamados-fila-atribuicao-tecnica`: fila global ganha Loja e período da
  última atualização; detalhes encaminham ao Monitoramento existente.
- `frontend-chamados-gerente`: a jornada local restaura todos os filtros
  básicos e abre o drawer autorizado do Totem.
- `monitoramento-disponibilidade-totens`: a rota restaura seleção de Totem
  pela URL sem criar nova rota ou contrato.

## Impact

- Reflex: filtros/State compartilhado, catálogo global de Totens com Loja,
  URL de seleção no Monitoramento e drawer nativo do Gerente.
- Xano: filtros e preferências adicionais, projeção de Loja na fila global e
  resumo mínimo do Totem no detalhe da Loja.
- Não há alteração de SLA, papéis, Simulator, Fiscal, cálculos, gráficos ou
  novos históricos de telemetria; somente a ordenação já persistida da fila
  global passa a aceitar a coluna Loja.

## Decisões humanas pendentes

Nenhuma. O drawer do Gerente fica limitado ao resumo atual autorizado de seu
Totem, enquanto o detalhe completo permanece na rota já autorizada aos perfis
globais.
