# Design

## Context

Ver [proposta](proposal.md) e deltas de [fila](specs/chamados-fila-atribuicao-tecnica/spec.md) e [autorização](specs/autorizacao-perfis/spec.md). A implementação atual concentra fila, detalhe e `Assumir` em contratos do Service Desk para Técnico; `chamados` já possui `tecnico_id` e `atribuido_em`. `interacoes_chamado` já guarda autor, chamado, mensagem, visibilidade e timestamps, e o Xano já usa `db.transaction` na criação de comentário e na assunção.

Restrições relevantes: o Xano permanece autoridade de perfil, persistência e regras; a capacidade deve funcionar no plano Free. A tela evolui a fila e o detalhe Reflex existentes, sem redesign.

## Goals / Non-Goals

**Goals:**

- Reutilizar os contratos existentes de fila, detalhe e assunção.
- Guardar as mudanças de responsável como eventos estruturados em `interacoes_chamado` e expô-las junto aos comentários no detalhe.
- Manter o comando de atribuição e seu evento atômicos dentro do Xano.

**Non-Goals:**

- Alterar status ou criar eventos de status.
- Criar nova tabela, endpoint de histórico, endpoint de lista de Técnicos ou jornada paralela de comentários.
- Modificar a jornada de comentários do Gerente.

## Decisions

### Evoluir os contratos existentes

- Ampliar `GET /tecnico/chamados` para os três perfis globais e acrescentar pesquisa por número e filtros simples de responsável. A consulta Xano passa a incluir qualquer status; estados terminais continuam visíveis.
- Ampliar `GET /tecnico/chamados/{id}` para os mesmos perfis e retornar a timeline e uma lista mínima de Técnicos válidos (`id`, `nome`) para o seletor de atribuição. Essa lista no detalhe evita depender do CRUD genérico de usuários, que não fornece a consulta autorizada necessária, ou criar uma rota só para o seletor.
- Evoluir `POST /tecnico/chamados/{id}/assumir` para um comando de responsável com `acao` (`assumir`, `atribuir` ou `liberar`). `assumir` continua derivando o responsável de `$auth.id`; `atribuir` recebe o Técnico alvo; `liberar` não recebe alvo. Para manter o uso atual, ausência de `acao` equivale a `assumir`. Nenhuma ação aceita `status` ou `atribuido_em` do cliente. Um único comando evita rotas paralelas para as operações do mesmo domínio.
- Validar no Xano a sessão, o papel, o estado do chamado e o perfil Técnico do usuário alvo. Técnico, Diretoria e Administrador podem atribuir/reatribuir; somente o Técnico responsável pode liberar como Técnico. Diretoria e Administrador podem liberar qualquer atribuição. Os CRUDs genéricos permanecem negados.

### Preservar dados de atribuição e atomicidade

- Reutilizar `chamados.tecnico_id` e `chamados.atribuido_em`; não adicionar campos a `chamados`. Definir `atribuido_em` ao assumir/atribuir/reatribuir, limpar ao liberar e deixá-lo intacto em `Assumir` idempotente.
- Na função Xano já usada pela rota, executar validação, mutação do chamado e criação do evento dentro de uma única `db.transaction`. Atualizar `ultima_atualizacao_em` somente quando o responsável realmente mudar. O evento usa o ator autenticado e o mesmo instante aplicado à atribuição.
- Respeitar `Encerrado` e `Cancelado` como terminais; `Resolvido` permanece elegível. A operação não escreve status. A proteção concorrente de `Assumir` permanece best-effort conforme a limitação já registrada para o plano Free; não prometer isolamento forte.

### Evoluir `interacoes_chamado` como timeline única

- Acrescentar campos opcionais para tipo (`comentario`, `atribuicao`, `reatribuicao`, `liberacao`) e Técnico anterior/novo. Reutilizar `chamados_id`, `usuarios_id` como autor e timestamps existentes. Eventos novos recebem `criado_em` do Xano e visibilidade interna; campos de Técnico anterior/novo referenciam usuários, mas só são preenchidos com perfis Técnico.
- Comentários legados sem tipo continuam sendo comentários. Não fazer backfill. Para ordenar interação legada sem `criado_em`, usar seu `created_at` já persistido; para entradas novas, usar `criado_em`. Ordenar ascendentemente pelo instante efetivo e, em empate, pelo id da interação.
- Incluir comentários públicos e internos visíveis aos perfis da fila e eventos internos na resposta do detalhe, em uma única lista. Não usar o CRUD genérico de interações nem fazer request Reflex separado para gravar histórico. A jornada do Gerente continua usando seus contratos atuais de comentários públicos.

### Reutilizar a tela e o State Reflex

- Adaptar a página de fila, `ChamadosTecnicoState`, service e detalhe atuais para os perfis autorizados, mantendo pesquisa, filtros simples, seletor de responsável e timeline no detalhe.
- A interface oculta ações incompatíveis com perfil/estado para orientar o uso, mas cada operação continua sendo autorizada e validada no Xano.

### Alternativas consideradas

- **Tabela de auditoria separada:** rejeitada porque `interacoes_chamado` já é a entidade de histórico do domínio e pode receber os campos estruturados necessários.
- **Requests separados para atribuição e histórico:** rejeitada porque poderia deixar responsável persistido sem evento; a função Xano existente já agrupa a assunção em transação.
- **Nova rota de responsável ou endpoint de Técnicos:** rejeitados nesta proposta para não duplicar o contrato de assunção nem criar consulta apenas para o seletor; os contratos existentes podem ser ampliados.
- **Duas listas visuais de comentários e eventos:** rejeitada porque exigiria compor e ordenar listas no Reflex e quebraria a cronologia única; o Xano já consulta as interações de um chamado.

## Risks / Trade-offs

- **[Risco] Alterar a rota chamada `assumir` para acomodar outras ações pode deixá-la semanticamente ampla.** → Manter um único comando de responsável, discriminar a ação no payload e preservar `assumir` como padrão compatível.
- **[Risco] O Xano Free não fornece garantia forte documentada para duas assunções simultâneas.** → Manter validação antes/depois e comportamento best-effort já existente; não declarar compare-and-set.
- **[Risco] Interações históricas podem não ter `criado_em`.** → Usar o `created_at` persistido como instante efetivo legado, sem backfill nem data inventada.
- **[Risco] A lista de Técnicos no detalhe contém dados de usuários.** → Retornar somente id e nome, filtrados no Xano para perfil `Técnico`.

## Migration Plan

1. Adicionar os campos opcionais de evento a `interacoes_chamado`, sem backfill nem remoção de dados.
2. Atualizar as funções e contratos Xano de fila, detalhe e responsável, incluindo a autorização e o evento na mesma transação.
3. Atualizar página, State, service e detalhe Reflex para consumir os contratos ampliados.
4. Validar os cenários das specs e OpenSpec antes de considerar a implementação concluída.

Rollback: reverter o consumo Reflex e a lógica dos contratos ao comportamento anterior. Os campos opcionais e eventos já persistidos permanecem sem exclusão; o schema aditivo não exige migração reversa.

## Open Questions

Nenhuma. As regras funcionais e o escopo das operações estão definidos nos deltas desta change.
