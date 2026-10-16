# Spec Delta

## Purpose

Definir a tratativa operacional pendente e auditável de chamados, com Save atômico, comentários e integração segura entre Reflex e Xano.

## ADDED Requirements

### Requirement: Tratativa mantém edição pendente dos quatro campos funcionais
O sistema DEVE (MUST) apresentar a Técnico, Diretoria e Administrador, em chamado não terminal, os campos `Responsável`, `Status`, `Prioridade` e `Categoria` como edição pendente. A interface DEVE (MUST) conter `Descartar mudanças` e `Salvar`; mudanças locais NÃO DEVEM (MUST NOT) persistir antes de Salvar.

#### Scenario: Responsável é selecionado na edição pendente
- **WHEN** um perfil operacional abre chamado não terminal
- **THEN** `Responsável` oferece exatamente `Não atribuído` e usuários com perfil Técnico, sem persistir a seleção ao trocar o dropdown

#### Scenario: Descarte restaura o estado persistido
- **WHEN** o usuário altera um ou mais dos quatro campos e seleciona `Descartar mudanças`
- **THEN** a interface restaura os valores retornados no último detalhe persistido sem enviar mutação funcional

#### Scenario: Terminal bloqueia edição funcional
- **WHEN** o detalhe possui status `Encerrado` ou `Cancelado`
- **THEN** os quatro campos, Salvar e Descartar não permitem alteração funcional

### Requirement: Save aplica mudanças funcionais em uma transação lógica
O sistema DEVE (MUST) oferecer um único contrato autenticado de Save que receba o estado pendente e `ultima_atualizacao_em` do detalhe confirmado. O Xano DEVE (MUST) comparar esse valor com o registro persistido, rejeitar divergência sem efeito parcial e, quando coincidir, autorizar, validar e persistir todas as diferenças efetivas em uma única transação lógica, retornando o detalhe canônico pós-commit.

#### Scenario: Save combinado válido
- **WHEN** um perfil operacional salva mudanças válidas de responsável, status, prioridade e Categoria em chamado não terminal
- **THEN** todas as mudanças são persistidas juntas e o detalhe retornado representa o estado pós-commit

#### Scenario: Falha impede estado parcial
- **WHEN** qualquer validação ou persistência de um Save falha
- **THEN** nenhum campo funcional, comentário obrigatório, evento automático ou `ultima_atualizacao_em` permanece alterado

#### Scenario: Save sem diferença funcional
- **WHEN** o usuário salva valores iguais aos persistidos
- **THEN** o chamado e `ultima_atualizacao_em` permanecem inalterados e nenhum evento automático é criado

#### Scenario: Detalhe foi atualizado por outra operação
- **WHEN** o Save informa `ultima_atualizacao_em` diferente do valor persistido atual
- **THEN** o Xano rejeita o Save sem persistir campo, comentário ou evento e o Reflex informa a atualização e recarrega o detalhe atual

### Requirement: Responsável é alterado somente pelo Save operacional
O Save DEVE (MUST) interpretar responsável ausente para Técnico como atribuição, Técnico para Técnico como reatribuição e Técnico para `Não atribuído` como liberação. Técnico, Diretoria e Administrador DEVEM (MUST) poder selecionar qualquer Técnico ou `Não atribuído` em chamado não terminal; somente usuário com perfil Técnico pode ser responsável.

#### Scenario: Atribuição, reatribuição e liberação
- **WHEN** um perfil operacional salva uma mudança válida de Responsável
- **THEN** o Xano persiste o responsável resultante, define `atribuido_em` para atribuição ou reatribuição, limpa `tecnico_id` e `atribuido_em` para `Não atribuído` e não altera o status por esse motivo

#### Scenario: Responsável inválido
- **WHEN** o Save informa usuário que não possui perfil Técnico como Responsável
- **THEN** o Xano rejeita toda a transação sem alterar o chamado ou criar interações

#### Scenario: Técnico altera responsável de outro Técnico
- **WHEN** um Técnico autenticado salva Responsável diferente do responsável atual
- **THEN** o Xano aplica a mudança se o chamado for não terminal, sem restringir a liberação à própria atribuição

### Requirement: Status canônico exige comentário humano associado
O Save DEVE (MUST) aceitar somente `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Resolvido`, `Solução Rejeitada`, `Encerrado` e `Cancelado`. Toda diferença efetiva de Status DEVE (MUST) incluir comentário humano não vazio na mesma transação; para Resolvido, Aguardando Solicitante e Cancelado sua visibilidade DEVE (MUST) ser Pública.

#### Scenario: Destino com comentário público obrigatório
- **WHEN** o usuário altera o Status para Resolvido, Aguardando Solicitante ou Cancelado
- **THEN** o Xano rejeita visibilidade Interno, comentário ausente ou texto vazio sem persistir qualquer parte do Save

#### Scenario: Destino com visibilidade escolhida
- **WHEN** o usuário altera o Status para Novo, Em Atendimento, Aguardando Mudança, Solução Rejeitada ou Encerrado com comentário não vazio Público ou Interno
- **THEN** o Xano persiste comentário e alteração no mesmo Save

#### Scenario: Status não canônico
- **WHEN** o Save informa `Aguardando Terceiro` ou outro status fora da lista canônica
- **THEN** o Xano rejeita a transação sem alterar o chamado ou criar interação

#### Scenario: Formulário de comentário acompanha Status pendente
- **WHEN** o Status do rascunho permanece igual ao persistido
- **THEN** o formulário independente `Adicionar comentário` permanece separado do Save
- **WHEN** o Status do rascunho muda
- **THEN** Salvar permanece indisponível ou apresenta validação clara até haver comentário humano válido; Resolvido, Aguardando Solicitante e Cancelado fixam a visibilidade em Público, e os demais destinos permitem Público ou Interno

