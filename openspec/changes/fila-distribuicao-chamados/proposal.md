# Proposta: fila de distribuição de chamados

## Why

A fila consolidada atende somente Técnicos, limita a consulta a chamados `Novo` e permite apenas autoatribuição. Isso não oferece a visão global de distribuição prevista para Técnico, Diretoria e Administrador nem permite acompanhar de forma auditável as mudanças de responsável.

## What Changes

- Ampliar a fila existente para consulta global por Técnico, Diretoria e Administrador, com pesquisa pelo número e identificação de chamados sem responsável, próprios e atribuídos a outros Técnicos.
- Permitir assumir, atribuir, reatribuir e liberar o Técnico responsável em chamados não terminais, preservando o status e validando no Xano que o responsável é Técnico.
- Preservar idempotência ao repetir `Assumir` pelo Técnico já responsável, sem renovar `atribuido_em` nem duplicar o evento.
- Apresentar comentários existentes e eventos estruturados de atribuição, reatribuição e liberação em uma única timeline cronológica.
- Aplicar a autorização e registrar a alteração do responsável e seu evento na mesma operação Xano.
- Manter a fila e o detalhe Reflex existentes, ampliando seus contratos e componentes conforme necessário.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-fila-atribuicao-tecnica`: evoluir consulta, visibilidade do responsável, atribuição e timeline da fila existente.
- `autorizacao-perfis`: autorizar no Xano a consulta global e gestão de atribuição por Técnico, Diretoria e Administrador, sem ampliar o Gerente.

## Impact

- **Reflex:** página, `ChamadosTecnicoState`, service de Service Desk e detalhe técnico existentes.
- **Xano:** listagem e detalhe técnicos, comando existente de assunção/atribuição, autorização por perfil e consulta estruturada de `interacoes_chamado`.
- **Dados:** evolução aditiva de `interacoes_chamado`; reutilização de `chamados.tecnico_id` e `chamados.atribuido_em`, sem backfill ou tabela de auditoria paralela.
- **Fora do escopo:** mudança de status, tratativa completa, redesign, dashboards, notificações, escalonamento, nova infraestrutura de auditoria e conversão da jornada do Gerente.
