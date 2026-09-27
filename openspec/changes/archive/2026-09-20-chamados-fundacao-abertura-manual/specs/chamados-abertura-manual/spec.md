## Purpose

Definir a fundação persistida e os contratos funcionais pelos quais o Gerente abre um chamado manual e acompanha todos os chamados vinculados aos ativos de sua Loja, preservando a compatibilidade do criador automático existente.

## ADDED Requirements

### Requirement: Novos chamados preservam origem, abertura e SLA aplicado
O sistema DEVE (MUST) persistir em cada chamado criado pelos fluxos funcionais novos a origem canônica, `criado_em` como único timestamp de negócio da abertura e `sla_horas_aplicado` como snapshot numérico do `sla_horas` vigente na categoria no instante da criação. `created_at` PODE (MAY) continuar existindo como metadado técnico, mas NÃO DEVE (MUST NOT) ser tratado como uma segunda referência funcional de abertura.

#### Scenario: Fundação preenchida em chamado manual
- **WHEN** o Xano cria um chamado por uma submissão manual válida
- **THEN** o registro recebe `origem = "manual"`, `criado_em` definido pelo backend no instante da criação e `sla_horas_aplicado` igual ao valor numérico vigente da categoria

#### Scenario: Fundação preenchida em chamado automático
- **WHEN** o heartbeat cria um novo chamado pela regra automática existente
- **THEN** o registro recebe `origem = "automatico"`, `criado_em` definido pelo backend no instante da criação e `sla_horas_aplicado` igual ao valor numérico vigente da categoria do heartbeat

#### Scenario: Valores de criação enviados pelo cliente
- **WHEN** um consumidor tenta informar ou substituir `origem`, `criado_em`, `created_at`, `sla_horas_aplicado`, `solicitante_id`, `tecnico_id`, `lojas_id` ou `status` na abertura manual
- **THEN** esses valores não são usados como autoridade para a criação e o Xano aplica exclusivamente os valores derivados pelo contrato funcional

### Requirement: Evolução do schema preserva dados legados sem inferência
O sistema DEVE (MUST) adicionar `descricao`, `origem` e `sla_horas_aplicado` de forma fisicamente compatível com chamados existentes e manter `criado_em` compatível com valores ausentes. Os valores novos DEVEM (MUST) ser obrigatórios nos fluxos definidos por esta capacidade, mas registros anteriores NÃO DEVEM (MUST NOT) receber origem, descrição, timestamp de negócio ou SLA histórico inferidos de categoria, título, usuário, `created_at` ou qualquer outra heurística.

#### Scenario: Chamado legado sem os novos dados
- **WHEN** a evolução do schema encontra um chamado existente sem origem, descrição, `criado_em` ou snapshot de SLA
- **THEN** o registro permanece armazenado com esses valores ausentes e nenhum dado histórico é fabricado

#### Scenario: Consulta de chamado legado atribuível a uma Loja
- **WHEN** um chamado legado possui relação válida com um ativo da Loja do Gerente, mas algum dado novo está ausente
- **THEN** o contrato de consulta pode retorná-lo com o valor correspondente nulo, sem substituí-lo por uma inferência

#### Scenario: Chamado legado sem ativo válido
- **WHEN** um chamado legado não possui relação válida com um ativo e, por isso, não pode ser atribuído com segurança à Loja do Gerente
- **THEN** ele não é exposto nos contratos da Loja e permanece armazenado para tratamento posterior explícito

### Requirement: Categorias declaram permissão de abertura manual
O sistema DEVE (MUST) persistir em cada categoria a propriedade booleana `permite_abertura_manual`. Somente categorias com valor explícito `true` e com `sla_horas` numérico válido PODEM (MAY) ser usadas pelo contrato de abertura manual; categorias legadas sem classificação explícita DEVEM (MUST) permanecer indisponíveis para essa abertura, e a categoria usada pelo heartbeat DEVE (MUST) possuir valor `false`. A classificação das categorias existentes DEVE (MUST) ocorrer por identificador mediante decisão humana explícita, sem seleção automática por nome, descrição, tipo ou qualquer outra inferência.

#### Scenario: Categoria permitida
- **WHEN** uma categoria possui `permite_abertura_manual = true` e um `sla_horas` numérico válido
- **THEN** ela é disponibilizada ao Gerente e pode classificar um novo chamado manual

