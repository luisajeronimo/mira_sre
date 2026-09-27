## 1. Preparação e segurança da migração Xano

- [x] 1.1 Consultar o workspace e a branch alvo, comparar tabelas, categorias, chamados, endpoint `verificar-falhas` e grupos de API com o snapshot local e verificar que o inventário do diff foi registrado sem alterar recursos remotos.
- [x] 1.2 Registrar um ponto de recuperação dos recursos e dados afetados, incluindo os valores textuais originais de `categorias_servico.sla_horas`, e verificar que o procedimento de rollback pode restaurá-los sem apagar chamados novos.
- [x] 1.3 Inventariar todos os consumidores existentes de `categorias_servico.sla_horas` em XanoScript, Simulator, Fiscal, Reflex, testes, scripts e demais contratos locais relevantes, registrar a forma de uso e verificar compatibilidade ou adaptação necessária antes da mudança de `text` para `decimal`.
- [x] 1.4 Auditar por identificador todos os valores atuais de `sla_horas`, verificar quais são numericamente inequívocos e interromper a implementação diante de valor incompatível em categoria necessária, sem atribuir SLA padrão.
- [x] 1.5 Apresentar a tabela obrigatória de categorias existentes com ID, nome, tipo atual, SLA atual, vínculo com o heartbeat e valor atual/proposto de `permite_abertura_manual`; aguardar decisão humana explícita sobre quais IDs receberão `true`, sem classificação automática, e manter a categoria do heartbeat com proposta `false`.
- [x] 1.6 Consultar e validar com o Xano Developer MCP a sintaxe suportada para decimal, enum opcional, booleano padrão, resposta HTTP 201 e testes dos endpoints planejados, verificando que o XanoScript local segue a documentação atual.

## 2. Evolução do modelo e compatibilidade legada

- [x] 2.1 Atualizar localmente `chamados` com `descricao`, enum opcional `origem` (`manual`/`automatico`) e decimal opcional `sla_horas_aplicado`, mantendo `criado_em` anulável, e verificar que registros legados continuam representáveis sem backfill.
- [x] 2.2 Atualizar localmente `categorias_servico` com `permite_abertura_manual` padrão `false` e `sla_horas` decimal opcional, verificando que a definição não introduz faixa, SLA padrão ou nova taxonomia.
- [x] 2.3 Preparar a conversão controlada dos valores de SLA e a atribuição explícita das flags aprovadas, verificando em dry-run que somente valores inequívocos e categorias revisadas serão alterados.
- [x] 2.4 Verificar por inspeção e testes de dados que nenhum chamado existente recebeu origem, descrição, `criado_em` ou snapshot de SLA inferido e que chamados legados com ativo válido permanecem consultáveis.

## 3. Grupo funcional `mira-service-desk`

- [x] 3.1 Criar localmente o grupo autenticado `mira-service-desk` e verificar que possui canonical próprio, usa a autenticação `usuarios` e não altera os grupos CRUD existentes.
- [x] 3.2 Implementar `GET /gerente/ativos` com identidade e Loja derivadas do token e verificar por testes XanoScript Gerente autorizado, Gerente sem Loja, Técnico, Diretoria e isolamento entre duas Lojas.
- [x] 3.3 Implementar `GET /gerente/categorias` filtrando somente `permite_abertura_manual = true`, normalizando `desc` para `descricao`, e verificar que a categoria do heartbeat e categorias não classificadas não são retornadas.
- [x] 3.4 Implementar `POST /gerente/chamados` com os cinco inputs permitidos e verificar por harness local os campos obrigatórios, as quatro prioridades, prioridade inválida, `titulo`/`descricao` ausentes, vazios ou compostos somente por espaços, ausência de limite mínimo/máximo, categoria inexistente/bloqueada/sem SLA e ativo inexistente ou de outra Loja.
- [x] 3.5 Fazer a criação derivar solicitante, Loja, `Novo`, `manual`, `criado_em` e snapshot de SLA no Xano e verificar por harness local que campos extras do cliente não substituem esses valores e que duas submissões equivalentes criam dois chamados.
- [x] 3.6 Implementar o DTO e a resposta HTTP 201 da abertura e verificar por harness local que contém somente os campos funcionais previstos, usa `criado_em`, retorna técnico nulo quando aplicável e não expõe `created_at`, token ou credenciais.
- [x] 3.7 Implementar `GET /gerente/chamados` e verificar que retorna todos os chamados vinculados aos ativos da Loja, independentemente de solicitante e origem, excluindo outras Lojas e registros sem vínculo autorizável.
- [x] 3.8 Implementar `GET /gerente/chamados/{chamados_id}` verificando existência antes de relações e autorização, e validar por testes sucesso, chamado legado, identificador inexistente e chamado de outra Loja.
- [x] 3.9 Padronizar nos cinco contratos as respostas 401, 403, 404, 422 e 5xx e verificar por testes locais de transporte/harness que falhas não retornam dados protegidos nem deixam criação parcial.
- [x] 3.10 Executar novamente os testes negativos dos POST/PATCH/DELETE genéricos e verificar que a negação por padrão consolidada continua intacta.

