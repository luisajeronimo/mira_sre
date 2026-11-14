# Proposta — Acessos operacionais equivalentes

## Why

A Diretoria não consegue consultar o consumo de SLA no detalhe porque o backend ainda aplica uma autorização antiga. Outras diferenças entre Técnico, Diretoria e Administrador também divergem da decisão humana atual: os três devem ter os mesmos acessos operacionais, com Gestão e suas rotas exclusivas do Administrador.

## What Changes

- Liberar o consumo de SLA de fila/detalhe e todos os indicadores aos três perfis operacionais.
- Igualar navegação, abertura manual global e escopos da fila, mantendo somente Técnicos como responsáveis por chamados, conforme confirmação expressa da responsável.
- Disponibilizar a abertura global por contratos operacionais compartilhados, sem conceder acesso aos contratos da Gestão administrativa.
- Alinhar consultas genéricas de leitura de chamado, Categoria, Loja, Totem, telemetria e interações já utilizadas pelos perfis internos; manter mutações genéricas bloqueadas.
- Reconciliar documentação estável e a autorização da change ativa de causas/recorrência; preservar seu cálculo, os dados e as changes arquivadas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `autorizacao-perfis`: equivalência de acessos operacionais e proteção da Gestão.
- `sla-encerramento-chamados`: consumo de SLA também disponível à Diretoria na fila/detalhe.
- `navegacao-lateral-perfis`: Indicadores disponível aos três perfis internos.
- `dashboard-disponibilidade-confiabilidade`: autorização dos três perfis internos.
- `dashboard-operacao-sla`: autorização dos três perfis internos.
- `chamados-abertura-manual`: formulário e abertura global compartilhados.
- `chamados-fila-atribuicao-tecnica`: mesmos escopos e preferências de consulta, sem ampliar quem pode ser responsável.
- `frontend-sessao-navegacao`: proteção comum das jornadas operacionais e aliases.

## Impact

Gates Xano, consultas de indicadores/SLA, leituras legadas e abertura manual; navegação, State e cliente Reflex; testes de matriz de acesso. Gestão de Usuários/Lojas/Totens segue exclusiva do Administrador. Não há novo perfil, campo persistido, entidade, mudança de senha, alteração de usuário ou reatribuição de chamados históricos.

## Decisão humana

Em 14/11/2026, a responsável determinou acessos iguais a Técnico, Diretoria e Administrador, exceto Gestão e suas rotas. Na confirmação específica, respondeu: “Não, responsáveis continuam sendo somente Técnicos”. A implementação e publicação das correções operacionais seguem o trabalho autorizado nesta sessão; nenhuma decisão funcional permanece pendente. Archive não integra este pedido.