#### Scenario: Categoria não permitida
- **WHEN** uma categoria possui `permite_abertura_manual = false`
- **THEN** ela não é retornada no catálogo de abertura manual e é rejeitada se seu identificador for enviado diretamente

#### Scenario: Categoria legada sem classificação
- **WHEN** a migração encontra uma categoria existente sem decisão explícita sobre abertura manual
- **THEN** a categoria permanece com `permite_abertura_manual = false` e não é classificada por nome, descrição ou tipo ITIL

#### Scenario: Gate humano de classificação das categorias existentes
- **WHEN** o inventário das categorias existentes apresenta identificador, nome, tipo atual, SLA atual, vínculo com o heartbeat e valor atual ou proposto de `permite_abertura_manual`
- **THEN** a implementação aguarda decisão humana explícita sobre os identificadores que receberão `true` e não altera os dados remotos antes dessa aprovação

#### Scenario: Categoria do heartbeat
- **WHEN** a categoria já utilizada pela criação automática é preparada para o schema evoluído
- **THEN** ela recebe explicitamente `permite_abertura_manual = false` sem alterar a forma como o heartbeat a localiza

### Requirement: SLA da categoria possui representação numérica segura
O sistema DEVE (MUST) representar `categorias_servico.sla_horas` e `chamados.sla_horas_aplicado` em formato numérico compatível entre si. Antes da mudança de tipo, a implementação DEVE (MUST) identificar e verificar todos os consumidores existentes de `categorias_servico.sla_horas`, incluindo XanoScript, Python e demais contratos locais relevantes, e definir a adaptação ou a evidência de compatibilidade de cada consumidor. A migração somente DEVE (MUST) converter valores textuais existentes cuja equivalência numérica seja inequívoca e DEVE (MUST) interromper a ativação dos novos contratos diante de consumidor incompatível ou de valor vazio, não numérico ou ambíguo em categoria que precise participar de um novo fluxo.

#### Scenario: Consumidores do SLA auditados antes da mudança de tipo
- **WHEN** a implementação prepara a alteração de `categorias_servico.sla_horas` de texto para decimal
- **THEN** todos os usos existentes em XanoScript, Python e contratos locais relevantes estão inventariados, classificados quanto à compatibilidade e cobertos por adaptação ou verificação antes de a alteração ser aplicada

#### Scenario: Consumidor incompatível identificado
- **WHEN** a auditoria encontra um consumidor que depende da representação textual e ainda não possui adaptação validada
- **THEN** a mudança de tipo permanece bloqueada sem alterar dados ou contratos remotos

#### Scenario: Valor textual inequivocamente numérico
- **WHEN** uma categoria existente possui `sla_horas` textual cuja conversão preserva exatamente seu valor numérico
- **THEN** a migração converte o valor para a representação numérica aprovada sem atribuir outro SLA

#### Scenario: Valor incompatível
- **WHEN** a auditoria encontra `sla_horas` vazio, não numérico ou ambíguo em uma categoria que será usada na abertura manual ou pelo heartbeat
- **THEN** a migração ou ativação é interrompida para correção explícita, sem escolher um SLA padrão

#### Scenario: Alteração posterior da categoria
- **WHEN** o `sla_horas` de uma categoria é alterado depois da criação de um chamado
- **THEN** o `sla_horas_aplicado` já persistido no chamado permanece inalterado

### Requirement: Grupo funcional fornece catálogo de ativos da Loja
O sistema DEVE (MUST) fornecer no grupo `mira-service-desk` uma consulta autenticada de ativos para o Gerente que retorne somente os ativos cuja `lojas_id` corresponda à Loja derivada da identidade autenticada. A resposta DEVE (MUST) conter uma coleção de itens com `id`, `nome_ativo`, `tipo` e `status_atual`.

#### Scenario: Gerente consulta ativos permitidos
- **WHEN** um Gerente autenticado e associado a uma Loja consulta `GET /gerente/ativos`
- **THEN** o Xano retorna `items` contendo somente os ativos dessa Loja e os campos públicos previstos pelo contrato

#### Scenario: Gerente sem Loja
- **WHEN** um Gerente autenticado sem associação válida de Loja consulta o catálogo de ativos
- **THEN** o Xano rejeita a operação como não autorizada sem retornar ativos

