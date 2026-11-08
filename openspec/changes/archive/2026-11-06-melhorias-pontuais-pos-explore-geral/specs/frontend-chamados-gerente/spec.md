# Spec Delta

## ADDED Requirements

### Requirement: Estado local da jornada do Gerente é isolado por sessão
O Reflex DEVE (MUST) descartar dados protegidos, rascunhos e preferências em memória da jornada do Gerente ao sair da sessão e antes de apresentar ou usar esses dados em outra identidade ou nova sessão. A preferência persistida DEVE (MUST) ser restaurada somente para o Gerente autenticado atual.

#### Scenario: Logout da jornada do Gerente
- **WHEN** um Gerente encerra a sessão com lista, detalhe ou filtros carregados
- **THEN** a interface protegida deixa de apresentar esses dados e o contexto local do Gerente é descartado

#### Scenario: Outro Gerente entra na mesma sessão do navegador
- **WHEN** um Gerente diferente autentica após a saída do anterior
- **THEN** nenhum chamado, comentário, rascunho, catálogo ou filtro em memória do usuário anterior é apresentado ou enviado em consulta

#### Scenario: Mesmo Gerente inicia nova sessão
- **WHEN** o mesmo Gerente autentica novamente após logout
- **THEN** os dados efêmeros anteriores não reaparecem e a preferência durável é relida para a sessão atual antes da consulta

#### Scenario: Sessão expira durante consulta
- **WHEN** a sessão do Gerente é invalidada enquanto uma consulta está em andamento
- **THEN** a resposta antiga não repovoa o estado da nova sessão nem é apresentada na rota protegida

## MODIFIED Requirements

### Requirement: Reflex permite comentar chamado autorizado com rascunho descartável
O Reflex DEVE (MUST) oferecer ao Gerente autenticado envio de comentário para o contrato funcional específico e descarte exclusivamente local do rascunho. A interface NÃO DEVE (MUST NOT) enviar autor, Loja, visibilidade, timestamp ou status como dados sob controle do cliente.

#### Scenario: Envio de comentário público
- **WHEN** o Gerente envia conteúdo de comentário não vazio em chamado autorizado
- **THEN** o Reflex chama o contrato específico, apresenta o comentário retornado e atualiza a visualização sem inventar dados locais

#### Scenario: Descarte do rascunho
- **WHEN** o Gerente descarta comentário ainda não enviado
- **THEN** o Reflex limpa somente o conteúdo local sem executar requisição nem alterar o chamado

#### Scenario: Chamado terminal
- **WHEN** o detalhe informa status `Encerrado` ou `Cancelado`
- **THEN** o Reflex mantém os comentários públicos visíveis e oferece envio de comentário Público autorizado, sem permitir edição dos campos funcionais
