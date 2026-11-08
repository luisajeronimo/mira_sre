# administracao-lojas Specification

## Purpose

Definir a gestão administrativa de Lojas da rede, sua situação e a proteção dos vínculos que sustentam operação e histórico do MIRA.

## Requirements

### Requirement: Administrador cria Loja com dados obrigatórios
O Xano DEVE (MUST) permitir somente a Administrador autenticado e sem troca de senha pendente criar Loja com nome, endereço e região não vazios. A situação de toda Loja nova DEVE (MUST) ser `Ativa`, definida pelo backend.

#### Scenario: Criação válida
- **WHEN** Administrador cria Loja com os três dados obrigatórios
- **THEN** a Loja recebe ID persistido e situação `Ativa`, independentemente de situação enviada pelo cliente

#### Scenario: Campo obrigatório ausente
- **WHEN** nome, endereço ou região está ausente ou vazio após remoção de espaços nas extremidades
- **THEN** o Xano rejeita a criação sem persistir Loja

### Requirement: Administração lista e consulta Lojas
O Xano DEVE (MUST) fornecer listagem e detalhe administrativos de Lojas, incluindo `Ativa` e `Inativa`, exclusivamente ao Administrador. Essas respostas DEVEM (MUST) conter somente os dados cadastrais necessários à gestão.

#### Scenario: Consulta de Loja Inativa
- **WHEN** Administrador consulta uma Loja `Inativa`
- **THEN** a Loja continua disponível com seus dados e situação

#### Scenario: Perfil indevido
- **WHEN** Gerente, Técnico, Diretoria, sessão pendente ou pessoa sem sessão consulta contrato administrativo
- **THEN** o Xano rejeita a consulta sem expor o cadastro

### Requirement: Administrador edita dados e situação da Loja
O Xano DEVE (MUST) permitir ao Administrador alterar nome, endereço, região e situação entre `Ativa` e `Inativa`, mantendo ID e vínculos existentes. A inativação NÃO DEVE (MUST NOT) alterar nem excluir automaticamente Gerentes, Totens ou registros históricos.

#### Scenario: Inativação com vínculos
- **WHEN** Administrador inativa Loja que já possui Gerentes ou Totens
- **THEN** a situação muda e os registros vinculados permanecem intactos

#### Scenario: Situação inválida
- **WHEN** edição informa situação diferente de `Ativa` ou `Inativa`
- **THEN** o Xano rejeita a alteração sem modificar a Loja

#### Scenario: Reativação
- **WHEN** Administrador altera Loja `Inativa` para `Ativa`
- **THEN** a Loja volta a aceitar novos vínculos de Gerentes e Totens conforme as validações existentes

### Requirement: Loja Inativa não recebe novos vínculos
O Xano DEVE (MUST) rejeitar criação ou transferência de Gerente ou Totem para Loja `Inativa`. A situação da Loja NÃO DEVE (MUST NOT) ser usada para apagar ou reclassificar vínculos anteriores.

#### Scenario: Novo vínculo com Loja Inativa
- **WHEN** criação ou transferência aponta para Loja `Inativa`
- **THEN** a operação é rejeitada sem alterar Gerente ou Totem

### Requirement: Inativação não interrompe a operação existente
A situação `Inativa` NÃO DEVE (MUST NOT) suspender automaticamente Gerentes e Totens já vinculados, monitoramento, abertura manual ou automática de chamados, tratativa, comentários, atribuição ou acompanhamento autorizados. Ela NÃO DEVE (MUST NOT) transformar Totem em `Offline` nem modificar chamados ou telemetrias.

#### Scenario: Gerente já vinculado
- **WHEN** Loja de um Gerente existente se torna `Inativa`
- **THEN** ele conserva acesso e permissões a chamados conforme o escopo aprovado, sem receber vínculo novo

#### Scenario: Totem já vinculado
- **WHEN** Loja de Totem existente se torna `Inativa`
- **THEN** o Totem continua monitorado, sem transição `Offline` causada pela situação cadastral

#### Scenario: Chamados em Loja Inativa
- **WHEN** há abertura manual ou automática, tratativa, atribuição, comentário ou acompanhamento elegível em Loja `Inativa`
- **THEN** a operação segue as regras existentes sem bloqueio causado apenas pela situação da Loja

### Requirement: Exclusão física de Loja respeita dependências
O Xano DEVE (MUST) excluir fisicamente Loja somente quando não houver Gerente, Totem, preferência ou outro vínculo ou histórico impeditivo. A exclusão NÃO DEVE (MUST NOT) produzir cascata nem apagar histórico operacional.

#### Scenario: Loja sem dependências
- **WHEN** Administrador exclui Loja existente sem vínculos ou histórico impeditivos
- **THEN** somente essa Loja é removida

#### Scenario: Loja com dependência
- **WHEN** a Loja possui vínculo ou histórico impeditivo
- **THEN** o Xano retorna erro funcional e não remove nenhum registro
