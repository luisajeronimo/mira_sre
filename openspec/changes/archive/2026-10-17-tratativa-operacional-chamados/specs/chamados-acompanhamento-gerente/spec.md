# Delta: chamados-acompanhamento-gerente

## MODIFIED Requirements

### Requirement: Gerente publica comentário público em chamado não terminal
O sistema DEVE (MUST) fornecer comando específico para o Gerente autenticado publicar comentário Público não vazio em chamado de sua Loja e jornada autorizada, inclusive quando estiver Encerrado ou Cancelado. Autor, visibilidade e `criado_em` DEVEM (MUST) ser definidos pelo Xano; o comando DEVE (MUST) atualizar `ultima_atualizacao_em` junto da criação, sem modificar campos funcionais nem reabrir chamado terminal.

#### Scenario: Comentário público válido
- **WHEN** Gerente autorizado envia conteúdo não vazio para chamado de sua Loja
- **THEN** o Xano cria comentário Público com autor da sessão, atualiza `ultima_atualizacao_em` e retorna somente o DTO sanitizado

#### Scenario: Chamado terminal permite comentário público
- **WHEN** o chamado da Loja do Gerente está Encerrado ou Cancelado e recebe comentário Público não vazio
- **THEN** o Xano cria somente o comentário, atualiza `ultima_atualizacao_em` e preserva os campos funcionais

#### Scenario: Gerente tenta comentário Interno
- **WHEN** o Gerente tenta criar comentário Interno ou informar visibilidade distinta de Público
- **THEN** o Xano rejeita a operação sem criar interação

#### Scenario: Comentário fora do escopo
- **WHEN** o Gerente tenta comentar chamado fora de sua Loja ou jornada autorizada
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
