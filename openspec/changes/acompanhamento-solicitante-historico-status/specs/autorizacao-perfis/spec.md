# Spec Delta

## ADDED Requirements

### Requirement: Consulta do solicitante é autorizada pelo vínculo com o chamado
O Xano DEVE (MUST) autorizar os contratos de consulta do solicitante somente quando ocorrerem cumulativamente: autenticação válida de `usuarios`; troca obrigatória de senha não pendente; perfil oficial Gerente, Técnico, Diretoria ou Administrador; `chamados.solicitante_id` não nulo; e `chamados.solicitante_id` igual à identidade autenticada. A autorização NÃO DEVE (MUST NOT) depender da Loja atual do usuário, e o vínculo NÃO DEVE (MUST NOT) conceder acesso a outros chamados, inclusive aos da Loja anterior do usuário. Chamado inexistente e chamado não associado ao usuário DEVEM (MUST) receber a mesma resposta de recurso não encontrado, sem revelar a existência do chamado. A visibilidade do item "Chamados solicitados" no menu e identificadores, Loja ou perfil enviados pelo cliente NÃO DEVEM (MUST NOT) conceder autorização. Esses contratos são somente leitura e NÃO DEVEM (MUST NOT) conceder comentário, rejeição de solução, Save, atribuição ou acesso à fila e ao detalhe técnicos.

#### Scenario: Solicitante associado
- **WHEN** um usuário com perfil oficial consulta chamado do qual é o solicitante
- **THEN** o Xano autoriza a consulta

#### Scenario: Solicitante de outra Loja
- **WHEN** o solicitante pertence hoje a Loja diferente da Loja do Totem do chamado
- **THEN** o Xano autoriza a consulta pelo vínculo, sem considerar a Loja atual

#### Scenario: Perfil global como solicitante
- **WHEN** Técnico, Diretoria ou Administrador consulta pelo contrato do solicitante chamado do qual é o solicitante
- **THEN** o Xano autoriza a consulta somente desse chamado

#### Scenario: Chamado de outra pessoa
- **WHEN** um usuário com perfil oficial consulta pelo contrato do solicitante chamado cujo solicitante é outro usuário, inclusive da mesma Loja ou da Loja anterior do usuário
- **THEN** o Xano responde como recurso não encontrado, sem retornar dados

#### Scenario: Chamado inexistente
- **WHEN** o identificador não corresponde a chamado existente
- **THEN** o Xano responde com a mesma resposta de recurso não encontrado dada a chamado de outra pessoa

#### Scenario: Chamado sem solicitante humano
- **WHEN** o chamado possui `solicitante_id` nulo
- **THEN** nenhum usuário é autorizado pelo contrato do solicitante e a resposta é de recurso não encontrado

#### Scenario: Perfil não oficial
- **WHEN** um usuário autenticado sem perfil oficial usa o contrato do solicitante, ainda que seja o solicitante do chamado
- **THEN** o Xano responde como não autorizado sem consultar chamados

#### Scenario: Troca de senha pendente
- **WHEN** um usuário com troca obrigatória pendente usa o contrato do solicitante
- **THEN** o Xano responde como não autorizado sem consultar chamados

#### Scenario: Identificador inválido
- **WHEN** o identificador do chamado é ausente, não numérico ou menor que 1
- **THEN** o Xano rejeita a entrada antes de qualquer consulta

## MODIFIED Requirements

### Requirement: CRUDs genéricos não ampliam permissões
O sistema NÃO DEVE (MUST NOT) permitir que endpoints CRUD genéricos contornem as regras de autorização ou concedam operações administrativas e destrutivas não previstas para os perfis oficiais. A criação de usuário administrativo DEVE permanecer no contrato funcional específico autorizado apenas a Administrador. As consultas genéricas de `interacoes_chamado`, por lista ou por identificador, NÃO DEVEM (MUST NOT) atender o Gerente e DEVEM (MUST) negá-lo antes de ler qualquer interação; o Gerente lê interações exclusivamente pelos contratos funcionais de comentários públicos e de histórico público de status. Os demais perfis mantêm o comportamento vigente dessas consultas.

#### Scenario: Acesso direto a mutação genérica
- **WHEN** um usuário autenticado chama diretamente um endpoint genérico de criação, alteração ou exclusão sem permissão funcional correspondente
- **THEN** o Xano rejeita a operação sem modificar os dados

#### Scenario: Consulta genérica fora do escopo
- **WHEN** uma consulta genérica poderia retornar dados além do escopo autorizado ao usuário
- **THEN** o Xano aplica o filtro de escopo no backend ou rejeita a consulta sem expor esses dados

#### Scenario: Gerente lista interações pelo CRUD genérico
- **WHEN** um Gerente autenticado chama `GET /interacoes_chamado`
- **THEN** o Xano responde como não autorizado sem retornar comentários públicos, comentários internos ou eventos operacionais

#### Scenario: Gerente consulta interação por identificador no CRUD genérico
- **WHEN** um Gerente autenticado chama `GET /interacoes_chamado/{interacoes_chamado_id}` para interação de chamado da própria Loja, comentário público, comentário interno, evento operacional ou identificador inexistente
- **THEN** o Xano responde como não autorizado sem ler nem retornar a interação

#### Scenario: Demais perfis preservados
- **WHEN** Técnico, Diretoria ou Administrador utiliza as consultas genéricas de `interacoes_chamado`
- **THEN** o resultado permanece o mesmo vigente antes desta change
