# Spec Delta

## ADDED Requirements

### Requirement: Campos administrativos possuem rótulos persistentes
Os campos existentes dos formulários de criação de usuário e de troca obrigatória de senha DEVEM (MUST) apresentar rótulos persistentes associados aos controles, legíveis antes e depois de digitar, conforme `DESIGN.md`.

#### Scenario: Criação de usuário
- **WHEN** Administrador abre o formulário de criação
- **THEN** Nome, E-mail, Perfil, Loja quando aplicável, Senha temporária e Confirmação possuem rótulos persistentes sem alterar campos ou validações

#### Scenario: Troca obrigatória de senha
- **WHEN** usuário abre o formulário de primeiro acesso
- **THEN** Nova senha e Confirmação possuem rótulos persistentes sem alterar o envio ou a política de senha
