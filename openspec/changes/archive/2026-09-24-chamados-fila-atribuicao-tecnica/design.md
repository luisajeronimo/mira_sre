## Context

O estado atual possui `chamados.tecnico_id` como FK opcional, mas não possui timestamp de atribuição, contratos técnicos ou UI de fila. Chamados manuais e automáticos começam em `Novo` sem Técnico; o heartbeat continua usando `Novo`, `Em Atendimento` e `Aguardando Terceiro` apenas para deduplicação de incidentes abertos. O Técnico tem consulta global consolidada nos endpoints genéricos, enquanto suas mutações genéricas são negadas.

Esta change adiciona uma jornada técnica separada da tratativa. O contrato de autenticação continua sendo `usuarios`, a autorização continua no Xano e o grupo existente `MIRA Service Desk` será reutilizado.

## Goals / Non-Goals

**Goals:**

- Evoluir `chamados` de forma aditiva com `atribuido_em` opcional, sem backfill.
- Expor as visões Xano `nao_atribuidos` e `atribuidos_a_mim`, sempre filtradas no backend e ordenadas por `id desc`.
- Consultar detalhe técnico global sem permitir mutações de tratativa.
- Implementar autoatribuição derivada de `$auth.id`, idempotente para o mesmo Técnico e com a proteção de concorrência best-effort disponível no plano Free do Xano.
- Transformar `/tecnico` em fila e adicionar detalhe técnico, preservando sessão backend-only e o cliente Service Desk existente.
- Validar os contratos com testes de autorização, DTO, erro, legado, concorrência e regressão.

**Non-Goals:**

- Alterar status ou iniciar `Em Atendimento`/`Aguardando Terceiro`.
- Implementar work log, diagnóstico, solução, resolução, encerramento, cancelamento, reabertura, liberação ou reatribuição.
- Ordenar por prioridade ou SLA, calcular vencimento, pausa, SLA compliance, MTTD ou MTTR.
- Adicionar paginação, filtros AND/OR, dashboards ou indicadores.
- Alterar abertura manual, heartbeat, Simulator ou Fiscal.
- Alterar, excluir ou limpar chamados antigos.

## Decisions

### 1. Contratos dedicados no grupo existente

Serão adicionados `GET /tecnico/chamados?visao=...`, `GET /tecnico/chamados/{chamados_id}` e `POST /tecnico/chamados/{chamados_id}/assumir` ao grupo `MIRA Service Desk`. O contrato técnico não reutiliza o CRUD genérico para mutação, porque esses endpoints continuam negados por padrão.

Alternativa rejeitada: fazer o Reflex consultar o CRUD global e filtrar localmente. Isso permitiria respostas inconsistentes, não formalizaria as visões e transferiria autorização para o frontend.

### 2. Elegibilidade e escopo

`nao_atribuidos` significa `status = "Novo"` e ausência de Técnico (`tecnico_id = null` ou a representação legada `tecnico_id = 0`). `atribuidos_a_mim` significa `status = "Novo"` e `tecnico_id = $auth.id`. Status nulo, outros status e chamados atribuídos a outro Técnico ficam fora das duas visões. O Técnico mantém escopo global de consulta; `lojas_id` não será usado como filtro.

Alternativa rejeitada: incluir todos os status considerados abertos pelo heartbeat. Esses status pertencem à deduplicação automática e não foram aprovados como ciclo funcional da fila.

### 3. Timestamp aditivo de atribuição

`atribuido_em` será `timestamp?` no schema. O Xano preencherá o campo somente na transição de ausência de Técnico (`tecnico_id = null` ou `0`) para o Técnico autenticado. Registros antigos permanecem nulos e nenhuma informação será inferida de `created_at`, `criado_em` ou histórico de usuário.

O campo não participa de ordenação, SLA ou indicadores nesta change; preserva apenas o fato histórico da atribuição para uso futuro aprovado. Quando a ausência legada estiver representada por `0`, a assunção pode substituí-la pelo Técnico autenticado, sem backfill de registros não assumidos.

### 4. Assunção com recursos do plano Free e concorrência best-effort

O endpoint usará somente operações normais disponíveis no plano Free: `db.get`, validações, `db.edit` e o agrupamento `db.transaction { stack { ... } }`. A documentação do Xano descreve níveis de isolamento, mas a validação sintática no parser disponível rejeitou a propriedade `isolation` e aceitou somente a forma de transação sem esse parâmetro. `db.direct_query` e Direct Database Access não fazem parte da implementação.

O fluxo fará uma leitura inicial para classificar o chamado e, dentro da transação suportada, relerá o registro antes de editar. A edição só ocorrerá se o status continuar `Novo` e a ausência de Técnico continuar representada por `null` ou `0`. Após a edição, o endpoint relerá o chamado e validará o resultado antes de retornar o DTO. Se a releitura observar outro Técnico, responderá HTTP 409 sem sobrescrever a atribuição observada. Essa sequência reduz a janela de decisões com dados obsoletos, mas não é compare-and-set.