### Requirement: Save pode encerrar ou cancelar após aplicar todas as mudanças válidas
O Save DEVE (MUST) aceitar alterações simultâneas dos quatro campos quando o estado resultante for Encerrado ou Cancelado. O bloqueio de edição funcional DEVE (MUST) passar a valer somente depois do commit dessa transação.

#### Scenario: Save que termina em Cancelado
- **WHEN** um chamado não terminal recebe no mesmo Save novo Responsável, Prioridade e Status Cancelado com comentário público válido
- **THEN** todas as mudanças válidas são persistidas juntas e o chamado passa a bloquear edições funcionais posteriores

#### Scenario: Reabertura é negada
- **WHEN** qualquer perfil tenta salvar campos funcionais de chamado Encerrado ou Cancelado
- **THEN** o Xano rejeita a operação sem reabrir nem modificar o chamado

### Requirement: Comentário operacional é independente do Save
O sistema DEVE (MUST) oferecer `Adicionar comentário` independente do Save, com texto não vazio e visibilidade Público ou Interno. Técnico, Diretoria e Administrador DEVEM (MUST) poder adicionar ambas as visibilidades inclusive em chamados terminais; o comentário DEVE (MUST) atualizar `ultima_atualizacao_em` sem modificar campo funcional.

#### Scenario: Comentário em chamado terminal
- **WHEN** um perfil operacional envia comentário Público ou Interno não vazio para chamado Encerrado ou Cancelado
- **THEN** o Xano cria somente o comentário e atualiza `ultima_atualizacao_em`, sem reabrir o chamado

#### Scenario: Comentário vazio
- **WHEN** o texto está ausente, vazio ou contém apenas espaços
- **THEN** o Xano rejeita a operação sem criar interação nem alterar `ultima_atualizacao_em`

### Requirement: Alteração efetiva produz um único evento estruturado
Cada Save com uma ou mais diferenças funcionais efetivas DEVE (MUST) criar exatamente um evento automático `alteracao_chamado`. O evento DEVE (MUST) identificar autor, chamado, instante e as diferenças anterior/resultante de Responsável, Status, Prioridade, Categoria e SLA que existirem; ele NÃO DEVE (MUST NOT) ser tratado como comentário humano.

#### Scenario: Save com múltiplas diferenças
- **WHEN** um Save altera Status, Prioridade, Categoria, SLA e Responsável
- **THEN** a timeline recebe um único `alteracao_chamado` contendo todas essas diferenças

#### Scenario: Save com mudança de status
- **WHEN** o Save altera Status com comentário obrigatório válido
- **THEN** a transação cria um comentário humano e, se houver diferença funcional, um único evento automático distinto

#### Scenario: Save sem diferença
- **WHEN** o Save não possui diferença funcional
- **THEN** ele cria zero eventos `alteracao_chamado`

### Requirement: Categoria inativa persistida permanece válida até ser trocada
O sistema DEVE (MUST) registrar em cada Categoria o campo booleano `ativo`, com padrão `true` para registros existentes e novos. O sistema DEVE (MUST) exibir Categoria persistida inativa e permitir Save de outros campos sem exigi-la como nova escolha. O catálogo de edição NÃO DEVE (MUST NOT) oferecer Categoria com `ativo = false`; a validação de Categoria ativa DEVE (MUST) ocorrer somente se seu valor for efetivamente alterado e NÃO DEVE (MUST NOT) usar `permite_abertura_manual`.

#### Scenario: Outra alteração preserva Categoria inativa
- **WHEN** o chamado possui Categoria inativa e o usuário altera somente Prioridade
- **THEN** o Save é válido e preserva a Categoria e o SLA aplicados

#### Scenario: Troca de Categoria inativa
- **WHEN** o usuário tenta substituir a Categoria atual por Categoria inativa ou inválida no cadastro vigente
- **THEN** o Xano rejeita toda a transação sem alterar o chamado

#### Scenario: Categoria ativa sem abertura manual
- **WHEN** Categoria possui `ativo = true` e `permite_abertura_manual = false`
- **THEN** ela permanece disponível como nova escolha na tratativa operacional

### Requirement: Troca de Categoria atualiza SLA aplicado sem reiniciar sua referência
Quando o Save altera efetivamente a Categoria, o Xano DEVE (MUST) gravar em `sla_horas_aplicado` o SLA da Categoria resultante. A referência temporal do SLA DEVE (MUST) permanecer a criação original do chamado e preservar as regras existentes de consumo e interrupção.

#### Scenario: Categoria com SLA diferente
- **WHEN** o usuário altera Categoria de SLA 8h para Categoria de SLA 4h
- **THEN** o chamado passa a ter `sla_horas_aplicado = 4h` sem reiniciar sua data de criação e o evento registra Categoria e SLA anterior/resultante

### Requirement: Timeline apresenta formatos históricos e novo evento
A timeline DEVE (MUST) reunir comentários, `atribuicao`, `reatribuicao`, `liberacao` e `alteracao_chamado` sem backfill ou conversão de históricos. A ordenação DEVE (MUST) usar o instante efetivo decrescente e `id` decrescente no empate.

#### Scenario: Coexistência de interações
- **WHEN** o chamado contém comentário legado, evento histórico de atribuição e novo `alteracao_chamado`
- **THEN** a timeline exibe os três no mesmo fluxo do mais recente para o mais antigo
