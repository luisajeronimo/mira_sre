# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente consulta comentários públicos do chamado da própria Loja
O sistema DEVE (MUST) fornecer uma consulta específica de comentários públicos por chamado ao Gerente autenticado. Ela DEVE (MUST) autorizar o chamado pela Loja histórica demonstrável em `criado_em`, retornar somente DTO sanitizado de comentário público e ordenar por `criado_em` decrescente. O DTO público contém exclusivamente `id`, `conteudo`, `criado_em` e `autor`, sendo `autor` objeto nulo ou com somente o campo público `nome`; ele NÃO DEVE (MUST NOT) expor identificador de usuário, e-mail, perfil, Loja, credenciais ou qualquer atributo interno.

#### Scenario: Consulta autorizada ordenada
- **WHEN** um Gerente consulta comentários públicos de chamado comprovadamente aberto em sua Loja
- **THEN** recebe somente comentários públicos, do mais recente ao mais antigo, com conteúdo, data funcional e autor limitado ao nome público

#### Scenario: Relação de autor ausente ou incompatível
- **WHEN** um comentário público possui relação de autor ausente ou que não pode ser projetada com segurança
- **THEN** o DTO retorna `autor = null`, sem vazar identificador ou atributo interno e sem inferir autoria

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta comentários de chamado comprovadamente aberto em outra Loja
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta comentários de identificador inexistente
- **THEN** o Xano responde como recurso não encontrado

#### Scenario: Loja histórica não demonstrável
- **WHEN** não é possível comprovar a Loja de abertura do chamado legado
- **THEN** o Xano não libera comentários ao Gerente por inferência da Loja atual do Totem

### Requirement: Gerente publica comentário público em chamado não terminal
O sistema DEVE (MUST) fornecer comando específico para o Gerente autenticado publicar comentário Público não vazio em chamado historicamente autorizado de sua Loja, inclusive quando estiver Encerrado ou Cancelado. Autor, visibilidade e `criado_em` DEVEM (MUST) ser definidos pelo Xano; o comando DEVE (MUST) atualizar `ultima_atualizacao_em` junto da criação, sem modificar campos funcionais nem reabrir chamado terminal.

#### Scenario: Comentário público válido
- **WHEN** Gerente autorizado envia conteúdo não vazio para chamado historicamente autorizado de sua Loja
- **THEN** o Xano cria comentário Público com autor da sessão, atualiza `ultima_atualizacao_em` e retorna somente o DTO sanitizado

#### Scenario: Chamado terminal permite comentário público
- **WHEN** o chamado autorizado da Loja do Gerente está Encerrado ou Cancelado e recebe comentário Público não vazio
- **THEN** o Xano cria somente o comentário, atualiza `ultima_atualizacao_em` e preserva os campos funcionais

#### Scenario: Gerente tenta comentário Interno
- **WHEN** o Gerente tenta criar comentário Interno ou informar visibilidade distinta de Público
- **THEN** o Xano rejeita a operação sem criar interação

#### Scenario: Comentário fora do escopo
- **WHEN** o Gerente tenta comentar chamado fora da Loja histórica comprovada de sua sessão ou jornada autorizada
- **THEN** o Xano rejeita a operação sem expor ou alterar o chamado

#### Scenario: Autoridade do cliente é ignorada
- **WHEN** o cliente tenta informar autor, Loja, timestamp, status ou outro campo funcional junto do comentário
- **THEN** o Xano usa somente identidade, escopo, visibilidade Pública e data definidos pelo backend

#### Scenario: Comentário vazio ou somente espaços
- **WHEN** o conteúdo está ausente, vazio ou fica vazio após remoção de espaços nas extremidades
- **THEN** o Xano rejeita a operação sem criar interação ou alterar `ultima_atualizacao_em`

#### Scenario: Chamado terminal permanece somente leitura
- **WHEN** o chamado possui status Encerrado ou Cancelado
- **THEN** o Gerente pode consultar e publicar comentário Público autorizado, mas não altera nenhum campo funcional

### Requirement: Visibilidade de comentário não define autorização do chamado
Público/Interno DEVE (MUST) classificar somente comentários. O acesso do Gerente ao chamado e ao status atual DEVE (MUST) continuar derivado da sessão e da Loja histórica demonstrável na abertura. O contrato público de comentários DEVE (MUST) retornar somente interações de comentário explicitamente públicas, sem inferir que evento operacional sem visibilidade seja público ou privado.

#### Scenario: Gerente consulta status atual
- **WHEN** o Gerente autorizado abre chamado comprovadamente de sua Loja após alteração operacional de Status
- **THEN** o detalhe apresenta o Status atual persistido independentemente da visibilidade dos comentários associados

#### Scenario: Comentário interno permanece protegido
- **WHEN** chamado autorizado possui comentário Interno e eventos operacionais
- **THEN** a consulta pública não retorna o comentário Interno nem usa os eventos para contornar essa restrição

#### Scenario: Evento operacional não é comentário privado
- **WHEN** evento operacional novo ou histórico não possui classificação funcional de visibilidade
- **THEN** o contrato de comentários não o retorna nem o classifica como comentário Público ou Interno

#### Scenario: Escopo da change no histórico do Gerente
- **WHEN** o Gerente consulta o acompanhamento autorizado
- **THEN** permanece com o detalhe atual e os comentários públicos vigentes, sem receber por esta change a timeline operacional global dos perfis internos

## ADDED Requirements

### Requirement: Transferência de Totem preserva escopo histórico de chamado
Listagem, detalhe e comentários do Gerente DEVEM (MUST) autorizar chamados pela Loja demonstrável em `criado_em`. Uma transferência NÃO DEVE (MUST NOT) expor chamados antigos ao Gerente da Loja de destino nem ocultar da origem os chamados cuja Loja histórica seja comprovada. Sem comprovação, a autorização DEVE (MUST) falhar fechada.

#### Scenario: Gerente da Loja de origem
- **WHEN** Totem é transferido e Gerente da Loja de origem consulta chamado anterior com vínculo histórico comprovado
- **THEN** o Xano mantém o chamado consultável e comentável conforme as regras existentes da jornada

#### Scenario: Gerente da Loja de destino
- **WHEN** Gerente da Loja de destino tenta consultar chamado anterior à transferência
- **THEN** o Xano rejeita sem expor chamado ou comentários

#### Scenario: Loja de origem não demonstrável
- **WHEN** um chamado legado anterior ao primeiro vínculo comprovado não permite determinar a Loja da abertura
- **THEN** nenhum Gerente o recebe por inferência do vínculo atual; o registro permanece preservado

#### Scenario: Loja Inativa existente
- **WHEN** Loja do Gerente já vinculado passa a `Inativa`
- **THEN** ele continua a consultar e comentar chamados historicamente autorizados conforme as regras existentes
