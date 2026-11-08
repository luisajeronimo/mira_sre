# Design

## Context

Ver `proposal.md` para motivação e `specs/` para comportamento. Hoje `POST /administracao/usuarios` e `GET /administracao/lojas` sustentam a criação de usuários; `GET /administracao/lojas` devolve somente `{id, nome}`. Os CRUDs gerados de `usuarios`, `lojas` e `ativos_referencia` não são o caminho administrativo e as mutações genéricas chamam `autorizacao/negar_mutacao_generica`. A página Reflex `/administracao/usuarios` contém apenas criação. `lojas` possui `nome`, `endereco`, `regiao`, `status` opcionais; `ativos_referencia` possui `nome_ativo`, `tipo`, `status_atual` e `lojas_id`, sem identificação cadastral distinta do ID.

Os fatos não guardam diretamente a Loja da ocorrência: `chamados`, `telemetria_equipamentos` e `historico_disponibilidade_totens` apontam para `ativos_referencia`. A listagem e a autorização do Gerente derivam a Loja de `ativos_referencia.lojas_id` atual. `chamados` referencia `solicitante_id` e `tecnico_id`; `interacoes_chamado` guarda autor e Técnicos anteriores/novos; `preferencias_fila_chamados` referencia Usuário, Loja, Totem e responsável. Essas relações são relevantes para exclusão física.

## Goals / Non-Goals

**Goals:** contratos de administração com autoridade no Xano, integração Reflex reutilizando a criação vigente, integridade de transferências e exclusões, e compatibilidade com registros legados sem backfill.

**Non-Goals:** migrar a autenticação; abrir CRUDs genéricos; reconstruir a criação de usuário; redefinir heartbeat, Simulator ou Fiscal; inferir situação operacional de Totem sem telemetria; suspender operações existentes pela situação cadastral da Loja.

## Decisions

### 1. Contratos administrativos separados dos CRUDs gerados

**Decisão técnica proposta:** manter `POST /administracao/usuarios` e o catálogo mínimo `GET /administracao/lojas` para o seletor já existente. Criar contratos específicos de coleção e detalhe para leitura, edição e exclusão, com caminhos distintos quando o GET atual de Lojas precisa permanecer mínimo; por exemplo, `/administracao/lojas/registros` para a listagem gerencial e `/administracao/lojas/{id}` para detalhe/mutação. Usar projeções explícitas sem campos sensíveis e `autorizacao/exigir_perfil(administrador: true)` em toda operação. Revalidar entrada e dependências no Xano no instante da escrita. As rotas exatas e o formato de erro serão fechados durante o Apply sem mudar os cenários das specs.

**Alternativa descartada:** desbloquear os endpoints `apis_from_table_*`; seus payloads e superfícies de mutação excedem o contrato aprovado.

### 2. Modelos novos e compatibilidade de registros existentes

**Decisão técnica proposta:** validar nome, endereço e região não vazios nos novos contratos de Loja; gravar status canônico `Ativa`/`Inativa` e iniciar sempre `Ativa`. Para Totem, acrescentar identificação cadastral própria (por exemplo, `identificacao`) sem trocar o ID nem `nome_ativo`; manter `tipo` compatível com a representação atual e não gravar `online`/`offline` na criação sem primeira telemetria. Campos legados opcionais podem continuar nulos; a obrigatoriedade vale para novas criações e edições feitas pelo contrato administrativo, sem migração forçada. Os valores legados `ativa` dos mocks e `Ativo` encontrados na `v1` são lidos como situação ativa para selecionar destino, sem reescrever as linhas; valores ausentes não são presumidos Ativa. Novas criações e edições continuam aceitando apenas `Ativa`/`Inativa`. Não se presume unicidade da identificação, pois o requisito aprovado não a define.

**Alternativa descartada:** transformar os campos existentes em NOT NULL em todos os registros; isso exigiria backfill ou rejeitaria dados históricos.

### 3. Edição de usuário e integridade de responsabilidades

**Decisão técnica proposta:** limitar a edição aos campos aprovados. Reusar a validação de e-mail, perfil e Loja, acrescentando situação `Ativa` somente ao novo vínculo ou destino de Gerente; editar nome/e-mail de Gerente já vinculado a Loja `Inativa` não cria vínculo novo. Ao sair do perfil `tecnico`, consultar `chamados.tecnico_id` antes da escrita e bloquear se houver responsabilidade atual, inclusive em chamado terminal, pois a referência continua significando Técnico responsável. Preservar IDs de usuário em `solicitante_id`, `tecnico_id`, `interacoes_chamado` e preferências; não reatribuir autorias ou chamados.

