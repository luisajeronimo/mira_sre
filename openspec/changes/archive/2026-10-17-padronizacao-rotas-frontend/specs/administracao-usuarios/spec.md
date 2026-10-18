# Delta: administracao-usuarios

## ADDED Requirements

### Requirement: Interface administrativa usa rota funcional de usuários
O Reflex DEVE (MUST) disponibilizar a interface existente de criação administrativa exclusivamente em `/administracao/usuarios` para Administrador autenticado e sem troca pendente. A antiga `/administracao` DEVE atuar somente como alias transitório protegido para essa rota. Esta mudança NÃO DEVE (MUST NOT) ampliar administração para Loja, Totem ou outra função ainda não implementada.

#### Scenario: Administrador acessa rota canônica
- **WHEN** Administrador autenticado e sem pendência acessa `/administracao/usuarios`
- **THEN** o Reflex apresenta o formulário administrativo existente e mantém os contratos de criação e consulta de Lojas atuais

#### Scenario: Perfil não administrativo acessa rota administrativa
- **WHEN** Gerente, Técnico ou Diretoria acessa a rota canônica ou o alias administrativo
- **THEN** o Reflex não apresenta o formulário e o Xano continua negando contratos administrativos indevidos

#### Scenario: Primeiro acesso pendente
- **WHEN** Administrador com troca obrigatória pendente acessa rota canônica ou alias administrativo
- **THEN** o Reflex redireciona para `/primeiro-acesso` antes de carregar catálogo ou formulário
