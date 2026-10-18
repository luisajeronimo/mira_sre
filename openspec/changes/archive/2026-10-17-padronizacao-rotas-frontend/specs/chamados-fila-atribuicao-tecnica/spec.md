# Delta: chamados-fila-atribuicao-tecnica

## ADDED Requirements

### Requirement: Jornada global usa rotas canônicas de chamados
O Reflex DEVE (MUST) apresentar a fila global existente em `/inicio` e `/chamados` e seu detalhe operacional existente em `/chamados/[chamado_id]` para Técnico, Diretoria e Administrador. A jornada DEVE reutilizar `ChamadosTecnicoState`, componentes, filtros, timeline e tratativa atuais; ela NÃO DEVE (MUST NOT) converter Diretoria ou Administrador em responsável de chamado.

#### Scenario: Perfil global acessa início ou lista canônica
- **WHEN** Técnico, Diretoria ou Administrador autenticado acessa `/inicio` ou `/chamados`
- **THEN** o Reflex revalida a identidade e apresenta a fila global existente

#### Scenario: Detalhe canônico global
- **WHEN** Técnico, Diretoria ou Administrador autenticado acessa `/chamados/[chamado_id]`
- **THEN** o Reflex carrega o detalhe, a timeline e a tratativa operacional existentes conforme o contrato atual

#### Scenario: Escopo rápido exclusivo do Técnico
- **WHEN** Diretoria ou Administrador acessa a fila canônica
- **THEN** a interface não apresenta `Atribuídos a mim`; quando Técnico acessa a mesma rota, o escopo rápido aprovado permanece disponível

#### Scenario: Troca de identidade não reutiliza o contexto da fila
- **WHEN** um Técnico usa `Atribuídos a mim`, encerra a sessão e outra identidade acessa `/inicio` ou `/chamados`
- **THEN** o Reflex descarta antes da consulta os dados, filtros e escopo da identidade anterior e solicita a fila apenas com o escopo permitido ao novo perfil
- **AND WHEN** o mesmo Técnico inicia uma nova sessão
- **THEN** os filtros desse usuário podem ser mantidos, mas `Atribuídos a mim` volta para `Todos`

#### Scenario: Navegação global canônica
- **WHEN** perfil global segue link de detalhe, retorna à fila ou seleciona `Início`
- **THEN** a navegação usa as rotas canônicas sem alterar filtros, contratos Xano ou comportamento de tratativa

#### Scenario: Gerente acessa rota global canônica
- **WHEN** Gerente tenta acessar uma rota que resolveria para a jornada global
- **THEN** o Reflex não apresenta a jornada global e o Xano continua respondendo 403 para contrato global indevido
