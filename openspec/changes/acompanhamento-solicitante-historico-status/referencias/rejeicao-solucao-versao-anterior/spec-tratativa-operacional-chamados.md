# Spec Delta

## ADDED Requirements

### Requirement: Mudança de status pelo Save grava evento público de histórico
Toda diferença efetiva de Status persistida pelo Save DEVE (MUST) gravar, na mesma transação, um evento `alteracao_status` com visibilidade pública contendo somente o status anterior e o resultante, além da auditoria interna `alteracao_chamado` já existente. O evento público NÃO DEVE (MUST NOT) conter responsável, prioridade, Categoria, SLA, referência a comentário ou outro dado de auditoria. Save sem mudança de Status NÃO DEVE (MUST NOT) gravar evento público.

#### Scenario: Save altera status
- **WHEN** o Save persiste mudança de `Em Atendimento` para `Resolvido`
- **THEN** o Xano grava evento público `Em Atendimento` → `Resolvido`, a auditoria interna e o comentário público obrigatório como três registros distintos

#### Scenario: Save altera somente outros campos
- **WHEN** o Save altera prioridade, Categoria ou responsável sem mudar Status
- **THEN** nenhum evento `alteracao_status` é gravado

#### Scenario: Falha do evento público
- **WHEN** a gravação do evento público falha
- **THEN** o Save não confirma sucesso; a ausência de efeito parcial só é declarada se o gate de transação e rollback do design tiver sido confirmado com evidência

#### Scenario: Timeline técnica
- **WHEN** Técnico, Diretoria ou Administrador consulta o detalhe técnico
- **THEN** a timeline pode conter o evento público e a auditoria interna da mesma mudança, e o Reflex os apresenta sem sugerir duas mudanças de status

### Requirement: Solução Rejeitada é somente legado de leitura
O status `Solução Rejeitada` NÃO DEVE (MUST NOT) ser destino de nenhum fluxo. Chamado persistido com esse valor DEVE (MUST) continuar consultável, filtrável e tratável como não terminal, podendo ser retirado desse estado pelo Save para um destino permitido. O sistema NÃO DEVE (MUST NOT) migrar, reescrever ou converter automaticamente esse valor para `Reaberto`.

#### Scenario: Chamado legado tratado pelo Save
- **WHEN** um perfil operacional salva chamado persistido em `Solução Rejeitada` com destino `Em Atendimento` e comentário válido
- **THEN** o Xano aplica a mudança e grava os eventos correspondentes

#### Scenario: Legado não é convertido
- **WHEN** existe chamado persistido em `Solução Rejeitada`
- **THEN** nenhum fluxo desta change altera esse valor sem ação explícita do Save

## MODIFIED Requirements

### Requirement: Status canônico exige comentário humano associado
O Save DEVE (MUST) aceitar como destino somente `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido`, `Encerrado` e `Cancelado`. `Reaberto` é status canônico alcançado exclusivamente pela operação de rejeição de solução e NÃO DEVE (MUST NOT) ser destino do Save; `Solução Rejeitada` é legado e também NÃO DEVE (MUST NOT) ser destino. O Save DEVE (MUST) aceitar chamado cujo status atual seja `Reaberto` ou `Solução Rejeitada` e permitir a saída para os destinos acima. Toda diferença efetiva de Status DEVE (MUST) incluir comentário humano não vazio na mesma transação; para `Resolvido`, `Aguardando Solicitante` e `Cancelado` sua visibilidade DEVE (MUST) ser Pública.

#### Scenario: Destino com comentário público obrigatório
- **WHEN** o usuário altera o Status para `Resolvido`, `Aguardando Solicitante` ou `Cancelado`
- **THEN** o Xano rejeita visibilidade Interno, comentário ausente ou texto vazio sem persistir qualquer parte do Save

#### Scenario: Destino com visibilidade escolhida
- **WHEN** o usuário altera o Status para `Novo`, `Em Atendimento`, `Aguardando Mudança` ou `Encerrado` com comentário não vazio Público ou Interno
- **THEN** o Xano persiste comentário e alteração no mesmo Save

#### Scenario: Save não reabre nem rejeita
- **WHEN** Técnico, Diretoria ou Administrador tenta alterar pelo Save o Status para `Reaberto` ou `Solução Rejeitada`
- **THEN** o Xano rejeita toda a transação sem alterar status, comentário, eventos ou `ultima_atualizacao_em`

#### Scenario: Retomada após reabertura
- **WHEN** o chamado está `Reaberto` e um perfil operacional salva destino `Em Atendimento` com comentário válido
- **THEN** o Xano aplica a mudança como em qualquer status não terminal

#### Scenario: Status não canônico
- **WHEN** o Save informa `Aguardando Terceiro` ou outro status fora da lista canônica
- **THEN** o Xano rejeita a transação sem alterar o chamado ou criar interação

#### Scenario: Formulário de comentário acompanha Status pendente
- **WHEN** o detalhe da tratativa é carregado
- **THEN** o campo de comentário e a escolha Público/Interno permanecem visíveis, inclusive sem mudança de Status
- **WHEN** o Status do rascunho muda
- **THEN** Salvar permanece indisponível ou apresenta validação clara até haver comentário humano válido; `Resolvido`, `Aguardando Solicitante` e `Cancelado` fixam a visibilidade em Público, os demais destinos permitem Público ou Interno, e `Reaberto` e `Solução Rejeitada` não são oferecidos como destino, embora o status atual seja exibido

#### Scenario: Comentário opcional acompanha Save funcional
- **WHEN** o usuário informa comentário não vazio e salva uma ou mais diferenças funcionais sem mudar Status
- **THEN** o Xano cria exatamente um comentário humano na mesma transação e o evento da alteração referencia essa interação
