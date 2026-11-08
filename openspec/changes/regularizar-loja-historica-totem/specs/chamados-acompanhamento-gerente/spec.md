# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente consulta comentários públicos do chamado da própria Loja
O sistema DEVE (MUST) fornecer uma consulta específica de comentários públicos por chamado ao Gerente autenticado. Ela DEVE (MUST) autorizar o chamado pela Loja resolvida pelo vínculo histórico do Totem no `criado_em` do chamado (`vinculo-historico-totem-loja`), retornar somente DTO sanitizado de comentário público e ordenar por `criado_em` decrescente. O DTO público contém exclusivamente `id`, `conteudo`, `criado_em` e `autor`, sendo `autor` objeto nulo ou com somente o campo público `nome`; ele NÃO DEVE (MUST NOT) expor identificador de usuário, e-mail, perfil, Loja, credenciais ou qualquer atributo interno.

#### Scenario: Consulta autorizada ordenada
- **WHEN** um Gerente consulta os comentários públicos de chamado cuja Loja resolvida é a sua
- **THEN** recebe somente comentários públicos, do mais recente ao mais antigo, com conteúdo, data funcional e autor limitado ao nome público

#### Scenario: Relação de autor ausente ou incompatível
- **WHEN** um comentário público possui relação de autor ausente ou que não pode ser projetada com segurança
- **THEN** o DTO retorna `autor = null`, sem vazar identificador ou atributo interno e sem inferir autoria

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta comentários de chamado cuja Loja resolvida é outra Loja
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado sem Loja histórica
- **WHEN** um Gerente consulta comentários de chamado cuja Loja resolvida é nula
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta comentários de identificador inexistente
- **THEN** o Xano responde como recurso não encontrado
