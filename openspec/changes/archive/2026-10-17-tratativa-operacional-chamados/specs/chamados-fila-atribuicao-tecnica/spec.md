# Delta: chamados-fila-atribuicao-tecnica

## MODIFIED Requirements

### Requirement: Dados de responsável e atribuição permanecem compatíveis
O sistema DEVE (MUST) substituir, na jornada operacional, comandos imediatos de assumir, atribuir, reatribuir e liberar por Save pendente de Responsável. A fila e o detalhe permanecem contratos de consulta; ao concluir esta change, somente o Save transacional é caminho funcional autorizado para mudança de responsável, sem alterar status.

#### Scenario: Detalhe não oferece controles imediatos de responsável
- **WHEN** Técnico, Diretoria ou Administrador abre um chamado não terminal
- **THEN** a jornada operacional apresenta apenas o campo `Responsável` e o botão Salvar, sem controles separados Assumir, Atribuir, Reatribuir ou Liberar

#### Scenario: Contratos anteriores não formam caminho alternativo de tratativa
- **WHEN** a migração técnica interna concluir
- **THEN** comandos imediatos anteriores não permanecem autorizados como caminho funcional alternativo para alterar Responsável

#### Scenario: Fila preserva escopo e consulta
- **WHEN** um perfil autorizado consulta a fila global ou o detalhe
- **THEN** Todos, Atribuídos a mim, filtros, pesquisa, tabela e DTO de consulta mantêm seu comportamento aprovado

#### Scenario: Atribuição via Save válida
- **WHEN** um perfil operacional salva Responsável Técnico em chamado não terminal sem responsável
- **THEN** o Save aplica atribuição conforme a spec de tratativa, sem usar comando imediato

#### Scenario: Save sem diferença de Responsável
- **WHEN** o Save informa Responsável igual ao já persistido e não há outra diferença funcional
- **THEN** o Xano retorna o detalhe sem alterar `tecnico_id`, `atribuido_em`, `ultima_atualizacao_em` ou histórico

#### Scenario: Responsável divergente no Save
- **WHEN** o estado persistido no momento do Save diverge do rascunho de responsável do cliente
- **THEN** o Xano valida o estado atual e não sobrescreve silenciosamente mudança incompatível

#### Scenario: Dois Técnicos concorrem
- **WHEN** duas pessoas salvam mudanças de Responsável simultaneamente
- **THEN** o Xano aplica a transação conforme o estado persistido e retorna o detalhe canônico sem afirmar garantia matemática além dos recursos Free

#### Scenario: Chamado inelegível para edição funcional
- **WHEN** o Save tenta editar Responsável de chamado Encerrado, Cancelado ou com estado inválido
- **THEN** o Xano rejeita a transação sem efeito parcial

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** o responsável atual é Técnico diferente do ator autenticado
- **THEN** Técnico, Diretoria e Administrador podem selecioná-lo ou trocá-lo pelo Save conforme a autorização da tratativa

#### Scenario: Campos sob autoridade do Xano
- **WHEN** o cliente informa timestamp, autor de evento ou valores funcionais fora do contrato
- **THEN** o Xano rejeita ou ignora esses valores sem permitir substituir regras de backend

#### Scenario: Registro legado
- **WHEN** a consulta encontra chamado existente sem data de atribuição persistida
- **THEN** o registro é preservado e `atribuido_em` permanece nulo quando não houver valor persistido

#### Scenario: Dados retornados pelo detalhe
- **WHEN** o chamado possui responsável e data de atribuição persistidos
- **THEN** o detalhe canônico os retorna sem inferir ou alterar valores

### Requirement: Autorização e erros da consulta técnica são estáveis
Os contratos de consulta e tratativa global DEVEM (MUST) exigir autenticação e aplicar no Xano os perfis e regras funcionais autorizados. Falha de sessão DEVE (MUST) ser 401, perfil ou escopo sem permissão 403, chamado inexistente 404, entrada ou estado funcional inválido 422 e falha interna 5xx; CRUD genérico NÃO DEVE (MUST NOT) contornar a autorização.

