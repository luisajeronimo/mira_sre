# Tasks

## 0. Gate técnico obrigatório antes de Apply

- [x] 0.1 Antes de autorizar Apply, validar com Xano Developer MCP e parser, no Free, a disponibilidade e sintaxe de `db.transaction`, as operações de banco necessárias dentro dela, o schema histórico com relações e enum e a semântica documentada de rollback/all-or-nothing. Se o rollback necessário não puder ser demonstrado, interromper Apply para decisão humana, sem inventar infraestrutura nem aceitar estado parcial.
- [x] 0.2 Registrar que o gate 0 é estático/técnico: parser confirma sintaxe e MCP/documentação confirmam capacidade e contrato. Por decisão humana de segurança e proporcionalidade, fault injection remoto de rollback e nova tentativa não será executado; o gate não exige isolamento serializável, CAS, locks, múltiplos Fiscais ou chamadas concorrentes.

## 1. Modelagem temporal de disponibilidade

- [x] 1.1 Após o gate 0, validar com Xano Developer MCP e parser que tabela, relações obrigatórias para Totem e telemetria, enum `online`/`offline`, timestamps e snapshot numérico do limite são compatíveis com o Free.
- [x] 1.2 Criar `historico_disponibilidade_totens` com `id`, `ativos_referencia_id`, `telemetria_referencia_id`, `status`, `detectado_em`, `heartbeat_limite_minutos` e `created_at`, sem itens iniciais, backfill, `chamado_id`, auditoria genérica ou campos derivados; validar o XanoScript do schema.
- [x] 1.3 Verificar por diff/schema que o histórico preserva somente fatos de transições futuras e não altera dados legados, ativos, telemetrias ou chamados fora do escopo.

## 2. Regra de transição e atomicidade Offline

- [x] 2.1 Adaptar `verificar-falhas` para ler e revalidar estado persistido e última telemetria, produzindo Online → Offline somente para Totem previamente Online com `evento_timestamp` estritamente superior a 15 minutos; validar XanoScript e limite estrito.
- [x] 2.2 Na `db.transaction` aprovada no gate, validar categoria, equivalente, telemetria e estado; registrar evento Offline com telemetria de referência e snapshot `15`, atualizar Totem e criar incidente quando aplicável.
- [x] 2.3 Preservar Totem sem telemetria sem escrita de estado, evento ou chamado; cobrir por teste XanoScript/harness.
- [x] 2.4 Cobrir Offline contínuo em fiscalizações sequenciais, sem novo evento Offline, sobrescrita do histórico ou novo incidente por repetição do polling.

## 3. Deduplicação e criação automática

- [x] 3.1 Atualizar busca de equivalente para ativo + categoria de heartbeat + exatamente os status não terminais `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido` e `Solução Rejeitada`; validar XanoScript e testes de cada status.
- [x] 3.2 Confirmar por testes que `Encerrado` e `Cancelado` não bloqueiam incidente em nova transição elegível, `Aguardando Terceiro` não participa e equivalente não impede persistência da transição de disponibilidade.
- [x] 3.3 Garantir na inserção de incidente novo Totem e categoria corretos, status `Novo`, prioridade `Urgente`, origem `automatico`, solicitante humano nulo, `criador_sistema = bot_fiscalizacao`, `criado_em` backend e snapshot do SLA; validar sem modificar chamado equivalente ou legado.
- [x] 3.4 Validar contrato da categoria `Totem Offline / Sem Heartbeat`, corrigir somente descrição versionada para mais de 15 minutos e verificar que tipo, SLA e `permite_abertura_manual = false` permanecem inalterados.

## 4. Recuperação Online e fatos para consumo futuro

- [x] 4.1 Adaptar verificação para registrar Offline → Online somente quando Totem previamente Offline receber telemetria no limite ou mais recente; persistir telemetria de referência e snapshot do limite, atualizar Totem e validar XanoScript e transição única.
- [x] 4.2 Cobrir por teste que fiscalizações sequenciais após recuperação não duplicam evento Online e que telemetria retornada não resolve, encerra, cancela nem altera chamado.
- [x] 4.3 Verificar por consulta/teste que fatos de telemetria, histórico e `chamados.criado_em` permitem relacionar Offline → Online, último heartbeat, detecção e incidente sem implementar dashboard, endpoint, MTTD ou MTTR.

## 5. Testes locais e validações XanoScript