#### Scenario: Outro perfil consulta o catálogo do Gerente
- **WHEN** um Técnico ou usuário da Diretoria consulta `GET /gerente/ativos`
- **THEN** o Xano rejeita a operação como não autorizada

### Requirement: Grupo funcional fornece categorias de abertura manual
O sistema DEVE (MUST) fornecer no grupo `mira-service-desk` uma consulta autenticada para o Gerente que filtre categorias exclusivamente por `permite_abertura_manual = true`. A resposta DEVE (MUST) conter `items` com `id`, `nome`, `tipo_itil`, `descricao` e `sla_horas`, sem usar nome, descrição ou tipo ITIL como critério implícito de permissão.

#### Scenario: Consulta de categorias manuais
- **WHEN** um Gerente autenticado consulta `GET /gerente/categorias`
- **THEN** o Xano retorna somente categorias explicitamente permitidas para abertura manual

#### Scenario: Categoria automática não é oferecida
- **WHEN** a categoria do heartbeat possui `permite_abertura_manual = false`
- **THEN** ela não aparece na resposta do catálogo manual

### Requirement: Gerente pode abrir chamado manual da própria Loja
O sistema DEVE (MUST) aceitar em `POST /gerente/chamados` somente `ativos_referencia_id`, `categorias_servico_id`, `prioridade`, `titulo` e `descricao` como dados funcionais fornecidos pelo Gerente. Todos os cinco valores DEVEM (MUST) estar presentes; `titulo` e `descricao` DEVEM (MUST) ser rejeitados quando ausentes, vazios ou compostos somente por espaços após remoção de espaços nas extremidades. Esta capacidade NÃO DEVE (MUST NOT) introduzir limite mínimo ou máximo de caracteres para esses campos.

#### Scenario: Abertura manual válida
- **WHEN** um Gerente autenticado envia ativo de sua Loja, categoria permitida, uma prioridade oficial, título e descrição válidos
- **THEN** o Xano cria um novo chamado com `status = "Novo"`, `origem = "manual"`, solicitante igual ao usuário autenticado e os dados de abertura e SLA definidos pelo backend

#### Scenario: Prioridade oficial
- **WHEN** o Gerente informa `Baixa`, `Média`, `Alta` ou `Urgente`
- **THEN** o Xano preserva exatamente o valor escolhido no novo chamado sem derivá-lo da categoria ou de outra matriz

#### Scenario: Prioridade fora do vocabulário
- **WHEN** o Gerente informa uma prioridade diferente de `Baixa`, `Média`, `Alta` ou `Urgente`
- **THEN** o Xano rejeita a submissão como contrato inválido sem criar chamado

#### Scenario: Campo obrigatório ausente, vazio ou composto somente por espaços
- **WHEN** ativo, categoria, prioridade, título ou descrição está ausente, ou `titulo` ou `descricao` está vazio ou fica vazio após remoção de espaços nas extremidades
- **THEN** o Xano rejeita a submissão como contrato inválido sem criar chamado

#### Scenario: Ativo de outra Loja
- **WHEN** um Gerente autenticado informa um ativo pertencente a outra Loja
- **THEN** o Xano rejeita a operação como não autorizada sem criar chamado e sem usar uma Loja informada pelo cliente

#### Scenario: Categoria inexistente ou não permitida
- **WHEN** o Gerente informa uma categoria inexistente ou com `permite_abertura_manual` diferente de `true`
- **THEN** o Xano rejeita a submissão sem criar chamado

#### Scenario: Submissões manuais repetidas
- **WHEN** duas submissões manuais válidas são processadas separadamente, ainda que tenham os mesmos dados
- **THEN** o Xano cria um novo chamado para cada submissão e não aplica a deduplicação do heartbeat

### Requirement: Resposta da abertura contém o chamado criado
O sistema DEVE (MUST) responder à criação válida com status HTTP de criação e um objeto `chamado` contendo `id`, `titulo`, `descricao`, `status`, `prioridade`, `origem`, `criado_em`, `sla_horas_aplicado`, ativo, categoria, solicitante e técnico responsável quando existir. A resposta NÃO DEVE (MUST NOT) expor credenciais, campos internos de autenticação nem tratar `created_at` como data funcional.

#### Scenario: Resposta de criação
- **WHEN** o chamado manual é persistido com sucesso
- **THEN** o Xano retorna HTTP 201 e o objeto funcional do chamado criado com `tecnico` nulo enquanto não houver atribuição

