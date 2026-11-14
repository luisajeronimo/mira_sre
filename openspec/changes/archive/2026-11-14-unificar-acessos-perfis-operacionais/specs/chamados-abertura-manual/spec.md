## ADDED Requirements

### Requirement: Perfis operacionais iniciam abertura manual no Início
O Reflex DEVE (MUST) oferecer a Técnico, Diretoria e Administrador, em `/inicio`, a ação de abrir chamado com a mesma apresentação e posição do botão usado pelo Gerente, além da mesma composição de formulário em `/chamados/novo`. O Gerente DEVE (MUST) conservar seu fluxo e escopo de Loja; os três perfis operacionais DEVEM (MUST) escolher Totem globalmente. A apresentação compartilhada NÃO DEVE (MUST NOT) deslocar autorização ou regras de negócio do Xano para o Reflex. A gestão administrativa NÃO DEVE (MUST NOT) apresentar o formulário de chamado.

#### Scenario: Administrador parte do Início
- **WHEN** Administrador autenticado aciona Criar chamado em `/inicio`
- **THEN** abre o formulário compartilhado em `/chamados/novo`, com Totens globais elegíveis

#### Scenario: Gerente conserva a abertura
- **WHEN** Gerente autenticado aciona Criar chamado em `/inicio`
- **THEN** abre o mesmo formulário visual com Totens limitados pela própria Loja no Xano

#### Scenario: Técnico e Diretoria também abrem chamados
- **WHEN** Técnico ou Diretoria abre `/chamados/novo` com sessão concluída
- **THEN** recebe o mesmo formulário e contrato operacional global do Administrador, sem acessar Gestão

## MODIFIED Requirements

### Requirement: Administrador pode abrir chamado manual para qualquer Totem
A abertura manual DEVE (MUST) aceitar Técnico, Diretoria e Administrador autenticados em escopo global com os mesmos campos e validações funcionais do Gerente. O solicitante DEVE (MUST) ser o usuário operacional autenticado, e a Loja DEVE (MUST) corresponder ao vínculo do Totem no momento da abertura.

#### Scenario: Abertura global válida
- **WHEN** Administrador informa título, descrição, Totem, Categoria elegível e prioridade válidos
- **THEN** o Xano cria chamado manual com solicitante Administrador e Loja do Totem na abertura

#### Scenario: Tentativa de Loja diferente
- **WHEN** cliente tenta associar chamado manual a Loja diferente da Loja do Totem
- **THEN** o Xano rejeita ou desconsidera o dado forjado sem criar vínculo incorreto

## REMOVED Requirements

### Requirement: Administrador inicia abertura manual no Início
**Reason**: Substituído pela decisão humana de acessos operacionais equivalentes, que revoga as restrições de perfil anteriores.
**Migration**: Aplicar o requisito "Perfis operacionais iniciam abertura manual no Início" nesta mesma capacidade; contratos e dados históricos permanecem compatíveis.