- [x] 5.1 Atualizar harness de heartbeat com: sem telemetria; Online com telemetria recente; Online com mais de 15 minutos; Offline contínuo; equivalente em cada status não terminal; `Encerrado`/`Cancelado`; Bot; Offline → Online; Online contínuo; referência à telemetria; snapshot do limite; e preservação de chamado.
- [x] 5.2 Criar ou atualizar testes XanoScript/contrato para schema, endpoint, transações, categoria e autenticação técnica inalterada; validar XanoScripts afetados no MCP.
- [x] 5.3 Criar no harness ou em validação estática uma falha controlada da unidade Online → Offline para verificar a sequência prevista de rollback e nova tentativa, sem tratá-la como prova runtime.
- [x] 5.4 Confirmar por testes e diff que Fiscal continua somente disparando endpoint sequencialmente, Simulator continua somente enviando telemetria de Totens existentes e nenhum Reflex/dashboard da Diretoria foi alterado.

## 6. Validação runtime/E2E controlada após push autorizado

- [x] 6.1 Depois de Apply, executar `xano workspace push --dry-run`, revisar diff remoto completo, obter autorização humana de push e fazer push somente ao alvo remoto autorizado. Se não houver autoridade para mutação, registrar runtime/E2E como não executado ou bloqueado.
- [x] 6.2 Somente após 6.1, executar cenário sequencial controlado com Totem existente: silenciar somente seu envio no Simulator, acionar Fiscal após mais de 15 minutos e verificar Offline, evento histórico com referência e limite, e incidente novo ou causa concreta da supressão, sem expor segredos.
  - Evidência runtime (2026-10-04): Totem E2E `16` (`TOT-E2E-HB-001`) passou de Online para Offline após 942,894 segundos desde a telemetria `717`; o Fiscal retornou `incidentes_criados: 1`, criou o histórico Offline `49` (referência `717`, limite `15`) e o chamado automático `33`.
- [x] 6.3 Repetir Fiscal sem telemetria e comprovar ausência de evento ou incidente duplicados; consultar equivalente quando houver para classificar deduplicação legítima, incorreta, categoria ausente, falha de criação ou outro bloqueio.
  - Evidência runtime (2026-10-04): segunda fiscalização com o Totem `16` ainda silenciado retornou `incidentes_criados: 0`; os IDs permaneceram histórico `49` e chamado `33`.
- [x] 6.4 Sustentar atomicidade e rollback pela documentação oficial de `db.transaction` (all-or-nothing), validar a estrutura transacional pelo parser e a sequência de falha/nova tentativa pelo harness estático. Não executar fault injection remoto nem mutação temporária do endpoint no único workspace, por decisão humana de segurança e proporcionalidade; não alegar rollback runtime comprovado.
  - Evidência: gate 0 confirmou o contrato oficial e a capacidade no Free; parser e harness validaram a unidade e sua sequência de falha. A decisão humana de 2026-10-04 dispensou deliberadamente a prova runtime por fault injection. O E2E comprovou somente o fluxo normal e não é evidência de rollback provocado.
- [x] 6.5 Restaurar telemetria do Totem controlado, acionar verificação e comprovar Offline → Online com evento histórico único, telemetria de referência, snapshot do limite e chamado preservado; remover antes da entrega qualquer instrumentação temporária segura usada na investigação.
  - Evidência runtime (2026-10-04): a telemetria normal `763` restaurou o Totem `16` para Online e criou somente o histórico Online `65` (referência `763`, limite `15`); o chamado `33` permaneceu `Novo`, sem responsável, resolução, encerramento ou cancelamento.

## 7. Documentação e validação final

- [x] 7.1 Atualizar somente documentação estável necessária para descrever histórico específico de disponibilidade, transições e descrição de categoria; revisar diff para confirmar ausência de auditoria genérica, backfill ou expansão de UI.
- [x] 7.2 Após push autorizado e runtime/E2E, executar novo `xano workspace push --dry-run`, revisar diff remoto completo e confirmar que não restaram alterações não aprovadas; não executar push adicional sem autorização humana.
  - Evidência (2026-10-04): `xano workspace push --dry-run` retornou `No changes to push.`; nenhum push adicional foi executado. O resultado não usa `--records` como critério de limpeza.
- [x] 7.3 Executar `openspec validate monitoramento-heartbeat-incidentes-automaticos --strict`, `git diff --check`, testes aplicáveis e revisar `git diff`, incluindo arquivos não rastreados, registrando separadamente passou, falhou, não executado ou bloqueado.
  - Evidência (2026-10-04): `openspec validate --strict` passou; `git diff --check` passou; testes específicos de heartbeat/automações passaram (33) e a suíte completa passou (121); o MCP validou os três XanoScripts afetados; `git diff`, `git diff --stat`, `git status --short` e a checagem de whitespace dos artefatos não rastreados foram revisados. Nenhuma validação planejada ficou bloqueada.
