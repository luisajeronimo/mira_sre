# Proposal

## Why

O monitoramento já detecta um Totem sem heartbeat e pode marcá-lo Offline, mas não preserva as transições de disponibilidade, não exige o estado prévio Online e usa deduplicação incompatível com o ciclo de vida vigente dos chamados. A evidência runtime `offline = 1` e `incidentes_criados = 0` confirma que a criação controlada ainda não está demonstrada ponta a ponta.

## What Changes

- Introduzir histórico específico de transições de disponibilidade de Totens, contendo o Totem, a telemetria de referência, o status da transição, o instante de detecção e o snapshot do limite de heartbeat. A estrutura não é auditoria genérica e não recebe backfill.
- Fazer o Xano registrar somente transições efetivas Online → Offline e Offline → Online. Totem sem telemetria anterior permanece sem mudança, histórico ou incidente; polling sem mudança de estado não cria evento.
- Tornar a criação de incidente de heartbeat elegível somente na transição Online → Offline, mantendo categoria `Totem Offline / Sem Heartbeat`, prioridade `Urgente`, origem `automatico`, solicitante humano ausente, `criador_sistema = bot_fiscalizacao`, status inicial `Novo` e snapshot de SLA.
- Corrigir a deduplicação para considerar incidente equivalente do mesmo Totem e categoria em qualquer status vigente não terminal, excluindo `Encerrado` e `Cancelado` e sem reutilizar o status legado `Aguardando Terceiro`.
- Usar `db.transaction` para que a transição Offline, seu histórico e a criação elegível de incidente sejam atômicos em uma execução normal. O gate técnico pré-Apply valida no Xano Free a sintaxe, as operações admitidas e a semântica documentada de all-or-nothing; por decisão humana de segurança e proporcionalidade, esta change não executará fault injection remoto e não alegará prova runtime de rollback.
- Preservar a recuperação Offline → Online no Xano e seu histórico, sem resolver, encerrar, cancelar ou alterar o chamado por retorno de telemetria.
- Corrigir somente a descrição versionada da categoria de heartbeat para refletir ausência superior a 15 minutos, sem alterar tipo, SLA ou permissão de abertura manual.
- Prever testes locais, XanoScript e runtime/E2E controlado para distinguir deduplicação legítima, categoria ausente, erro de criação e demais bloqueios relacionados ao resultado `incidentes_criados = 0`.

## Capabilities

### New Capabilities

- `monitoramento-disponibilidade-totens`: decisão de disponibilidade pelo Xano, transições históricas de Totens e criação controlada de incidente por heartbeat.

### Modified Capabilities

- `chamados-abertura-manual`: atualizar o contrato compartilhado da criação automática de heartbeat para deduplicação vigente e criação atômica, preservando autoria do Bot, SLA e compatibilidade dos chamados.

## Impact

- **Xano:** schema novo e específico de histórico de disponibilidade, `verificar-falhas`, categoria de heartbeat e validações XanoScript/runtime.
- **Dados:** nenhuma inferência, backfill, limpeza ou reescrita de registros históricos. Os eventos passam a ser produzidos somente em transições futuras.
- **Premissa operacional:** existe um único Fiscal, que chama sequencialmente `GET /verificar-falhas`, aguarda a resposta e só então espera aproximadamente 300 segundos para o próximo ciclo. Múltiplas instâncias, workers ou fiscalizações concorrentes não pertencem ao escopo desta sprint.
- **Componentes:** Fiscal continua apenas disparando o endpoint e Simulator continua somente enviando telemetria de Totens existentes.
- **Frontend:** não há nova tela da Diretoria, dashboard ou mudança de Reflex; os fatos armazenados são preparados para consumo futuro.
- **Plano Xano e validação:** antes de Apply, MCP e parser demonstrarão a disponibilidade no Free, a sintaxe e as operações da transação, o schema e a semântica documentada de all-or-nothing. Se o rollback necessário não puder ser demonstrado, Apply para para decisão humana. Após push autorizado, o runtime/E2E valida a transição e a recuperação em um Totem controlado.
- **Planejamento:** as dependências `1`, `D1` e `D2` não foram localizadas em documentação do projeto; permanecem metadados não resolvidos e não bloqueiam esta change.

## Fora de escopo

- Dashboards, indicadores MTTD/MTTR, nova UI da Diretoria, filtros e novas jornadas Reflex.
- Tratamento técnico, atribuição, comentários, reatribuição, resolução, encerramento ou cancelamento automático de chamados.
- Nova autenticação, credencial, Environment Variable, identidade do Bot ou alteração das automações Fiscal e Simulator.
- Auditoria genérica, framework de eventos, backfill ou alteração de dados históricos.
- Serialização, locks, CAS, `FOR UPDATE`, múltiplas instâncias de Fiscal, exclusão mútua, índice UNIQUE para concorrência e testes de chamadas concorrentes.

## Decisões humanas pendentes

A persistência histórica específica, incluindo a referência técnica à telemetria e o snapshot de 15 minutos, é decisão humana aprovada nesta solicitação; não é pendência nova. As referências `1`, `D1` e `D2` seguem sem fonte documental e são metadados não bloqueantes.

Há um gate técnico obrigatório antes de Apply: MCP e parser devem demonstrar no Xano Free a capacidade, sintaxe, operações e semântica documentada de all-or-nothing da unidade atômica. Se o rollback necessário não puder ser demonstrado, Apply deve parar para decisão humana, sem aceitar estado parcial nem inventar infraestrutura alternativa.