#### Scenario: Erro de autenticação e autorização
- **WHEN** uma chamada de tratativa recebe sessão inválida ou perfil sem permissão
- **THEN** o Xano responde respectivamente 401 ou 403 sem alterar chamado ou interações

#### Scenario: Contrato de Save inválido
- **WHEN** o cliente informa valor incompatível para o Save
- **THEN** o Xano responde 422 sem persistir efeito parcial

#### Scenario: Sessão ausente
- **WHEN** rota de consulta ou tratativa recebe requisição sem sessão válida
- **THEN** o Xano responde 401 sem consultar ou alterar chamado

#### Scenario: Perfil sem acesso global
- **WHEN** um Gerente solicita a fila ou detalhe técnico global
- **THEN** o Xano responde 403 sem expor dados

#### Scenario: Gerente ou Diretoria tenta usar rota técnica
- **WHEN** Gerente usa rota global ou perfil não autorizado usa operação fora da tratativa prevista
- **THEN** o Xano responde 403 sem expor ou alterar chamado

#### Scenario: CRUD genérico continua negado
- **WHEN** usuário tenta alterar chamado por CRUD genérico
- **THEN** nenhum chamado é modificado

### Requirement: Reflex oferece jornada técnica de consulta global
O Reflex DEVE (MUST) preservar a fila e o detalhe globais existentes e acrescentar a tratativa pendente somente ao detalhe. A interface DEVE (MUST) manter Estado persistido e pendente distintos, usar a resposta canônica pós-commit depois de Salvar e manter erro, carregamento, vazio e sucesso mutuamente coerentes.

#### Scenario: Save bem-sucedido atualiza o detalhe
- **WHEN** o Xano retorna sucesso para Save
- **THEN** o Reflex substitui valores persistidos e pendentes pelo detalhe retornado, sem alterar a fila por filtro local

#### Scenario: Save falha
- **WHEN** o Xano rejeita ou falha ao salvar
- **THEN** o Reflex informa a falha, conserva o detalhe persistido e não apresenta seleção pendente como se tivesse sido confirmada

#### Scenario: Status pendente exige comentário no Reflex
- **WHEN** o usuário altera Status no rascunho
- **THEN** o Reflex exige comentário associado antes de Salvar, fixa Público para Resolvido, Aguardando Solicitante e Cancelado e permite Público ou Interno para os demais destinos, sem substituir a validação definitiva do Xano

#### Scenario: Escopo rápido exclusivo do Técnico
- **WHEN** Diretoria ou Administrador acessa a fila
- **THEN** a interface preserva a tabela global sem apresentar `Atribuídos a mim`

#### Scenario: Técnico carrega a fila
- **WHEN** Técnico autenticado acessa a fila
- **THEN** o Reflex preserva a tabela global e seus estados aprovados de carregamento, vazio, sucesso e erro

#### Scenario: Chamado terminal
- **WHEN** a interface apresenta chamado `Encerrado` ou `Cancelado`
- **THEN** ela mantém o detalhe disponível para consulta e bloqueia edição funcional

#### Scenario: Save de Responsável bem-sucedido
- **WHEN** o Xano retorna sucesso para Save que atribui Responsável
- **THEN** o Reflex atualiza o detalhe pelo DTO canônico e a fila é atualizada ou recarregada sem aplicar filtro local

#### Scenario: Conflito ao salvar Responsável
- **WHEN** o Xano informa conflito ou estado divergente ao salvar responsável
- **THEN** o Reflex informa a falha sem substituir o detalhe confirmado e recarrega quando necessário

#### Scenario: Sessão ou autorização rejeitada
- **WHEN** rota de tratativa responde 401 ou 403
- **THEN** o Reflex encerra sessão em 401, preserva-a em 403 e não trata proteção visual como autorização

#### Scenario: Erro de contrato ou carregamento da fila
- **WHEN** a consulta da fila recebe resposta incompatível, falha de rede ou filtro inválido
- **THEN** o Reflex informa o erro correspondente sem encerrar a sessão nem apresentar a falha como problema de identidade

#### Scenario: Consulta não oferece controles imediatos de responsável
- **WHEN** um perfil apenas consulta fila ou detalhe sem editar o rascunho
- **THEN** a consulta não altera o chamado e a fila não passa a oferecer controles imediatos de responsável