O plano Free não fornece evidência de isolamento forte ou atualização condicional suficiente para garantir matematicamente um único vencedor em duas escritas exatamente simultâneas. Em condições normais, uma requisição que observa a atribuição efetivada pela outra retorna 409; uma corrida exatamente simultânea pode permanecer sujeita à ordem de gravação do Xano. Essa limitação é aceita e documentada para o projeto acadêmico, sem afirmar atomicidade forte ou exatamente um vencedor.

Dentro da operação:

1. chamado inexistente produz 404;
2. `status != Novo` ou `status = null` produz 422;
3. `tecnico_id = $auth.id` retorna o estado atual sem novo timestamp;
4. `tecnico_id` de outro Técnico produz 409 sem sobrescrita;
5. ausência de Técnico (`tecnico_id = null` ou `0`) recebe `$auth.id` e `atribuido_em = now` uma única vez.

Alternativa rejeitada: sequência HTTP `GET -> verificar -> PATCH`, que permite que dois Técnicos observem ausência antes de escrever sem releitura e sem classificação do conflito.

### 5. DTOs e compatibilidade

Os DTOs técnicos reutilizarão a forma funcional consolidada do Gerente, adicionando `atribuido_em` e mantendo nulos legados. A listagem exibirá somente dados necessários à triagem; o detalhe poderá exibir descrição, ativo, categoria, solicitante e Técnico atual, mas nenhum controle de tratativa.

### 6. Reflex e concorrência observável

O State técnico manterá a visão selecionada, coleção, detalhe, carregamento, erro e assunção em andamento. A ação `Assumir` aparecerá somente quando o DTO indicar `status = Novo` e `tecnico = null`; `atribuido_em` é somente informação histórica e não é uma terceira condição visual. Em HTTP 409, o Reflex não altera o item localmente: informa a disputa e recarrega a lista ou detalhe para refletir a autoridade do Xano.

## Risks / Trade-offs

- [Corrida de assunção] Dois Técnicos podem clicar simultaneamente → validação antes da edição, transação com operações Free e releitura após a edição reduzem sobrescritas; em ordem normal o conflito observado retorna 409, mas o Free não garante matematicamente um único vencedor em simultaneidade exata.
- [Lista obsoleta] Um chamado pode ser assumido após o carregamento → tratar 409 e recarregar dados no Reflex.
- [Status sem enum] O schema permite textos arbitrários → filtrar explicitamente somente `Novo` e não criar transições nesta change.
- [Legados incompletos] Campos novos podem ser nulos → DTOs tipados aceitam nulos e nenhum backfill é executado.
- [Fila sem paginação] A resposta pode crescer → registrar limitação e planejar paginação em change posterior, sem introduzi-la agora.
- [SLA sem relógio de vencimento] `sla_horas_aplicado` é snapshot, não prazo calculado → não ordenar nem derivar indicadores.
- [Referências inconsistentes] `tecnico_id` pode apontar para dados antigos → não tratar referência inválida como “não atribuído”; preservar e sinalizar por contrato conforme validação de dados.
- [Exposição global] Técnico consulta globalmente → manter autorização explícita no Xano e DTO sem credenciais ou campos internos.

## Migration Plan

1. Auditar localmente schema, consumidores de `chamados` e distribuição remota de `status`/`tecnico_id` com operações somente leitura.
2. Validar no Xano Developer MCP a sintaxe de `timestamp?`, transação/isolamento e resposta HTTP 409.
3. Adicionar `atribuido_em` opcional sem backfill.
4. Adicionar funções e endpoints técnicos no grupo `MIRA Service Desk`, mantendo CRUDs genéricos negados.
5. Implementar e testar cliente, State, rotas e componentes Reflex.
6. Executar testes locais, validação XanoScript, compilação Reflex e OpenSpec strict.
7. Executar `xano workspace push --dry-run`, apresentar o diff completo e aguardar aprovação humana antes de qualquer push real.
8. Após aprovação, sincronizar apenas o diff aprovado e validar a jornada técnica em ambiente controlado.

Rollback: interromper antes do push quando o dry-run divergir; após sincronização, remover/desativar apenas os contratos novos e o código da jornada, preservando `atribuido_em` nulo dos registros antigos e os valores de `tecnico_id`/`atribuido_em` já gravados. Não excluir chamados nem fazer limpeza de dados.

## Open Questions

Nenhuma decisão de negócio está pendente neste escopo; os status elegíveis, visões, ordenação, idempotência, conflito e limites foram aprovados no pedido desta change. A sintaxe das operações Free foi validada no Xano Developer MCP e no parser local. A cobertura de corrida deve registrar o conflito observável e a limitação de simultaneidade exata; não deve declarar garantia matemática de um único vencedor.
