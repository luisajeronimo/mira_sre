# Proposta: fila de distribuição de chamados

## Why

A fila técnica precisa oferecer a Técnico, Diretoria e Administrador uma visão global confiável da distribuição e consulta dos chamados, sem divergir dos filtros explícitos usados na jornada do Gerente. A consulta também precisa preservar o responsável atual, a data de atribuição e o histórico legado no detalhe canônico.

## What Changes

- Alinhar a fila existente ao padrão da listagem do Gerente: uma tabela global com filtros explícitos de número, status, Totem e período; sem filtros, `Todos` representa todos os chamados globais.
- Manter somente os escopos de navegação aprovados: `Todos` para os perfis globais e `Atribuídos a mim` como escopo rápido exclusivo do Técnico, sem visões específicas para chamados atribuídos a outros Técnicos ou não atribuídos.
- Exibir responsável atual e `atribuido_em` na fila e no detalhe global canônico.
- Apresentar comentários existentes e eventos legados estruturados de atribuição, reatribuição e liberação em uma única timeline cronológica.
- Manter a fila e o detalhe Reflex existentes, com DTO único e contrato de consulta validado contra respostas reais do Xano.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-fila-atribuicao-tecnica`: evoluir a consulta global, os filtros, a visibilidade do responsável e a timeline compatível da fila existente.
- `autorizacao-perfis`: autorizar no Xano a consulta global por Técnico, Diretoria e Administrador, sem ampliar a jornada do Gerente.

## Impact

- **Reflex:** página, `ChamadosTecnicoState`, service de Service Desk e detalhe técnico existentes.
- **Xano:** listagem e detalhe técnicos, autorização por perfil e consulta estruturada de `interacoes_chamado`.
- **Dados:** reutilização de `chamados.tecnico_id` e `chamados.atribuido_em`, além da leitura compatível de eventos históricos em `interacoes_chamado`, sem backfill ou tabela de auditoria paralela.
- **Fora do escopo:** tratativa operacional e a gestão de responsável. Essa gestão foi posteriormente substituída pela change `tratativa-operacional-chamados`.
