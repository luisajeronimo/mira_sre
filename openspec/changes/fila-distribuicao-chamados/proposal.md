# Proposta: fila de distribuição de chamados

## Why

A implementação atual da fila global divergiu da listagem do Gerente: mantém visões de atribuição como navegação, não aplica os mesmos filtros explícitos e não possui evidência de integração do contrato real. Isso impede Técnico, Diretoria e Administrador de consultar a distribuição global de forma confiável e encobre erros de contrato no detalhe.

## What Changes

- Alinhar a fila existente ao padrão da listagem do Gerente: uma tabela global com filtros explícitos de número, status, Totem e período; sem filtros, `Todos` representa todos os chamados globais.
- Remover as visões e filtros de navegação por situação de atribuição, inclusive `Atribuídos a outros Técnicos`; o responsável continua visível na tabela e administrável no detalhe.
- Permitir assumir, atribuir, reatribuir e liberar o Técnico responsável em chamados não terminais, preservando o status e validando no Xano que o responsável é Técnico.
- Preservar idempotência ao repetir `Assumir` pelo Técnico já responsável, sem renovar `atribuido_em` nem duplicar o evento.
- Apresentar comentários existentes e eventos estruturados de atribuição, reatribuição e liberação em uma única timeline cronológica.
- Aplicar a autorização e registrar a alteração do responsável e seu evento na mesma operação Xano.
- Manter a fila e o detalhe Reflex existentes, com DTO único e contrato validado contra respostas reais do Xano.

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
