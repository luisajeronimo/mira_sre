# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente consulta comentários públicos do chamado da própria Loja
O sistema DEVE (MUST) fornecer consulta específica de comentários públicos por chamado ao Gerente autenticado, autorizada pela Loja resolvida pelo vínculo histórico do Totem em `criado_em` (`vinculo-historico-totem-loja`), com resultados em ordem decrescente de `criado_em`. O DTO contém somente `id`, `conteudo`, `criado_em` e `autor`. `autor` é nulo ou objeto apenas com `nome`; para o comentário comprovadamente gerado pelo encerramento sob comando, DEVE (MUST) ser `{nome: "Sistema"}`. Nenhum identificador de usuário, e-mail, perfil, Loja, credencial ou dado interno do autor é exposto.

#### Scenario: Consulta autorizada ordenada
- **WHEN** um Gerente consulta comentários públicos de chamado comprovadamente aberto em sua Loja
- **THEN** recebe somente comentários públicos, do mais recente ao mais antigo, com conteúdo, data funcional e autor limitado ao nome público

#### Scenario: Comentário gerado pelo encerramento sob comando
- **WHEN** a consulta inclui o comentário público vinculado à transição `Resolvido` → `Encerrado` criada pelo comando de encerramento, sem usuário humano
- **THEN** o DTO desse comentário retorna `autor = {nome: "Sistema"}`

#### Scenario: Relação de autor ausente ou incompatível
- **WHEN** um comentário público não possui autor projetável com segurança e não é comprovadamente o comentário do encerramento sob comando
- **THEN** o DTO retorna `autor = null`, sem inferir autoria nem expor identificador ou atributo interno

#### Scenario: Chamado de outra Loja
- **WHEN** um Gerente consulta comentários de chamado comprovadamente aberto em outra Loja
- **THEN** o Xano responde como não autorizado sem retornar comentários

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta comentários de identificador inexistente
- **THEN** o Xano responde como recurso não encontrado

#### Scenario: Loja histórica não demonstrável
- **WHEN** não é possível comprovar a Loja de abertura do chamado legado
- **THEN** o Xano não libera comentários ao Gerente por inferência da Loja atual do Totem

#### Scenario: Chamado sem Loja histórica
- **WHEN** um Gerente consulta comentários de chamado cuja Loja resolvida é nula
- **THEN** o Xano responde como não autorizado sem retornar comentários
