# Design

## Context

Ver `proposal.md` para a motivação e as delta specs para o contrato observável. Hoje `verificar-falhas` consulta a telemetria mais recente por `evento_timestamp`, compara-a com 15 minutos, sobrescreve `status_atual` e consulta equivalentes pelos status `Novo`, `Em Atendimento` e o legado `Aguardando Terceiro`. Não há registro histórico de disponibilidade.

O Fiscal é a única automação de fiscalização prevista: chama sequencialmente `GET /verificar-falhas`, aguarda a resposta e então espera o intervalo padrão de 300 segundos. Não há múltiplas instâncias, workers, scheduler paralelo, alta disponibilidade ou requisito de concorrência nesta change. Simulator apenas envia telemetria e o Xano continua sendo a autoridade para disponibilidade e chamados.

O MCP XanoScript documenta `db.transaction` para operações de banco e all-or-nothing. Antes de Apply, o gate técnico deve confirmar no Free a sintaxe, as operações necessárias, o schema e a semântica documentada de rollback. Parser confirma sintaxe, não comportamento runtime. Não há UI da Diretoria nesta change.

## Goals / Non-Goals

**Goals:**

- Preservar cada transição efetiva Online/Offline em histórico específico por Totem, sem registrar polling repetido.
- Centralizar no Xano o gate de estado prévio e a criação controlada do incidente automático.
- Impedir, em uma execução normal, falha parcial que deixe Offline sem histórico coerente e sem nova possibilidade de avaliação automática.
- Produzir fatos temporais para consumo futuro, sem calcular indicadores agora.

**Non-Goals:**

- Dashboard, tela nova, DTO ou mudança Reflex para Diretoria.
- Auditoria genérica, histórico de ações de chamados ou framework de eventos.
- Backfill de disponibilidade, inferência sobre dados passados ou alteração de incidentes legados.
- Identidade, autenticação ou credencial do Bot/Fiscal/Simulator; resolução, cancelamento ou encerramento automático de chamado.
- Isolamento serializável, CAS, lock, `FOR UPDATE`, claim de concorrência, índice UNIQUE por concorrência ou suporte a múltiplos Fiscais.

## Decisions

### Premissa de execução sequencial

O desenho trata uma execução normal do único Fiscal. A próxima chamada somente começa após a resposta da anterior e após o ciclo de aproximadamente 300 segundos. Assim, `db.transaction` é adotada por atomicidade da transição, e não por serialização entre fiscalizações concorrentes. Não será introduzida exclusão mútua nem infraestrutura adicional para cenário fora da arquitetura aprovada.

### Histórico mínimo e específico de disponibilidade

Será criada a tabela `historico_disponibilidade_totens`, com estes significados mínimos:

- `id`: identificador técnico do evento;
- `ativos_referencia_id`: relação obrigatória com o Totem cuja disponibilidade mudou;
- `telemetria_referencia_id`: relação técnica obrigatória com a última telemetria que fundamentou a decisão;
- `status`: enum canônico `online` ou `offline`;
- `detectado_em`: instante em que o Xano detectou e materializou a mudança;
- `heartbeat_limite_minutos`: snapshot do limite aplicado, atualmente `15`;
- `created_at`: metadado técnico da linha.

O histórico guarda somente transições: Online → Offline cria `offline`; Offline → Online cria `online`; Online → Online, Offline → Offline e Totem sem telemetria não criam evento. Não haverá itens iniciais, backfill, `chamado_id`, campos derivados ou auditoria genérica.

`telemetria_referencia_id` existe para rastreabilidade da decisão, relação entre último heartbeat e detecção e indicadores futuros; não identifica ator e não é mecanismo de concorrência. O snapshot `heartbeat_limite_minutos` torna eventos antigos interpretáveis se a regra mudar, sem substituir a regra vigente.

Campos sobrescritos em `ativos_referencia` foram rejeitados porque perdem histórico; auditoria universal foi rejeitada porque amplia o domínio. Vincular o histórico a chamado foi rejeitado: uma indisponibilidade continua sendo fato operacional mesmo se chamado equivalente não terminal impedir novo chamado.

### Classificação por transição e última telemetria

`verificar-falhas` selecionará a última telemetria por `evento_timestamp`. Totem sem telemetria não recebe escrita. Telemetria igual ou posterior ao limite de 15 minutos somente inicia Offline → Online se o estado anterior for Offline. Telemetria superior a 15 minutos somente inicia Online → Offline se o estado anterior for Online. Estados já iguais não geram escrita de disponibilidade ou histórico.

O estado anterior é lido antes de qualquer atualização; esse gate substitui a sobrescrita incondicional atual e impede eventos repetidos no polling sequencial previsto.

### Unidade atômica da transição Offline

Para uma candidata Online → Offline, `db.transaction` abrangerá:

1. revalidação da última telemetria e da idade estritamente superior a 15 minutos;
2. confirmação de que o estado persistido é Online;
3. localização e validação da categoria `Totem Offline / Sem Heartbeat`;
4. consulta de incidente equivalente;
5. criação do evento histórico `offline` com telemetria de referência, `detectado_em` e snapshot `15`;
6. atualização do Totem para Offline;
7. criação do incidente automático somente quando não houver equivalente não terminal.

