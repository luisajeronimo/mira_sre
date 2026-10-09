# Spec Delta

## MODIFIED Requirements

### Requirement: Última atualização representa alteração observável pelo Gerente
Todo chamado válido DEVE (MUST) possuir `criado_em` e `ultima_atualizacao_em`. Na criação manual ou automática, o Xano DEVE (MUST) definir ambos com o mesmo instante funcional, calculado uma única vez; `criado_em` permanece imutável. A atribuição efetiva, mudança de status e comentário público DEVEM (MUST) atualizar somente `ultima_atualizacao_em`; leitura e eventos internos não visíveis NÃO DEVEM (MUST NOT) atualizá-lo.

#### Scenario: Criação inicializa os timestamps funcionais
- **WHEN** um fluxo funcional cria chamado válido
- **THEN** `criado_em` e `ultima_atualizacao_em` recebem o mesmo instante funcional definido pelo Xano

#### Scenario: Criação inicializa a última atualização
- **WHEN** um fluxo funcional cria novo chamado válido
- **THEN** `ultima_atualizacao_em` recebe o mesmo instante funcional de `criado_em`

#### Scenario: Evento observável posterior
- **WHEN** atribuição efetiva, mudança de status ou comentário público ocorre
- **THEN** `criado_em` permanece imutável e o Xano atualiza `ultima_atualizacao_em` no mesmo ato

#### Scenario: Atribuição efetiva atualiza a data
- **WHEN** uma atribuição altera o Técnico responsável de um chamado
- **THEN** o Xano atualiza somente `ultima_atualizacao_em` no mesmo ato da alteração

#### Scenario: Mudança de status futura atualiza a data
- **WHEN** um fluxo funcional autorizado altera o status de um chamado
- **THEN** o Xano atualiza somente `ultima_atualizacao_em` no mesmo ato da alteração de status

#### Scenario: Evento interno não visível
- **WHEN** ocorre nota interna, work log, diagnóstico ou outra operação sem consequência visível ao Gerente
- **THEN** o evento não altera `ultima_atualizacao_em`

### Requirement: Dados legados permanecem sem última atualização inferida
O sistema NÃO DEVE (MUST NOT) fazer backfill ou derivar `criado_em` ou `ultima_atualizacao_em` de `created_at`, atribuição, interações ou outro timestamp aproximado. Registros históricos com ausência desses dados não são chamados válidos para a jornada operacional e não recebem compatibilidade de leitura nesta change.

#### Scenario: Registro histórico com timestamp ausente
- **WHEN** existe registro com `criado_em` ou `ultima_atualizacao_em` ausente
- **THEN** o sistema não altera o registro nem fabrica timestamp; a existência é somente reportada antes de qualquer ação de dados

#### Scenario: Chamado legado sem dado confiável
- **WHEN** um chamado histórico não possui `ultima_atualizacao_em`
- **THEN** a change não faz backfill nem substitui o valor por data técnica; esse registro não recebe compatibilidade temporal na jornada operacional

### Requirement: Detalhe autorizado expõe a última atualização funcional
O DTO de `GET /gerente/chamados/{chamados_id}` DEVE (MUST) retornar `criado_em` e `ultima_atualizacao_em` como timestamps funcionais obrigatórios do chamado válido autorizado, sem usar `created_at` ou timestamp inferido como fallback.

#### Scenario: Detalhe de chamado válido
- **WHEN** o Gerente autorizado consulta chamado válido
- **THEN** a resposta contém os dois timestamps funcionais definidos pelo Xano

#### Scenario: Detalhe de chamado legado
- **WHEN** o Gerente autorizado consulta chamado histórico com `ultima_atualizacao_em` ausente
- **THEN** o contrato não inventa timestamp nem usa `created_at` como fallback; o registro não é compatível com a jornada operacional desta change