### Requirement: Gerente acompanha todos os chamados da própria Loja
O sistema DEVE (MUST) fornecer `GET /gerente/chamados` e `GET /gerente/chamados/{chamados_id}` no grupo `mira-service-desk`. A lista DEVE (MUST) retornar `items` com resumo funcional e o detalhe DEVE (MUST) retornar um objeto `chamado` com os campos do contrato de criação; ambos DEVEM (MUST) determinar pertencimento à Loja pela relação persistida entre chamado, ativo e Loja, independentemente do solicitante e da origem.

#### Scenario: Lista da Loja
- **WHEN** um Gerente autenticado consulta a lista de chamados
- **THEN** o Xano retorna todos os chamados associados a ativos de sua Loja, incluindo chamados de outros solicitantes e chamados automáticos, sem retornar chamados de outras Lojas

#### Scenario: Detalhe da própria Loja
- **WHEN** um Gerente consulta o identificador de um chamado relacionado a um ativo de sua Loja
- **THEN** o Xano retorna o detalhe funcional do chamado

#### Scenario: Detalhe de outra Loja
- **WHEN** um Gerente consulta o identificador de um chamado relacionado a um ativo de outra Loja
- **THEN** o Xano rejeita a operação como não autorizada sem retornar os dados do chamado

#### Scenario: Chamado inexistente
- **WHEN** o Gerente consulta um identificador de chamado que não existe
- **THEN** o Xano responde como recurso não encontrado

### Requirement: Contratos funcionais preservam autenticação e negação por padrão
Todas as operações de `mira-service-desk` DEVEM (MUST) exigir autenticação da tabela `usuarios`, autorizar somente o perfil Gerente nesta capacidade e aplicar o escopo persistido de Loja no Xano. Os contratos funcionais NÃO DEVEM (MUST NOT) reabrir os endpoints genéricos de POST, PATCH ou DELETE nem atribuir autorização ao Reflex.

#### Scenario: Token ausente ou inválido
- **WHEN** uma operação funcional recebe uma requisição sem token válido
- **THEN** o Xano responde como não autenticado sem consultar ou modificar dados protegidos

#### Scenario: Perfil autenticado sem permissão
- **WHEN** um Técnico ou usuário da Diretoria chama uma operação funcional reservada ao Gerente
- **THEN** o Xano responde como não autorizado sem executar a operação

#### Scenario: Mutação genérica direta
- **WHEN** um usuário tenta usar os CRUDs genéricos existentes para criar, editar ou excluir chamado
- **THEN** a negação consolidada permanece aplicada e nenhum registro é modificado

### Requirement: Erros funcionais possuem classificação estável
Os contratos de `mira-service-desk` DEVEM (MUST) distinguir autenticação ausente ou inválida, falta de autorização, recurso inexistente, entrada incompatível com o contrato e indisponibilidade do serviço, sem retornar dados protegidos ou executar mutação parcial.

#### Scenario: Classificação dos erros HTTP
- **WHEN** uma chamada funcional falha
- **THEN** o contrato usa 401 para sessão não autenticada, 403 para perfil ou escopo não autorizado, 404 para recurso inexistente, 422 para entrada inválida e resposta 5xx para falha interna ou indisponibilidade do backend

### Requirement: Compatibilidade automática é limitada aos novos dados compartilhados
O criador automático existente DEVE (MUST) continuar aplicando seu título, status `Novo`, prioridade `Urgente`, categoria, ativo e verificação atual de incidente equivalente, acrescentando somente origem `automatico`, `criado_em` definido pelo backend e snapshot de SLA. Esta capacidade NÃO DEVE (MUST NOT) alterar o limite de heartbeat, o conjunto atual de status considerados abertos, a deduplicação concorrente, o encerramento automático nem o tratamento de ativo sem telemetria.

#### Scenario: Heartbeat cria incidente compatível
- **WHEN** a condição atual do heartbeat determina a criação de um incidente
- **THEN** o Xano cria o registro com os novos dados compartilhados sem alterar os demais critérios ou valores já usados pelo fluxo

#### Scenario: Heartbeat encontra incidente equivalente
- **WHEN** a verificação atual encontra um incidente equivalente aberto
- **THEN** nenhum novo chamado é criado, com a mesma regra anterior a esta capacidade