**Último Administrador — aprovado:** na exclusão ou mudança de perfil de `administrador`, o Xano deve impedir resultado com zero Administradores. A mesma regra cobre edição da própria conta; exclusão da própria conta continua sempre proibida. Um Administrador pode mudar de perfil quando outro permanecer. Implementar contagem e escrita na mesma `db.transaction` e validar os casos sequenciais. A sintaxe `db.query usuarios` com `lock = true` dentro da transação passou no parser MCP e pode ser usada quando a semântica do ambiente for confirmada, mas o parser não demonstra proteção contra duas alterações simultâneas. `isolation = "serializable"` foi recusado pelo parser e não será adotado. A ausência de teste concorrente não impede iniciar o Apply acadêmico; a garantia concorrente permanece **não verificada** e deve constar da evidência final, sem ser declarada atendida por inferência.

**Alternativa descartada:** alterar o perfil e limpar automaticamente `tecnico_id`; isso perderia responsabilidade e histórico.

### 4. Histórico temporal Totem–Loja — aprovado

**Observação:** mudar apenas `ativos_referencia.lojas_id` moveria retrospectivamente chamados antigos nas consultas do Gerente e nos filtros de Loja. Não existe snapshot de Loja no chamado, na telemetria ou no evento. `created_at` técnico não substitui o instante funcional de ocorrência.

**Representação proposta:** criar `historico_vinculos_totem_loja` com `id`, `ativos_referencia_id`, `loja_origem_id` opcional, `loja_destino_id` obrigatório, `tipo` (`criacao`, `marco` ou `transferencia`) e `efetivado_em` obrigatório. Um Totem novo recebe evento inicial com origem nula e destino da criação; cada transferência registra origem atual, destino `Ativa` e um único instante efetivo definido pelo Xano. O vínculo atual em `ativos_referencia.lojas_id` muda na mesma unidade de escrita do evento; IDs e linhas de fatos não mudam. Indexar `(ativos_referencia_id, efetivado_em)` e exigir ordem temporal inequívoca por Totem. Revalidar Totem, destino e último evento antes de gravar. Sem evento inicial para Totem legado, a primeira transferência registra somente o instante comprovado da mudança e o destino; `loja_origem_id` comprova a origem imediatamente anterior, mas não prova toda a trajetória passada. Se um novo chamado manual ou automático for aberto antes da primeira transferência de Totem legado, o Xano registra um `marco` no mesmo instante funcional `criado_em`, sob bloqueio do Totem e na mesma transação do chamado. Esse marco comprova apenas a Loja observada no instante do novo chamado; fatos anteriores continuam sem Loja histórica demonstrável. A ingestão de telemetria com `evento_timestamp` fornecido externamente não usa a Loja atual para criar marco retroativo.

**Resolução:** para fato com instante `t`, escolher o evento de vínculo do mesmo Totem com maior `efetivado_em <= t`; a Loja é `loja_destino_id`. O intervalo de validade é `[efetivado_em, próximo efetivado_em)`, portanto fato exatamente no instante da transferência pertence ao destino. Se não houver evento anterior a `t` nem outra evidência histórica direta e confiável, a Loja histórica é indeterminada; não usar `ativos_referencia.lojas_id` atual como fallback. O Gerente não recebe chamado de Loja indeterminada. Consultas globais podem exibir o fato sem Loja histórica atribuída, sem fabricar valor. Esse efeito sobre fatos legados é consequência explícita da proibição de inferência aprovada.

**Instantes funcionais verificados no schema e nas funções atuais:** chamado usa `chamados.criado_em` (a criação manual e a automática definem esse instante; `created_at` não é fallback); telemetria usa `telemetria_equipamentos.evento_timestamp` (referência temporal já aprovada); evento de disponibilidade usa `historico_disponibilidade_totens.detectado_em` (momento da decisão Xano). Para fato legado sem o timestamp funcional, a Loja histórica permanece indeterminada. O timestamp de recepção de telemetria ou o da telemetria que motivou evento não substitui o instante do próprio fato. A abertura de chamado após transferência deriva a Loja do vínculo válido em `criado_em`.

**Alternativa descartada:** usar somente o vínculo atual ou fazer backfill de `lojas_id` nos fatos; a primeira desloca o histórico e a segunda viola a restrição expressa.

### 5. Situação cadastral de Loja — aprovada

`Ativa`/`Inativa` classifica somente o cadastro da Loja. Criar ou transferir Gerente/Totem exige destino `Ativa`; reativar permite novos vínculos. Gerentes e Totens já vinculados continuam operando: escopo do Gerente, monitoramento do Totem, chamados manuais e automáticos, tratativa, comentários e acompanhamento seguem as regras existentes. Não converter Totem para `offline`, não modificar telemetria nem interromper o Fiscal por inativação. Validação de destino não deve ser aplicada a operação que apenas conserva vínculo antigo, como edição de nome do Gerente.

