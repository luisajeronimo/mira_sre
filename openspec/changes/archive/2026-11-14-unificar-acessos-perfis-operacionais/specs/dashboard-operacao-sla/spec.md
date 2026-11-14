## MODIFIED Requirements

### Requirement: Consulta executiva de operação exige Diretoria autenticada
Os contratos e painéis de volumetria e SLA DEVEM (MUST) atender a Técnico, Diretoria e Administrador autenticados, com sessão válida e troca de senha concluída. O Xano DEVE (MUST) aplicar a autorização a cada consulta antes de ler chamados.

#### Scenario: Diretoria consulta a operação
- **WHEN** usuário da Diretoria com sessão válida consulta os indicadores
- **THEN** recebe os agregados correspondentes aos filtros válidos

#### Scenario: Outro perfil ou sessão inválida
- **WHEN** Gerente, perfil não oficial, usuário anônimo ou sessão com troca pendente consulta diretamente o contrato
- **THEN** a consulta é negada sem dados de chamados ou SLA

#### Scenario: Todos os perfis operacionais consultam os indicadores
- **WHEN** Técnico, Diretoria ou Administrador com sessão concluída consulta os contratos e catálogos
- **THEN** recebe os mesmos indicadores e filtros globais
