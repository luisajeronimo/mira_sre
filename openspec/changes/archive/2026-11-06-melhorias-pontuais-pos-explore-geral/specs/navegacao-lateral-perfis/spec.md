## MODIFIED Requirements

### Requirement: Casca autenticada usa linguagem visual desktop compartilhada
Após a confirmação da sessão, a casca autenticada DEVE (MUST) apresentar
sidebar e topbar em superfícies claras, com identidade da sessão na topbar. O
contexto da página DEVE (MUST) permanecer reconhecível pela navegação e pelo
conteúdo; a topbar NÃO DEVE (MUST NOT) exibir título da rota em nenhum perfil.
A composição DEVE (MUST) usar a identidade visual definida e preservar os
destinos, a matriz de perfis e as rotas já aprovadas.

#### Scenario: Perfil autenticado abre rota protegida
- **WHEN** um perfil oficial confirmado abre uma rota protegida
- **THEN** a interface apresenta a única sidebar desktop existente, uma topbar
  com identidade e saída e o conteúdo em canvas claro, sem criar destino, ação
  ou permissão adicional

#### Scenario: Título da rota fora da topbar
- **WHEN** qualquer perfil oficial navega entre rotas protegidas
- **THEN** a topbar não exibe títulos como Início, Novo chamado, Detalhe do
  chamado, Monitoramento ou Administração de usuários

#### Scenario: Navegação acessível permanece configurada por perfil
- **WHEN** a casca renderiza a navegação para um perfil autenticado
- **THEN** o destino ativo, o foco visível e os rótulos continuam distinguíveis
  sem depender exclusivamente de cor, e somente os itens previstos para o perfil
  são exibidos

#### Scenario: Fluxo público ou revalidação
- **WHEN** a sessão ainda não foi confirmada ou a rota é pública
- **THEN** a interface não apresenta a casca autenticada nem conteúdo protegido
