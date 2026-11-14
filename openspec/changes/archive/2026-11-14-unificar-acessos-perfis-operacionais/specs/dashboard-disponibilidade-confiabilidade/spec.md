## MODIFIED Requirements

### Requirement: Consulta executiva exige Diretoria autenticada
O dashboard e seus contratos de leitura DEVEM (MUST) atender a Técnico, Diretoria e Administrador com sessão válida e troca de senha concluída. A autorização DEVE (MUST) ser aplicada pelo Xano em cada consulta; a rota protegida e a ocultação visual não concedem acesso.

#### Scenario: Diretoria consulta a rede
- **WHEN** usuário da Diretoria autenticado abre Indicadores ou consulta diretamente seus contratos
- **THEN** recebe dados globais correspondentes aos filtros válidos

#### Scenario: Outros perfis tentam consulta direta
- **WHEN** Gerente ou perfil não oficial chama o contrato de indicadores ou abre sua rota
- **THEN** o Xano responde 403 sem dados, e o Reflex não renderiza o dashboard

#### Scenario: Sessão inválida ou troca pendente
- **WHEN** a sessão é ausente, expirada ou possui troca obrigatória pendente
- **THEN** nenhuma métrica é retornada e a interface segue a proteção de sessão vigente

#### Scenario: Todos os perfis operacionais consultam os indicadores
- **WHEN** Técnico, Diretoria ou Administrador com sessão concluída consulta os contratos e catálogos
- **THEN** recebe os mesmos indicadores e filtros globais
