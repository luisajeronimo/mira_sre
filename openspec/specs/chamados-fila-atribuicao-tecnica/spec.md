# chamados-fila-atribuicao-tecnica Specification

## Purpose

Definir a fila técnica mínima do MIRA, permitindo que Técnicos consultem chamados elegíveis, vejam os chamados não atribuídos ou atribuídos a si e assumam um chamado com a proteção de concorrência best-effort disponível no plano Free, sem iniciar ainda a tratativa completa.

## Requirements

### Requirement: Fila técnica oferece somente as visões aprovadas
O sistema DEVE (MUST) fornecer no grupo `MIRA Service Desk` uma consulta autenticada exclusiva do perfil `tecnico`, usando `GET /tecnico/chamados?visao=nao_atribuidos` e `GET /tecnico/chamados?visao=atribuidos_a_mim`. O filtro DEVE (MUST) ser aplicado no Xano e a visão DEVE (MUST) aceitar somente esses dois valores.

#### Scenario: Visão de chamados não atribuídos
- **WHEN** um Técnico autenticado consulta `visao=nao_atribuidos`
- **THEN** o Xano retorna somente chamados com `status = "Novo"` e Técnico ausente (`tecnico_id = null` ou `tecnico_id = 0` na representação legada), ordenados por `id` decrescente

#### Scenario: Visão de chamados atribuídos a mim
- **WHEN** um Técnico autenticado consulta `visao=atribuidos_a_mim`
- **THEN** o Xano retorna somente chamados com `status = "Novo"` e `tecnico_id` igual ao identificador do Técnico autenticado, ordenados por `id` decrescente

#### Scenario: Chamado atribuído a outro Técnico
- **WHEN** um chamado tem `status = "Novo"` e `tecnico_id` preenchido com outro Técnico
- **THEN** ele não aparece em nenhuma das duas visões principais desta capacidade

#### Scenario: Status nulo ou inelegível
- **WHEN** um chamado possui `status = null` ou status diferente de `Novo`
- **THEN** ele não aparece na fila e não é tornado elegível por inferência

#### Scenario: Visão inválida
- **WHEN** uma requisição informa `visao` diferente de `nao_atribuidos` ou `atribuidos_a_mim`
- **THEN** o Xano responde HTTP 422 sem consultar uma visão implícita ou retornar dados

#### Scenario: Ordenação e ausência de paginação
- **WHEN** qualquer uma das visões retorna chamados
- **THEN** os itens são ordenados somente por `id desc` e a resposta não introduz ordenação por prioridade, SLA ou paginação nesta capacidade

### Requirement: Listagem técnica retorna DTO funcional estável
O sistema DEVE (MUST) retornar em cada item da fila `id`, `titulo`, `status`, `prioridade`, `origem`, `criado_em`, `sla_horas_aplicado`, `atribuido_em`, ativo, categoria, solicitante e técnico atual quando existir. Valores nulos de registros legados DEVEM (MUST) permanecer nulos, sem backfill ou inferência.

#### Scenario: Chamado manual na fila
- **WHEN** um chamado manual elegível é retornado
- **THEN** a resposta preserva sua origem manual, prioridade, abertura, snapshot de SLA, ativo, categoria e técnico atual

#### Scenario: Chamado automático na fila
- **WHEN** um chamado automático elegível é retornado
- **THEN** a resposta preserva sua origem automática e os demais dados já persistidos, sem alterar a regra do heartbeat

#### Scenario: Chamado legado na consulta
- **WHEN** um chamado legado elegível possui origem, SLA, abertura ou atribuição ausentes
- **THEN** a resposta representa esses campos como nulos e não fabrica valores históricos

### Requirement: Técnico pode consultar detalhe global somente leitura
O sistema DEVE (MUST) fornecer `GET /tecnico/chamados/{chamados_id}` para o perfil `tecnico`, com escopo global de consulta já consolidado. O detalhe DEVE (MUST) reutilizar o formato funcional consolidado quando possível, incluir `atribuido_em` e NÃO DEVE (MUST NOT) oferecer mutação de status, edição, reatribuição, liberação ou tratativa.

#### Scenario: Detalhe antes da assunção
- **WHEN** um Técnico consulta um chamado elegível ainda não atribuído
- **THEN** o Xano retorna o detalhe funcional com técnico e `atribuido_em` nulos, quando aplicável

#### Scenario: Detalhe depois da assunção
- **WHEN** um Técnico consulta um chamado atribuído
- **THEN** o Xano retorna o técnico responsável e o `atribuido_em` persistido sem permitir alteração pelo contrato de consulta

#### Scenario: Chamado inexistente
- **WHEN** o Técnico consulta identificador inexistente
- **THEN** o Xano responde HTTP 404

#### Scenario: Dados protegidos por rota indevida
- **WHEN** um consumidor tenta usar a jornada técnica sem ser Técnico
- **THEN** o Xano não retorna o detalhe e responde HTTP 403

### Requirement: Schema registra a atribuição sem backfill
O sistema DEVE (MUST) adicionar `atribuido_em` como timestamp opcional em `chamados`. O valor DEVE (MUST) ser definido somente pelo Xano quando uma assunção for efetivada, e registros existentes DEVEM (MUST) permanecer com `atribuido_em = null` sem limpeza ou preenchimento retroativo.

#### Scenario: Assunção grava timestamp do backend
- **WHEN** uma assunção válida efetiva a atribuição
- **THEN** o Xano grava `atribuido_em` usando o timestamp do backend

#### Scenario: Cliente tenta informar timestamp
- **WHEN** o cliente envia `atribuido_em` na requisição de assunção ou em campos adicionais
- **THEN** o valor do cliente não possui autoridade e não substitui o timestamp definido pelo Xano

#### Scenario: Registro legado
- **WHEN** a evolução do schema encontra um chamado existente
- **THEN** o registro é preservado e `atribuido_em` permanece nulo

### Requirement: Assunção é autoatribuição idempotente com consistência best-effort no plano Free
O sistema DEVE (MUST) fornecer `POST /tecnico/chamados/{chamados_id}/assumir` sem aceitar `tecnico_id`, `status` ou `atribuido_em` no payload. O Xano DEVE (MUST) derivar o Técnico por `$auth.id`, manter `status = "Novo"`, validar a ausência de Técnico antes da edição, reler o registro após a edição e responder HTTP 409 quando observar atribuição por outro Técnico. O contrato NÃO DEVE (MUST NOT) afirmar compare-and-set, isolamento forte ou garantia matemática de um único vencedor em duas escritas exatamente simultâneas no plano Free.

#### Scenario: Assunção válida
- **WHEN** um Técnico autenticado assume chamado com `status = "Novo"` e Técnico ausente (`tecnico_id = null` ou `tecnico_id = 0` na representação legada)
- **THEN** o Xano define `tecnico_id` como o usuário autenticado, define `atribuido_em` pelo backend, mantém `status = "Novo"` e retorna o DTO atualizado com sucesso

#### Scenario: Repetição pelo mesmo Técnico
- **WHEN** o mesmo Técnico repete a assunção de chamado já atribuído a ele