## 4. Compatibilidade do criador automático

- [x] 4.1 Alterar somente o bloco de criação de chamado em `verificar-falhas` para preencher `origem = automatico`, `criado_em` pelo backend e `sla_horas_aplicado` da categoria, verificando que os demais passos do endpoint não foram modificados.
- [x] 4.2 Adicionar testes XanoScript para a criação automática compatível e verificar origem, timestamp e snapshot de SLA sem descrição ou solicitante inventados por meio de harness local isolado, sem executar o endpoint remoto.
- [ ] 4.3 Executar cenários de regressão do heartbeat e verificar que limite de 15 minutos, status abertos existentes, não duplicidade sequencial, ativo sem telemetria e retorno a Online permanecem com o comportamento anterior.

## 5. Cliente Reflex do Service Desk

- [x] 5.1 Documentar `XANO_SERVICE_DESK_BASE_URL` em `.env.example` sem URL específica e implementar sua leitura independente, verificando que ausência/placeholder falha explicitamente e que não há fallback para `XANO_AUTH_BASE_URL` ou `XANO_BASE_URL`.
- [x] 5.2 Implementar modelos tipados para ativo, categoria, resumo e detalhe de chamado e verificar por testes respostas válidas, coleções vazias e campos anuláveis de registros legados.
- [x] 5.3 Implementar o adaptador assíncrono para os cinco contratos reutilizando timeout, Bearer e erros comuns sem alterar a API pública de autenticação, e verificar que cada método usa a base, rota, verbo e payload corretos.
- [x] 5.4 Mapear 401, 403, 404, 422, resposta inválida, timeout, conexão e 5xx para erros distintos e verificar todos os casos com transporte HTTP simulado, sem incluir corpos sensíveis nas mensagens.
- [x] 5.5 Executar integralmente os testes existentes de login, `/me`, State e configuração e verificar que a extração ou reutilização de transporte não introduziu regressão na fundação de sessão.

## 6. State, páginas e navegação do Gerente

- [x] 6.1 Implementar o State de chamados reutilizando token backend-only e revalidação do perfil Gerente, com estados separados de dados, carregamento, sucesso e erro, e verificar que token e Loja não são sincronizados como autoridade para o frontend.
- [x] 6.2 Transformar `/gerente` na listagem básica e implementar estados de carregamento, vazio, erro e valores legados não informados, verificando que cada item navega para seu detalhe e que a ação de abertura permanece disponível.
- [x] 6.3 Implementar `/gerente/chamados/novo` com catálogos do Xano, quatro prioridades e os cinco campos aprovados, verificando que o POST não envia solicitante, Loja, status, origem, timestamps, técnico ou SLA aplicado.
- [x] 6.4 Implementar bloqueio do mesmo envio enquanto o POST está em andamento, confirmação e redirecionamento ao detalhe após sucesso, verificando também que uma nova submissão posterior permanece permitida e independente.
- [x] 6.5 Implementar `/gerente/chamados/[chamado_id]` como detalhe somente leitura e verificar apresentação de dados completos, nulos legados, técnico ausente, 404 e ausência de controles de edição, atribuição ou tratativa.
- [x] 6.6 Estender a casca do Gerente com destinos de listagem e abertura, manter Técnico e Diretoria neutros e aplicar guards às novas rotas, verificando redirecionamento de visitante e de perfil indevido sem tratar navegação como autorização.
- [x] 6.7 Integrar o tratamento de 401 ao encerramento consolidado da sessão e preservar a sessão em 403, 404, 422 e indisponibilidade, verificando por testes de State todas as transições e mensagens correspondentes.

## 7. Verificação integrada e sincronização controlada

- [x] 7.1 Executar a suíte Python completa e a compilação Reflex e verificar que cliente, State, Vars, eventos, rotas estáticas/dinâmicas e fundações existentes passam sem erro.
- [x] 7.2 Validar todo XanoScript alterado com o Xano Developer MCP e os testes inline e verificar cobertura de autorização, Loja/ativo, categoria manual, prioridade, origem, `criado_em` e snapshot de SLA.
- [x] 7.3 Executar `xano workspace push --dry-run`, revisar o diff completo e verificar que somente schema, dados explicitamente aprovados, `mira-service-desk` e o bloco mínimo do heartbeat serão afetados antes de solicitar aprovação para sincronização.
- [ ] 7.4 Após aprovação explícita, sincronizar na ordem prevista pelo design e verificar no runtime os cinco contratos com dois Gerentes de Lojas distintas, sessão expirada, perfis indevidos, categoria bloqueada, ativo externo e chamado legado.
- [ ] 7.5 Executar Simulator e o disparo principal do Fiscal em validação de regressão e verificar que telemetria, heartbeat e criação automática continuam operacionais sem autenticação de máquina nova.
- [x] 7.6 Revisar o diff final e verificar que não foram adicionados fila técnica, atribuição, interações, diagnóstico, solução, novos status/transições, dashboards, indicadores, MTTD, MTTR, compliance de SLA ou endurecimento de deduplicação.
