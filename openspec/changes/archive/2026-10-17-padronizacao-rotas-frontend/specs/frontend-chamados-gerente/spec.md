# Delta: frontend-chamados-gerente

## ADDED Requirements

### Requirement: Jornada do Gerente usa rotas canônicas de chamados
O Reflex DEVE (MUST) apresentar ao Gerente a listagem local em `/inicio` e `/chamados`, a abertura manual em `/chamados/novo` e o detalhe local em `/chamados/[chamado_id]`. Essas rotas DEVEM reutilizar `ChamadosGerenteState`, componentes e contratos atuais, sem oferecer fila global, tratativa funcional ou capacidades adicionais.

#### Scenario: Gerente acessa lista canônica
- **WHEN** Gerente autenticado e sem pendência acessa `/inicio` ou `/chamados`
- **THEN** o Reflex revalida a sessão e apresenta somente a tabela de chamados da própria Loja com a ação existente de criar chamado

#### Scenario: Gerente acessa abertura canônica
- **WHEN** Gerente autenticado acessa `/chamados/novo`
- **THEN** o Reflex carrega os catálogos e o formulário existentes de abertura manual

#### Scenario: Gerente acessa detalhe canônico
- **WHEN** Gerente autenticado acessa `/chamados/[chamado_id]`
- **THEN** o Reflex apresenta o detalhe local e comentários públicos existentes, sem controles de tratativa

#### Scenario: Gerente recebe URL de fila global
- **WHEN** Gerente tenta acessar jornada global por URL canônica ou alias legado
- **THEN** o Reflex não apresenta fila ou detalhe global e o Xano continua negando qualquer chamada global indevida

#### Scenario: Navegação local canônica
- **WHEN** Gerente cria chamado, retorna do detalhe, descarta formulário ou seleciona `Início`
- **THEN** os links e redirecionamentos usam as rotas canônicas adequadas sem alterar requisição ao Xano
