# Spec Delta

## MODIFIED Requirements

### Requirement: Filtros da lista são restritos ao escopo da Loja
A lista DEVE (MUST) aceitar somente filtros opcionais de número exato, status canônico, Totem pertencente à Loja autorizada, intervalo inclusivo de `criado_em` e intervalo inclusivo de `ultima_atualizacao_em`. Critério inválido, status não canônico ou Totem fora do escopo DEVE (MUST) resultar em erro funcional sem ampliar a consulta.

#### Scenario: Combinação de filtros
- **WHEN** o Gerente aplica mais de um filtro válido
- **THEN** o Xano retorna somente chamados da própria Loja que atendem simultaneamente aos critérios e informa o total filtrado

#### Scenario: Período inclusivo de abertura
- **WHEN** o Gerente informa início e fim válidos do período
- **THEN** a consulta inclui chamados abertos nos dois dias-limite e não filtra por `ultima_atualizacao_em`

#### Scenario: Período inclusivo de última atualização
- **WHEN** o Gerente informa início e fim válidos da última atualização
- **THEN** a consulta inclui somente chamados atualizados nos dois dias-limite, sem alterar o período de abertura

#### Scenario: Totem de outra Loja
- **WHEN** o Gerente informa identificador de Totem que não pertence à sua Loja
- **THEN** o Xano rejeita a consulta como não autorizada sem retornar chamados

## ADDED Requirements

### Requirement: Detalhe da Loja fornece resumo autorizado do Totem

O detalhe autorizado do chamado DEVE (MUST) retornar Loja, estado atual e última
telemetria opcional do Totem (CPU, memória, temperatura, rede e timestamp). O
resumo NÃO DEVE (MUST NOT) incluir histórico, transição, incidente, cálculo ou
causalidade.

#### Scenario: Resumo disponível
- **WHEN** o Gerente consulta chamado de sua Loja com telemetria disponível
- **THEN** a resposta inclui os valores reais do resumo do Totem

#### Scenario: Telemetria ausente
- **WHEN** o Totem não possui telemetria
- **THEN** a resposta retorna telemetria nula sem fabricar valor ou timestamp

#### Scenario: Outra Loja
- **WHEN** o Gerente consulta chamado de outra Loja
- **THEN** o Xano mantém a negação sem retornar resumo do Totem