### 6. Exclusão física por ausência de dependências

**Decisão técnica proposta:** cada DELETE específico verifica dependências por referência antes de remover o registro alvo. Usuário: `chamados.solicitante_id`, `chamados.tecnico_id`, os três campos de usuário em `interacoes_chamado`, preferências como dono/responsável e demais referências. Loja: `usuarios.lojas_id`, `ativos_referencia.lojas_id`, `preferencias_fila_chamados.lojas_id` e origem/destino no histórico temporal. Totem: chamados, telemetria, disponibilidade, preferências e histórico temporal. **Decisão humana adicional aprovada no Apply:** Totem sem telemetria, chamado, evento, preferência ou transferência pode ter seu único vínculo temporal inicial removido explicitamente na mesma transação da exclusão cadastral. Eventos de transferência e qualquer fato operacional impedem a exclusão; não há cascata automática. Falha de dependência retorna erro funcional sem mutação. Incluir proteção contra a própria conta e último Administrador. A checagem e o DELETE pertencem à mesma unidade de escrita para os fluxos normais. A corrida entre DELETE e criação simultânea de dependência não é eliminada apenas por uma transação; não alegar integridade concorrente sem evidência de constraint ou lock compartilhado. Esse risco não bloqueia o início da implementação acadêmica.

**Alternativa descartada:** cascata, limpeza automática de preferências ou exclusão forçada; essas opções contrariam o escopo e escondem dependências.

### 7. Abertura manual global do Administrador

**Decisão técnica proposta:** oferecer `POST /administracao/chamados` como entrada específica do Administrador e preservar `POST /gerente/chamados` exclusivo ao Gerente. Reusar a validação compartilhada de `service_desk/abrir_chamado_manual`: para Gerente, manter comparação com sua Loja; para Administrador, derivar a Loja do Totem sem restringir a uma unidade. O solicitante continua sendo `$auth.id`; cliente não fornece Loja nem usuário substituto. Usar contrato de leitura de Totens e categorias apropriado ao Administrador na UI.

**Alternativa descartada:** reproduzir a validação de abertura no Reflex ou criar um caminho que pule o Service Desk.

### 8. Área Reflex e navegação

**Decisão humana de revisão da experiência (2026-11-07):** o item Administração da sidebar aponta diretamente para `/administracao/gestao`; `/administracao` e `/administracao/usuarios` são apenas aliases protegidos. A criação antiga de usuário deixa de ter página e State próprios e usa o mesmo State da gestão. O dashboard apresenta três cards uniformes para Usuários, Lojas e Totens, inspirado na composição do frame Figma `Main` (`1:1459`) e no PNG sanitizado, com indicadores calculados dos DTOs administrativos reais. Cada card abre um modal de criação ou a listagem correspondente dentro da mesma rota. As listagens recebem busca textual, identificação, badges e ações de edição, transferência e exclusão com confirmação. Formulários de criação não ocupam o dashboard permanentemente. O fluxo global de abertura manual do Administrador parte de `/inicio` e usa o mesmo componente visual de formulário do Gerente em `/chamados/novo`; os dois endpoints já existentes continuam delegando à mesma função XanoScript, preservando as autorizações distintas. O botão `Criar chamado` de ambos os perfis compartilha a mesma composição de cabeçalho, posição e estilo. Os textos da interface descrevem a ação para o usuário, sem expor o mecanismo de validação do Xano. Estados de sessão e rascunhos são isolados por identidade, token e versão local. Guard de rota não substitui autorização Xano.

**Refino da apresentação:** IDs internos deixam de aparecer nas três listagens. Nomes de Lojas são resolvidos dos dados administrativos já carregados, inclusive na lista de usuários, e atualizados após edição da Loja. Badges de perfil e situação aparecem em maiúsculas sem alterar os valores canônicos usados nos contratos. O card de Usuários mostra a distribuição dos quatro perfis. A busca integra ícone e limpeza contextual no campo, enquanto o indicador da listagem mostra a contagem filtrada. A ação `Editar` do Totem continua permitindo mudar sua Loja no modal existente.

**Alternativa descartada:** criar três pontos de entrada independentes na sidebar; não é necessário para a jornada pedida e ampliaria a matriz vigente.

## Risks / Trade-offs

