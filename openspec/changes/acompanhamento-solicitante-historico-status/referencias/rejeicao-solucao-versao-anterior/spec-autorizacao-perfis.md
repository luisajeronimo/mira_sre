# Spec Delta

## ADDED Requirements

### Requirement: Rejeição de solução é autorizada pela Loja do Gerente ou pelo vínculo de solicitante
O Xano DEVE (MUST) autorizar a rejeição de solução somente quando, pela identidade autenticada, ocorrer ao menos uma das condições: o usuário é Gerente com Loja associada igual à Loja do Totem do chamado; ou o usuário é o solicitante humano associado ao chamado. A condição do solicitante NÃO DEVE (MUST NOT) depender da Loja atual ou do perfil atual do usuário, e o vínculo de solicitante NÃO DEVE (MUST NOT) conceder acesso a outros chamados. A autorização DEVE (MUST) ser reavaliada dentro da unidade de escrita da rejeição, com os dados atuais do chamado e a identidade autenticada. A visibilidade do item "Chamados solicitados" no menu NÃO DEVE (MUST NOT) conceder autorização. Técnico, Diretoria e Administrador NÃO DEVEM (MUST NOT) receber essa permissão por perfil. Identificador, Loja ou perfil enviados pelo cliente e a visibilidade da ação no Reflex NÃO DEVEM (MUST NOT) conceder autorização. A permissão de rejeitar NÃO DEVE (MUST NOT) conceder ao Gerente tratativa, Save operacional, atribuição, comentário interno ou acesso à fila e ao detalhe técnicos.

#### Scenario: Gerente da Loja não solicitante
- **WHEN** um Gerente rejeita chamado da própria Loja cujo solicitante é outro usuário
- **THEN** o Xano autoriza a operação

#### Scenario: Gerente de outra Loja
- **WHEN** um Gerente tenta rejeitar chamado ligado a Totem de outra Loja e não é seu solicitante
- **THEN** o Xano nega a operação sem retornar nem alterar dados

#### Scenario: Gerente sem Loja
- **WHEN** um Gerente sem Loja associada tenta rejeitar chamado do qual não é solicitante
- **THEN** o Xano nega a operação

#### Scenario: Gerente da Loja proprietária
- **WHEN** um Gerente rejeita chamado ligado a Totem da Loja à qual está associado
- **THEN** o Xano autoriza a operação, sendo ele solicitante ou não

#### Scenario: Solicitante associado
- **WHEN** o usuário autenticado é o solicitante humano associado ao chamado
- **THEN** o Xano autoriza a operação

#### Scenario: Solicitante transferido de Loja
- **WHEN** o solicitante associado hoje pertence a outra Loja que não a do Totem do chamado
- **THEN** o Xano autoriza a rejeição pelo vínculo, sem considerar a Loja atual

#### Scenario: Vínculo não se estende a outros chamados
- **WHEN** esse solicitante transferido tenta rejeitar outro chamado da Loja antiga do qual não é solicitante
- **THEN** o Xano nega a operação

#### Scenario: Revalidação dentro da unidade de escrita
- **WHEN** a releitura do chamado ou da identidade dentro da unidade de escrita deixa de atender às condições de autorização
- **THEN** o Xano nega a operação sem executar escrita, mesmo que a validação anterior tenha sido aceita

#### Scenario: Usuário não associado
- **WHEN** o usuário não é Gerente da Loja do chamado nem seu solicitante
- **THEN** o Xano nega a operação

#### Scenario: Perfil operacional
- **WHEN** Técnico, Diretoria ou Administrador que não é o solicitante tenta usar a operação de rejeição
- **THEN** o Xano nega a operação

#### Scenario: Chamado automático sem solicitante
- **WHEN** o chamado não possui solicitante humano
- **THEN** somente o Gerente da Loja pode ser autorizado; nenhum vínculo é presumido para o Bot de Fiscalização

## MODIFIED Requirements

### Requirement: CRUDs genéricos não ampliam permissões
O sistema NÃO DEVE (MUST NOT) permitir que endpoints CRUD genéricos contornem as regras de autorização ou concedam operações administrativas e destrutivas não previstas para os perfis oficiais. A criação de usuário administrativo DEVE permanecer no contrato funcional específico autorizado apenas a Administrador. As consultas genéricas de `interacoes_chamado`, por lista ou por identificador, NÃO DEVEM (MUST NOT) atender o Gerente; o Gerente lê interações exclusivamente pelos contratos funcionais de comentários públicos e histórico público.

#### Scenario: Acesso direto a mutação genérica
- **WHEN** um usuário autenticado chama diretamente um endpoint genérico de criação, alteração ou exclusão sem permissão funcional correspondente
- **THEN** o Xano rejeita a operação sem modificar os dados

#### Scenario: Consulta genérica fora do escopo
- **WHEN** uma consulta genérica poderia retornar dados além do escopo autorizado ao usuário
- **THEN** o Xano aplica o filtro de escopo no backend ou rejeita a consulta sem expor esses dados

#### Scenario: Gerente lista interações pelo CRUD genérico
- **WHEN** um Gerente autenticado chama `GET /interacoes_chamado`
- **THEN** o Xano responde como não autorizado sem retornar interações públicas, internas ou eventos de auditoria

#### Scenario: Gerente consulta interação por identificador no CRUD genérico
- **WHEN** um Gerente autenticado chama `GET /interacoes_chamado/{interacoes_chamado_id}` para interação de chamado da própria Loja, pública ou interna
- **THEN** o Xano responde como não autorizado sem retornar a interação

#### Scenario: Demais perfis preservados
- **WHEN** um perfil hoje autorizado nas consultas genéricas de `interacoes_chamado` as utiliza
- **THEN** o comportamento permanece o mesmo vigente antes desta change
