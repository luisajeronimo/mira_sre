## MODIFIED Requirements

### Requirement: Histórico específico de disponibilidade preserva transições

O sistema DEVE (MUST) persistir em `historico_disponibilidade_totens` somente transições decididas pelo Xano, com a exceção explícita dos fatos sintéticos dos Totens existentes 1 e 2 delimitados em `dados-demonstracao-confiabilidade`. Cada evento DEVE (MUST) conter identificador técnico, relação obrigatória `ativos_referencia_id`, relação técnica `telemetria_referencia_id`, status canônico `online` ou `offline`, `detectado_em`, `heartbeat_limite_minutos` e `created_at` técnico. A telemetria identifica a última telemetria que fundamentou a decisão ou o cenário sintético, e o limite registra o snapshot da regra aplicada, atualmente `15`.

O histórico NÃO DEVE (MUST NOT) registrar polling sem transição, receber backfill fora do lote fictício explicitamente autorizado, conter `chamado_id`, transformar telemetria em ator, servir de auditoria genérica ou persistir métricas derivadas. A exceção de demonstração DEVE (MUST) criar somente fatos novos do lote identificado, preservando a distinção entre timestamps fictícios e o instante técnico da carga; não autoriza reparar ou completar histórico legado.

#### Scenario: Detecção Offline é preservada
- **WHEN** ocorre uma transição elegível Online → Offline
- **THEN** o histórico recebe um evento `offline` ligado ao Totem e à última telemetria, com `detectado_em` da decisão e `heartbeat_limite_minutos = 15`

#### Scenario: Recuperação Online é preservada
- **WHEN** ocorre uma transição elegível Offline → Online
- **THEN** o histórico recebe um evento `online` ligado ao Totem e à telemetria recente que fundamentou a recuperação

#### Scenario: Verificação sem transição
- **WHEN** uma verificação encontra o mesmo estado de disponibilidade já persistido
- **THEN** não cria registro histórico adicional

#### Scenario: Histórico fictício de demonstração é preparado
- **WHEN** a carga delimitada cria pares Offline/Online para os Totens existentes 1 e 2
- **THEN** os fatos sintéticos completos são persistidos somente nesses IDs, preservando os fatos existentes e o histórico dos demais

## ADDED Requirements

### Requirement: Retomada aparece somente para alvo elegível
O detalhe do monitoramento DEVE (MUST) oferecer **Retomar telemetria** para Totem Offline gerenciado e silenciado. Para envio já ativo, DEVE (MUST) informar a autorização existente sem alegar recuperação. Controle ausente ou não gerenciado NÃO DEVE (MUST NOT) habilitar a ação. O badge DEVE (MUST) continuar representando somente o estado persistido.

#### Scenario: Totem silenciado e Offline foi selecionado
- **WHEN** o detalhe autorizado informa essas condições
- **THEN** a ação de retomada fica disponível e identifica o Totem selecionado

#### Scenario: Totem já tem envio ativo ou não é gerenciado
- **WHEN** o controle está ativo, ausente ou não gerenciado
- **THEN** não é oferecida uma nova retomada elegível; autorização ativa não é apresentada como prova de saúde do processo

### Requirement: Retomada exige confirmação explícita antes da requisição
A ação DEVE (MUST) abrir diálogo acessível com nome e Loja do Totem, explicação de retomada nos próximos ciclos e de preservação dos chamados, além de **Cancelar** e **Retomar telemetria**. Somente a confirmação DEVE (MUST) enviar a requisição; abertura, cancelamento e fechamento NÃO DEVEM (MUST NOT) alterar dados.

#### Scenario: Pessoa cancela a confirmação
- **WHEN** o diálogo é cancelado ou fechado antes de confirmar
- **THEN** nenhuma requisição de retomada é enviada e os dados permanecem inalterados

#### Scenario: Confirmação por teclado
- **WHEN** uma pessoa navega pelo diálogo e confirma usando teclado
- **THEN** a mesma operação é enviada, com foco e identificação do alvo acessíveis

### Requirement: Retomada preserva alvo e apresenta resultado real
Durante o envio, a interface DEVE (MUST) impedir reenvio concorrente. Trocar de Totem DEVE (MUST) descartar a confirmação anterior; resposta tardia NÃO DEVE (MUST NOT) sobrescrever o novo detalhe. Sucesso DEVE (MUST) confirmar autorização de envio e recarregar os dados; erro DEVE (MUST) preservar o estado confirmado e seguir o tratamento normal de sessão.

#### Scenario: Confirmação repetida durante processamento
- **WHEN** a pessoa tenta confirmar de novo enquanto a operação está pendente
- **THEN** somente uma solicitação é enviada para o alvo confirmado

#### Scenario: Seleção muda com diálogo aberto ou resposta pendente
- **WHEN** outro Totem é selecionado
- **THEN** a confirmação anterior é descartada e uma resposta do alvo antigo não altera o detalhe do novo selecionado

#### Scenario: Operação é confirmada pelo Xano
- **WHEN** a resposta informa envio autorizado
- **THEN** a interface informa que é necessário aguardar os próximos ciclos, recarrega lista e detalhe e não força o badge para Online

#### Scenario: Operação falha
- **WHEN** o Xano rejeita a operação ou não é possível confirmar a resposta
- **THEN** a interface apresenta a falha sem indicar retomada concluída; se a sessão expirou, aplica o fluxo central de autenticação