- **[Fatos legados sem evento inicial comprovável]** → retornar Loja histórica indeterminada e negar acesso do Gerente por padrão; não confundir Loja atual com histórica nem fazer backfill.
- **[Relógio/timestamp na fronteira de transferência]** → calcular instante efetivo no Xano, definir intervalos semiabertos e testar ocorrência exatamente na fronteira; não usar relógio do Reflex.
- **[Último Administrador sob duas mutações simultâneas]** → aplicar as validações no Xano e transação para os casos normais; registrar a garantia concorrente como não verificada se não houver evidência runtime. Não exigir teste de stress ou isolamento `serializable` para iniciar o Apply.
- **[DELETE concorrente com criação de dependência]** → revalidar dependências no Xano antes de excluir e demonstrar bloqueio funcional em caso sequencial; registrar a corrida residual se não houver constraint ou lock compartilhado comprovado.
- **[Transferência com escrita parcial]** → criar evento e atualizar vínculo atual na mesma `db.transaction`, verificando sucesso e falhas funcionais com dados de teste; não declarar rollback de falha provocada como comprovado se não tiver sido executado.
- **[Schema legado com campos nulos e status de Totem não classificado]** → validar no contrato administrativo novo sem alterar registros antigos; monitoramento deve tolerar estado desconhecido até a primeira telemetria.
- **[Uso de `GET /administracao/lojas` por criação atual]** → preservar seu DTO mínimo ou evoluí-lo somente com delta explícito, para não quebrar o formulário existente.

## Verificação técnica Xano Free nesta Propose

**Evidência local do Apply (2026-11-06):** o Xano Developer MCP validou sintaticamente 130 arquivos `.xs` do repositório, incluindo os contratos e funções desta change: 130 válidos, 0 inválidos e 2 avisos não bloqueantes. A suíte Python usa dados fictícios isolados; nenhuma gravação remota foi feita. Essa validação não executa regras funcionais nem confirma transações ou locks em runtime.

- **Confirmado na documentação do Xano Developer MCP (XanoScript 2.7.1) e em validação sintática de trechos descartáveis em memória:** `table` aditiva com referências/índice, `db.query` com comparação temporal, `return = {type: "exists"}`, `db.get`, `db.del`, `db.transaction` e `lock = true` em `db.get`/`db.query` são aceitos pelo parser. O repositório já usa `db.transaction` em autenticação, chamado e heartbeat. Nenhum XanoScript do projeto foi alterado para essa verificação.
- **Confirmado em documentação oficial:** o Free anuncia banco PostgreSQL, APIs e lógica de servidor, com limites de 100 mil registros e 10 requisições por 20 segundos; transações são documentadas como unidade de escrita com rollback em falha. Fontes: [planos Xano](https://www.xano.com/pricing/), [Database Transaction](https://www.xano.com/learn/database-transaction/) e [anúncio de record lock](https://community.xano.com/product-updates/post/1-54-3-sep-26-2023-udampVryBnr1RHQ).
- **Não confirmado:** execução desses padrões no workspace Free específico; semântica runtime de `lock = true`, ordem de locks, constraint referencial efetiva, ausência de corrida entre DELETE e criação simultânea de dependência, serialização de duas mudanças do último Administrador e rollback de falha intermediária provocada na transferência. O validador sintático não executa chamadas concorrentes nem prova garantias de runtime. Esses riscos serão registrados na demonstração acadêmica se permanecerem sem teste.
- **Divergência técnica:** a documentação MCP de `database` menciona `isolation = "serializable"`, mas o validador MCP rejeitou o atributo antes e depois de `stack` em `db.transaction`; portanto não usar esse atributo sem documentação e suporte coerentes. Não depender de conexão direta ao banco, recurso listado para planos pagos na página de preços.

## Migration Plan

1. Iniciar o Apply com os recursos básicos já identificados no Free. Validar cada XanoScript com o Developer MCP e executar testes funcionais com dados de teste à medida que os contratos forem implementados; documentar separadamente qualquer garantia concorrente ou rollback de falha provocada que não tenha sido verificado.
2. Acrescentar schema de forma aditiva, sem backfill nem alteração de registros históricos; publicar contratos administrativos e consultas históricas apenas quando a política de vínculo estiver completa.
3. Integrar Reflex e testar a criação atual, novas gestões, autorização negativa, transferências, exclusões e abertura manual global. Não alterar Simulator ou Fiscal.
4. Revisar diff de publicação; qualquer push real segue o gate do repositório. Após push autorizado, executar novo dry-run para confirmar ausência de alterações não aprovadas.
5. Em reversão, desabilitar novos contratos e restaurar código anterior sem excluir dados já criados; preservar toda estrutura ou fato histórico introduzido até haver plano de dados aprovado.