Todos os dados obrigatórios são validados dentro da unidade antes de suas escritas dependentes. A intenção é que falha obrigatória de categoria, histórico ou inserção do chamado não deixe persistidos somente parte do evento. O design se baseia somente na semântica documentada de all-or-nothing de `db.transaction`; não presume a semântica de rollback de `return`, `precondition`, `throw` ou erro tratado. O Apply usa somente a sequência validada pelo gate, parser e harness. Por decisão humana de segurança e proporcionalidade no único workspace disponível, esta change não introduz fault injection remoto nem mutação temporária do endpoint: não há prova runtime de rollback, ausência de estado parcial ou nova tentativa provocada por falha.

Se houver equivalente não terminal, o histórico e a atualização para Offline permanecem fatos válidos; apenas a criação do novo chamado é omitida. Isso permite que nova indisponibilidade futura continue representada, mesmo com chamado anterior em tratamento.

### Incidente e deduplicação

Na transição Online → Offline, o Xano localizará a categoria exata `Totem Offline / Sem Heartbeat`, cujo contrato existente é `Incidente`, SLA numérico e `permite_abertura_manual = false`. A descrição versionada será corrigida de cinco para mais de 15 minutos, sem mudar tipo, SLA ou elegibilidade manual.

A consulta de equivalência usa somente ativo + categoria + status não terminal: `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido` e `Solução Rejeitada`. `Encerrado` e `Cancelado` não bloqueiam; `Aguardando Terceiro` não é reintroduzido. Origem e autoria do Bot não entram na chave e não haverá constraint física nova em `chamados`.

O incidente novo preserva título atual, status `Novo`, prioridade `Urgente`, origem `automatico`, solicitante humano ausente, `criador_sistema = bot_fiscalizacao`, `criado_em` backend e snapshot do SLA da categoria.

### Recuperação Online independente do chamado

Em Offline → Online, uma unidade de escrita registra o evento histórico `online`, com a telemetria que fundamentou a recuperação e o snapshot do limite aplicado, e atualiza o Totem para Online. Nenhuma consulta ou escrita em `chamados` ocorre nesse ramo: telemetria recuperada não resolve, encerra, cancela ou modifica tratativa.

### Dados para indicadores futuros

Os pares Offline/Online, `detectado_em`, `telemetria_referencia_id`, `heartbeat_limite_minutos` e `chamados.criado_em` permitem derivar posteriormente indisponibilidades por Totem ou Loja, duração, percentual histórico de disponibilidade, recorrência, tempo entre último heartbeat e detecção e tempo entre detecção e incidente.

Não serão persistidos duração, percentual, MTTD, MTTR, médias, quantidades agregadas ou outro valor derivado; nenhum dashboard, endpoint ou UI será criado.

## Risks / Trade-offs

- **Falha parcial na transição Offline** → o gate pré-Apply confirma `db.transaction`, operações admitidas e semântica documentada de all-or-nothing no Free; parser e harness validam a estrutura e a sequência prevista. A decisão humana dispensa fault injection remoto para evitar mutação temporária e risco no único workspace; essa limitação é registrada, sem alegar rollback runtime comprovado.
- **Categoria ausente ou incompatível** → falhar a unidade sem fallback; dados remotos só podem ser corrigidos mediante escopo aprovado.
- **Evento duplicado em polling sequencial** → gate de estado anterior e testes de Offline contínuo e Online contínuo.
- **Deriva de status legado** → enumeração explícita dos seis não terminais e dois terminais; nenhum uso de `Aguardando Terceiro`.
- **Limitação Xano Free ou parser** → validar via MCP e parser antes de Apply; não criar worker, serviço pago, lock ou infraestrutura paralela.
- **E2E interfere em dados operacionais** → usar Totem controlado existente e restaurar somente a telemetria prevista; se exigir mutação fora do escopo autorizado, parar para decisão humana.

## Migration Plan

1. Antes de Apply, validar via MCP e parser a transação, schema histórico, relações, enum, operações e semântica documentada de rollback/all-or-nothing no Free. Se não demonstrar rollback necessário, parar para decisão humana.
2. Criar a tabela sem itens iniciais ou backfill, adaptar somente `verificar-falhas` e a descrição versionada da categoria.
3. Validar XanoScript, harnesses e testes de contrato; executar `dry-run`, revisar o diff remoto completo e obter autorização humana antes de push.
4. Após push autorizado, executar E2E sequencial controlado: silenciar Totem existente, aguardar o limite, acionar Fiscal, verificar ativo/histórico/chamado, repetir, restaurar telemetria e confirmar que o chamado persiste. Fault injection remoto permanece deliberadamente não executado por decisão humana; sua cobertura limita-se à documentação oficial, parser e harness estático.

Em rollback operacional, desativar a mudança de endpoint junto com a tabela de histórico somente por procedimento aprovado. Eventos e chamados já produzidos não devem ser apagados ou reescritos; remoção de dados requer decisão destrutiva separada.

## Open Questions

As referências `1`, `D1` e `D2` não possuem fonte documental localizada. Elas permanecem metadados não bloqueantes e não mudam specs, design ou tasks.
