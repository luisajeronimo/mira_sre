# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente pode consultar o detalhe básico do chamado
O sistema DEVE (MUST) fornecer uma página de detalhe que consulte `GET /gerente/chamados/{chamados_id}` e apresente identificação, título, descrição, status, prioridade, origem, abertura, última atualização, SLA aplicado, ativo, categoria, solicitante e técnico quando houver. A página DEVE (MUST) consultar e apresentar separadamente os comentários públicos autorizados do chamado, sem oferecer edição do chamado, mudança de status, atribuição, diagnóstico, solução ou resolução nesta capacidade.

#### Scenario: Detalhe carregado
- **WHEN** o Xano retorna um chamado autorizado da Loja
- **THEN** o Reflex apresenta seus dados funcionais, incluindo ativo, categoria, solicitante, técnico quando houver e última atualização, sem usar `created_at` como abertura

#### Scenario: Última atualização legada não informada
- **WHEN** o detalhe retorna `ultima_atualizacao_em` nulo
- **THEN** o Reflex apresenta `Não informado`, sem substituir o valor por `created_at` ou outra data aproximada

#### Scenario: Técnico ainda não atribuído
- **WHEN** o detalhe retorna técnico nulo
- **THEN** o Reflex apresenta a ausência de atribuição sem oferecer ação para atribuir ou assumir

#### Scenario: Comentários públicos carregados
- **WHEN** a consulta de comentários públicos do chamado é aceita
- **THEN** o Reflex apresenta somente os comentários retornados, do mais recente ao mais antigo

## ADDED Requirements

### Requirement: Reflex permite comentar chamado autorizado com rascunho descartável
O Reflex DEVE (MUST) oferecer ao Gerente autenticado envio de comentário para o contrato funcional específico e descarte exclusivamente local do rascunho. A interface NÃO DEVE (MUST NOT) enviar autor, Loja, visibilidade, timestamp ou status como dados sob controle do cliente.

#### Scenario: Envio de comentário público
- **WHEN** o Gerente envia conteúdo de comentário não vazio em chamado não terminal autorizado
- **THEN** o Reflex chama o contrato específico, apresenta o comentário retornado e atualiza a visualização sem inventar dados locais

#### Scenario: Descarte do rascunho
- **WHEN** o Gerente descarta comentário ainda não enviado
- **THEN** o Reflex limpa somente o conteúdo local sem executar requisição nem alterar o chamado

#### Scenario: Chamado terminal
- **WHEN** o detalhe informa status `Encerrado` ou `Cancelado`
- **THEN** o Reflex mantém os comentários públicos visíveis e não oferece envio de novo comentário
