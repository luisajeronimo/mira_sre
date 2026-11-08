# Spec Delta

## ADDED Requirements

### Requirement: Contratos administrativos específicos exigem Administrador
O Xano DEVE (MUST) autorizar somente Administrador autenticado e sem troca pendente a listar, consultar, criar, editar, transferir ou excluir Usuários, Lojas e Totens pelos contratos administrativos específicos. CRUDs genéricos DEVEM (MUST) continuar bloqueados.

#### Scenario: Chamada direta de outro perfil
- **WHEN** Gerente, Técnico ou Diretoria chama diretamente mutação administrativa
- **THEN** o Xano rejeita sem ler ou alterar o cadastro

#### Scenario: Administrador autorizado
- **WHEN** Administrador com sessão concluída chama contrato administrativo válido
- **THEN** o Xano executa somente a operação e os campos definidos nesse contrato

#### Scenario: Último Administrador protegido no backend
- **WHEN** cliente chama diretamente edição de perfil ou exclusão que deixaria zero Administradores
- **THEN** o Xano rejeita a mutação sem efeito parcial, mesmo se duas requisições ocorrerem ao mesmo tempo

### Requirement: Administrador abre chamado manual global
O Xano DEVE (MUST) permitir a Administrador criar chamado manual para Totem de qualquer Loja, derivando a Loja do Totem e o solicitante da sessão. A validação de título, descrição, Categoria, prioridade, SLA e demais regras de abertura manual DEVE (MUST) permanecer no backend.

#### Scenario: Abertura em outra Loja
- **WHEN** Administrador autenticado abre chamado válido para Totem de qualquer Loja
- **THEN** o Xano cria chamado manual com Loja do Totem e Administrador como solicitante humano

#### Scenario: Loja ou solicitante forjado
- **WHEN** cliente informa Loja ou solicitante diferente da relação e sessão autenticadas
- **THEN** o Xano ignora ou rejeita esses valores sem atribuir identidade ou Loja indevidas

### Requirement: Gerente usa Loja histórica comprovada do chamado
O Xano DEVE (MUST) autorizar o Gerente em lista, detalhe e comentários pela Loja comprovada na abertura de cada chamado. A Loja atual do Totem NÃO DEVE (MUST NOT) conceder acesso a chamado antigo de outra Loja. Sem Loja histórica demonstrável, o acesso do Gerente DEVE (MUST) falhar fechado.

#### Scenario: Totem transferido
- **WHEN** Gerente da Loja de destino solicita chamado anterior à transferência
- **THEN** o Xano rejeita sem expor o chamado ou suas interações

#### Scenario: Origem indeterminada
- **WHEN** a Loja histórica de um chamado legado não pode ser demonstrada
- **THEN** nenhum Gerente recebe acesso por inferência da Loja atual do Totem
