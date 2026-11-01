# Spec Delta

## ADDED Requirements

### Requirement: Casca autenticada usa linguagem visual desktop compartilhada
Após a confirmação da sessão, a casca autenticada DEVE (MUST) apresentar
sidebar e topbar em superfícies claras, com contexto da página e identidade da
sessão. A composição DEVE (MUST) usar a identidade visual definida e preservar
os destinos, a matriz de perfis e as rotas já aprovadas.

#### Scenario: Perfil autenticado abre rota protegida
- **WHEN** um perfil oficial confirmado abre uma rota protegida
- **THEN** a interface apresenta a única sidebar desktop existente, uma topbar
  de contexto e o conteúdo em canvas claro, sem criar destino, ação ou permissão
  adicional

#### Scenario: Navegação acessível permanece configurada por perfil
- **WHEN** a casca renderiza a navegação para um perfil autenticado
- **THEN** o destino ativo, o foco visível e os rótulos continuam distinguíveis
  sem depender exclusivamente de cor, e somente os itens previstos para o perfil
  são exibidos

#### Scenario: Fluxo público ou revalidação
- **WHEN** a sessão ainda não foi confirmada ou a rota é pública
- **THEN** a interface não apresenta a casca autenticada nem conteúdo protegido

### Requirement: Identificação e saída ficam concentradas na topbar
A casca autenticada DEVE (MUST) apresentar nome, cargo em maiúsculas e a ação
existente de saída uma única vez na topbar. A sidebar NÃO DEVE (MUST NOT)
duplicar identificação ou logout, e a mudança NÃO DEVE (MUST NOT) alterar a
sessão, matriz de navegação ou destinos configurados. A ação de saída DEVE
(MUST) usar o rose primário com contraste adequado.

#### Scenario: Sessão confirmada renderiza a casca
- **WHEN** um perfil oficial confirmado abre uma rota protegida
- **THEN** a topbar apresenta identificação e saída, e a sidebar mantém apenas
  marca e os itens de navegação autorizados
