# Tasks

> Sanitização pré-Archive: os comandos independentes de gestão de responsável
> foram removidos deste escopo por terem sido substituídos pela change
> `tratativa-operacional-chamados`. As tasks abaixo registram apenas a evolução
> de fila e consulta que permanece no produto.

## 1. Fila, detalhe e histórico compatível

- [x] 1.1 Disponibilizar fila global para Técnico, Diretoria e Administrador com `Todos`, filtros explícitos de número, status, Totem e período, pesquisa por número e escopo rápido `Atribuídos a mim` exclusivo do Técnico.
- [x] 1.2 Expor no DTO canônico de lista e detalhe o responsável atual, `atribuido_em` e a consulta global de chamados terminais e não terminais, sem backfill de dados históricos.
- [x] 1.3 Preservar no detalhe a timeline cronológica de comentários e eventos legados de atribuição, reatribuição e liberação.

## 2. Reflex e autorização de consulta

- [x] 2.1 Adaptar rota, página, State e service à fila global, filtros confirmados somente após sucesso, pesquisa no backend, responsável atual e tratamento distinto de 401, 403 e falhas funcionais.
- [x] 2.2 Autorizar no Xano a consulta global de fila e detalhe para Técnico, Diretoria e Administrador e negar a fila técnica global ao Gerente.

## 3. Validação correspondente

- [x] 3.1 Validar em respostas reais do Xano e no Reflex a consulta global, filtros, pesquisa, detalhe canônico, responsável, `atribuido_em`, histórico legado, autorização representativa e preservação da fila. Evidências posteriores aceitas nas validações 5.1, 5.2, 6.1 e 6.2 da change `tratativa-operacional-chamados` confirmam a permanência desses contratos.
