# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente acompanha todos os chamados da própria Loja
O sistema DEVE (MUST) fornecer `GET /gerente/chamados` e `GET /gerente/chamados/{chamados_id}` no grupo `mira-service-desk`. A lista DEVE (MUST) retornar `items` com resumo funcional e `total` correspondente à consulta atual; o detalhe DEVE (MUST) retornar um objeto `chamado` com os campos do contrato de criação. Ambos DEVEM (MUST) determinar pertencimento pela Loja histórica demonstrável no `criado_em` do chamado, independentemente de solicitante e origem; sem comprovação, o acesso do Gerente falha fechado.

#### Scenario: Lista da Loja
- **WHEN** um Gerente autenticado consulta a lista de chamados
- **THEN** o Xano retorna todos os chamados comprovadamente abertos na sua Loja, incluindo chamados de outros solicitantes e automáticos, sem retornar chamados de outras Lojas ou de vínculo indeterminado

#### Scenario: Detalhe da própria Loja
- **WHEN** um Gerente consulta o identificador de um chamado comprovadamente aberto em sua Loja
- **THEN** o Xano retorna o detalhe funcional do chamado

#### Scenario: Detalhe de outra Loja
- **WHEN** um Gerente consulta o identificador de um chamado comprovadamente aberto em outra Loja
- **THEN** o Xano rejeita a operação como não autorizada sem retornar os dados do chamado

#### Scenario: Chamado inexistente
- **WHEN** um Gerente consulta um identificador de chamado que não existe
- **THEN** o Xano responde como recurso não encontrado

#### Scenario: Loja histórica indeterminada
- **WHEN** o chamado legado não possui vínculo de Loja demonstrável em `criado_em`
- **THEN** o Xano não o atribui à Loja atual do Totem nem o expõe ao Gerente

### Requirement: Filtros da lista são restritos ao escopo da Loja
A lista DEVE (MUST) aceitar somente filtros opcionais de número exato, status canônico, Totem com chamado comprovadamente aberto na Loja autorizada, intervalo inclusivo de `criado_em` e intervalo inclusivo de `ultima_atualizacao_em`. Critério inválido, status não canônico ou Totem sem chamado nesse escopo DEVE (MUST) resultar em erro funcional sem ampliar a consulta.

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
- **WHEN** o Gerente informa identificador de Totem sem chamado historicamente autorizado em sua Loja
- **THEN** o Xano rejeita a consulta como não autorizada sem retornar chamados

#### Scenario: Totem transferido da Loja
- **WHEN** Totem transferido possui chamado comprovadamente aberto na Loja do Gerente antes da transferência
- **THEN** o filtro por esse Totem pode retornar o chamado antigo da Loja sem expor chamados posteriores da Loja de destino

### Requirement: Detalhe da Loja fornece resumo autorizado do Totem

O detalhe autorizado do chamado DEVE (MUST) retornar a Loja histórica demonstrável da abertura, o estado atual e a última telemetria opcional do Totem (CPU, memória, temperatura, rede e timestamp). O resumo NÃO DEVE (MUST NOT) incluir histórico, transição, incidente, cálculo ou causalidade; a Loja atual do Totem NÃO DEVE (MUST NOT) substituir a Loja histórica do chamado.

#### Scenario: Resumo disponível
- **WHEN** o Gerente consulta chamado comprovadamente aberto em sua Loja com telemetria disponível
- **THEN** a resposta inclui a Loja da abertura e os valores reais do resumo atual do Totem

#### Scenario: Telemetria ausente
- **WHEN** o Totem não possui telemetria
- **THEN** a resposta retorna telemetria nula sem fabricar valor ou timestamp

#### Scenario: Outra Loja
- **WHEN** o Gerente consulta chamado comprovadamente aberto em outra Loja
- **THEN** o Xano mantém a negação sem retornar resumo do Totem

## ADDED Requirements

### Requirement: Administrador inicia abertura manual no Início
O Reflex DEVE (MUST) oferecer ao Administrador, em `/inicio`, a ação de abrir chamado com a mesma apresentação e posição do botão usado pelo Gerente, além da mesma composição de formulário em `/chamados/novo`. O Gerente DEVE (MUST) conservar seu fluxo e escopo de Loja; o Administrador DEVE (MUST) escolher Totem globalmente. A apresentação compartilhada NÃO DEVE (MUST NOT) deslocar autorização ou regras de negócio do Xano para o Reflex. A gestão administrativa NÃO DEVE (MUST NOT) apresentar o formulário de chamado.

#### Scenario: Administrador parte do Início
- **WHEN** Administrador autenticado aciona Criar chamado em `/inicio`
- **THEN** abre o formulário compartilhado em `/chamados/novo`, com Totens globais elegíveis

#### Scenario: Gerente conserva a abertura
- **WHEN** Gerente autenticado aciona Criar chamado em `/inicio`
- **THEN** abre o mesmo formulário visual com Totens limitados pela própria Loja no Xano

#### Scenario: Perfil sem permissão de abertura
- **WHEN** Técnico ou Diretoria tenta abrir `/chamados/novo`
- **THEN** o Reflex não apresenta o formulário e o Xano não recebe mutação

### Requirement: Administrador pode abrir chamado manual para qualquer Totem
A abertura manual DEVE (MUST) aceitar Administrador autenticado em escopo global com os mesmos campos e validações funcionais do Gerente. O solicitante DEVE (MUST) ser o Administrador autenticado, e a Loja DEVE (MUST) corresponder ao vínculo do Totem no momento da abertura.

#### Scenario: Abertura global válida
- **WHEN** Administrador informa título, descrição, Totem, Categoria elegível e prioridade válidos
- **THEN** o Xano cria chamado manual com solicitante Administrador e Loja do Totem na abertura

#### Scenario: Tentativa de Loja diferente
- **WHEN** cliente tenta associar chamado manual a Loja diferente da Loja do Totem
- **THEN** o Xano rejeita ou desconsidera o dado forjado sem criar vínculo incorreto

### Requirement: Chamado preserva sua Loja histórica após transferência de Totem
Um chamado com Loja de abertura demonstrável DEVE (MUST) continuar atribuído a ela após transferência do Totem. A transferência NÃO DEVE (MUST NOT) reescrever o chamado nem atribuir fato legado sem evidência à Loja atual do Totem. O instante funcional do chamado é `criado_em`.

#### Scenario: Transferência após abertura
- **WHEN** Totem é transferido depois da criação de chamado cuja Loja de abertura é demonstrável
- **THEN** o chamado permanece associado à Loja da criação e chamadas futuras usam a nova Loja

#### Scenario: Chamado sem Loja histórica comprovável
- **WHEN** chamado legado não possui vínculo de Loja demonstrável em `criado_em`
- **THEN** sua Loja histórica permanece indeterminada, sem usar o vínculo atual como substituto

#### Scenario: Loja Inativa na abertura
- **WHEN** Totem já vinculado a Loja `Inativa` recebe abertura manual elegível por perfil autorizado
- **THEN** a situação cadastral da Loja não bloqueia o chamado nem altera suas validações existentes
