## ADDED Requirements

### Requirement: Todas as páginas usam o favicon oficial do MIRA
A aplicação DEVE (MUST) declarar o logotipo oficial de `assets/mira-logo.svg` como ícone da aba do navegador nas páginas públicas e autenticadas, inclusive no primeiro acesso e em acessos diretos. O asset DEVE (MUST) estar disponível na publicação, preservando a identidade da marca e os fluxos de autenticação e navegação.

#### Scenario: Login ou primeiro acesso é aberto diretamente
- **WHEN** o navegador carrega uma dessas páginas
- **THEN** o documento declara o ícone oficial e seu recurso responde sem exigir sessão

#### Scenario: Página autenticada é aberta após a publicação
- **WHEN** uma sessão autorizada navega entre as rotas do MIRA
- **THEN** as páginas mantêm o ícone oficial, sem depender de declaração exclusiva da tela de login
