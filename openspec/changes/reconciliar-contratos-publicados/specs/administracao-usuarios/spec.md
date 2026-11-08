# Spec Delta

## MODIFIED Requirements

### Requirement: Associação de Loja segue o perfil criado
O sistema MUST exigir `lojas_id` de Loja existente e ativa para Gerente. Uma Loja é ativa quando seu `status` é `Ativa`, `ativa` ou, por compatibilidade com Lojas legadas, `Ativo`; qualquer outro valor, inclusive ausente, a torna inativa para esta regra. Para Técnico, Diretoria e Administrador, `lojas_id` DEVE ser nulo e a requisição que o informar DEVE ser rejeitada.

#### Scenario: Gerente com Loja existente
- **WHEN** um Administrador cria Gerente com `lojas_id` de uma Loja existente com `status` `Ativa` ou `ativa`
- **THEN** o sistema cria o Gerente associado àquela Loja

#### Scenario: Gerente com Loja legada ativa
- **WHEN** um Administrador cria Gerente com `lojas_id` de uma Loja existente com `status` `Ativo`
- **THEN** o sistema cria o Gerente associado àquela Loja

#### Scenario: Gerente sem Loja ou com Loja inexistente
- **WHEN** a criação de Gerente omite `lojas_id` ou informa uma Loja inexistente
- **THEN** o sistema rejeita a criação sem persistir usuário

#### Scenario: Gerente com Loja Inativa
- **WHEN** a criação de Gerente informa `lojas_id` de uma Loja existente cujo `status` não é `Ativa`, `ativa` nem `Ativo`
- **THEN** o sistema rejeita a criação como entrada inválida, sem persistir usuário

#### Scenario: Perfil global com Loja informada
- **WHEN** a criação de Técnico, Diretoria ou Administrador informa `lojas_id`
- **THEN** o sistema rejeita a criação sem ignorar silenciosamente o campo

### Requirement: Administração consulta opções mínimas de Loja para criar Gerente
O sistema MUST oferecer `GET /administracao/lojas` exclusivamente a Administrador autenticado e aprovado pelo gate central de primeiro acesso. A resposta MUST conter somente a lista de opções de Lojas ativas (`status` `Ativa`, `ativa` ou `Ativo`), cada uma com `id` e `nome`, para preencher o seletor da criação de Gerente. Administrador pendente, Gerente, Técnico, Diretoria e pessoa não autenticada MUST ser rejeitados. Esta capability NÃO DEVE ampliar as permissões de `GET /lojas`, `GET /lojas/{id}` ou de gestão de Lojas.

#### Scenario: Administrador concluído consulta opções para criação
- **WHEN** um Administrador autenticado e sem pendência consulta `GET /administracao/lojas`
- **THEN** o sistema retorna somente as Lojas ativas em uma lista mínima de `{id, nome}`

#### Scenario: Loja inativa não é opção
- **WHEN** existe Loja cujo `status` não é `Ativa`, `ativa` nem `Ativo`
- **THEN** ela não aparece nas opções de `GET /administracao/lojas`

#### Scenario: Sessão pendente ou perfil não administrativo consulta opções
- **WHEN** Administrador pendente, Gerente, Técnico, Diretoria ou pessoa não autenticada chama `GET /administracao/lojas`
- **THEN** o sistema rejeita a consulta sem ampliar a autorização geral de Lojas
