# Delta: estabilidade das interações da lista do Gerente

## MODIFIED Requirements

### Requirement: Jornada possui estados seguros de carregamento e falha
O sistema DEVE (MUST) concluir o estado de carregamento da lista em sucesso,
erro, cancelamento lógico ou redirecionamento. Uma nova ordenação ou filtro
enquanto houver consulta em andamento NÃO DEVE (MUST NOT) abrir uma tempestade
de requisições equivalentes nem permitir que resposta obsoleta sobrescreva uma
consulta mais recente. Uma intenção posterior DEVE (MUST) ser coalescida em no
m máximo uma nova consulta após sucesso da atual.

#### Scenario: Consulta concorrente de lista
- **WHEN** o Gerente dispara duas interações de lista antes da primeira resposta
- **THEN** o State mantém somente uma consulta em andamento e, após sucesso,
  executa no máximo uma nova consulta usando os critérios atuais

#### Scenario: Sessão expirada durante operação
- **WHEN** um contrato funcional responde 401
- **THEN** o Reflex limpa a sessão local e redireciona para `/login` sem
  tentar renovar o token

#### Scenario: Operação não autorizada
- **WHEN** um contrato funcional responde 403
- **THEN** o Reflex mantém a sessão autenticada e apresenta a negação sem
  exibir os dados solicitados

#### Scenario: Recurso não encontrado
- **WHEN** a consulta de detalhe responde 404
- **THEN** o Reflex informa que o chamado não foi encontrado sem encerrar a
  sessão

#### Scenario: Entrada ou resposta incompatível
- **WHEN** a criação responde 422 ou uma resposta não corresponde ao formato
  funcional esperado
- **THEN** o Reflex apresenta erro de validação ou contrato sem publicar dados
  inconsistentes

#### Scenario: Serviço indisponível
- **WHEN** ocorre timeout, falha de conexão ou resposta 5xx
- **THEN** o Reflex informa indisponibilidade temporária e oferece nova
  tentativa segura quando aplicável

#### Scenario: Falha transitória recuperável
- **WHEN** uma consulta de lista falha por timeout, conexão, 5xx ou limite 429
- **THEN** o loading termina, a sessão confirmada permanece válida, a mensagem
  é sanitizada e uma nova ação explícita consegue consultar novamente

#### Scenario: Limite de requisições
- **WHEN** o Xano responde 429 com ou sem `Retry-After`
- **THEN** o cliente classifica a resposta como indisponibilidade transitória,
  não limpa a sessão e não inicia retry agressivo

#### Scenario: Catálogo secundário indisponível
- **WHEN** `GET /gerente/ativos` falha durante a carga inicial mas
  `GET /gerente/chamados` retorna sucesso
- **THEN** os chamados e contadores permanecem visíveis, sem invalidar a sessão

#### Scenario: Falha real de autenticação
- **WHEN** uma consulta funcional responde 401
- **THEN** o State limpa a sessão e redireciona para login, preservando a
  distinção entre autenticação e indisponibilidade

### Requirement: Reflex controla filtros, ordenação e contadores da lista
O State DEVE (MUST) reutilizar o catálogo de ativos já carregado ao aplicar
ordenação, filtros ou limpeza. Essas interações DEVEM (MUST) consultar o
endpoint de chamados e NÃO DEVEM (MUST NOT) repetir consultas auxiliares
desnecessárias que possam gerar request storm.

#### Scenario: Ordenações consecutivas
- **WHEN** o Gerente alterna a ordenação várias vezes após o catálogo de ativos
  ter sido carregado
- **THEN** cada consulta de lista mantém a sessão e não dispara nova consulta
  de ativos

#### Scenario: Aplicação e limpeza de filtros
- **WHEN** o Gerente aplica ou limpa critérios de filtro
- **THEN** o State consulta novamente a lista, preserva a ordenação
  selecionada e apresenta os critérios efetivamente aplicados

#### Scenario: Ordenação de coluna
- **WHEN** o Gerente escolhe uma coluna ordenável e direção
- **THEN** o Reflex solicita a ordenação autorizada ao backend, sem ordenar
  somente a coleção local

#### Scenario: Falha de consulta não encerra sessão confirmada
- **WHEN** uma consulta de lista, filtro ou ordenação falha por
  indisponibilidade, timeout ou contrato incompatível
- **THEN** o Reflex apresenta erro sanitizado de serviço e preserva a
  identidade já confirmada; somente falha real de autenticação pode
  redirecionar ao login

#### Scenario: Contadores da consulta atual
- **WHEN** a lista responde a uma consulta com ou sem filtros
- **THEN** a interface apresenta o total filtrado e o tamanho atual de
  `items`
