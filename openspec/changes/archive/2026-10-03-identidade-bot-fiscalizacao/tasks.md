## 1. Preparação e modelo persistente

- [x] 1.1 Consultar o Xano Developer MCP para confirmar o schema e os recursos Free do workspace alvo antes da alteração e registrar que `criador_sistema` aditivo, opcional e enumerado não exige recurso pago.
- [x] 1.2 Adicionar `chamados.criador_sistema` como enum opcional limitado a `bot_fiscalizacao`, sem FK para `usuarios`, e validar o XanoScript do schema sem alterar dados existentes.
- [x] 1.3 Inspecionar o diff do schema e confirmar que não há usuário, perfil, credencial, secret, backfill ou alteração em `interacoes_chamado`.

## 2. Criação automática no Xano

- [x] 2.1 Adaptar somente a inserção de novo incidente em `verificar-falhas` para persistir `criador_sistema = "bot_fiscalizacao"` e validar o XanoScript afetado.
- [x] 2.2 Executar ou atualizar o harness de heartbeat para comprovar que incidente novo recebe origem automática, solicitante ausente e criador de sistema, sem mudar timeout, telemetria, disponibilidade, status, prioridade, SLA ou critério de incidente equivalente.
- [x] 2.3 Verificar por diff e teste que um incidente equivalente não cria nem atualiza chamado, inclusive sem preencher autoria em registros existentes.

## 3. Contratos de detalhe e cliente

- [x] 3.1 Expor `criador_sistema` opcional nos DTOs de detalhe de Gerente e Técnico, separado de origem e solicitante, e validar os testes XanoScript/contratuais de ambos os perfis.
- [x] 3.2 Adaptar os modelos e o parseamento do cliente Service Desk para aceitar `criador_sistema` nulo ou `bot_fiscalizacao`, mantendo `solicitante` como referência exclusivamente humana; verificar com testes do cliente.
- [x] 3.3 Cobrir nos contratos e clientes os cenários manual, automático atual e legado sem autoria, comprovando ausência de inferência e preservação de autorização existente.

## 4. Apresentação mínima no Reflex

- [x] 4.1 Ajustar os detalhes existentes de Gerente e Técnico para mostrar `Criado por: Bot de Fiscalização` somente para o valor canônico e manter `Origem: Automático` separadamente; verificar por teste de componente/state ou compilação Reflex aplicável.
- [x] 4.2 Confirmar por diff e teste que as listagens não ganham coluna de autoria, e que detalhes manual e legado não mostram o Bot quando `criador_sistema` é nulo.

## 5. Validação e segurança da entrega

- [x] 5.1 Atualizar somente os trechos necessários de `docs/domain-model.md` e `docs/project-overview.md` para distinguir solicitante humano ausente de criador de sistema Bot no heartbeat; verificar por diff que não houve reescrita de regras adjacentes, auditoria genérica ou mudança de domínio fora desse esclarecimento.
- [x] 5.2 Executar os testes Python relevantes de heartbeat, cliente Service Desk, estados e rotas/telas alteradas, registrando separadamente qualquer teste bloqueado pelo ambiente.
- [x] 5.3 Executar a validação/compilação Reflex aplicável e confirmar que não há regressão dos detalhes de Gerente e Técnico.
- [x] 5.4 Executar `xano workspace push --dry-run`, revisar o diff completo do Xano e confirmar que somente schema, endpoint e contratos aprovados estão no escopo antes de qualquer push real.
- [x] 5.5 Antes de considerar a change pronta, executar `openspec validate identidade-bot-fiscalizacao --strict`, `git diff --check`, revisar `git diff` e confirmar que não houve backfill, alteração de credenciais, segredo exposto, mudança de deduplicação ou mudança funcional fora do delta.
