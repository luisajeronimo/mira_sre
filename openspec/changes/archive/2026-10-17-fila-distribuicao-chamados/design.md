# Design

## Context

Ver [proposta](proposal.md) e deltas de [fila](specs/chamados-fila-atribuicao-tecnica/spec.md) e [autorização](specs/autorizacao-perfis/spec.md). A capacidade concentra a consulta global de fila e detalhe para os perfis técnicos autorizados. `chamados` já possui `tecnico_id` e `atribuido_em`, enquanto `interacoes_chamado` preserva comentários e eventos históricos de atribuição.

Restrições relevantes: o Xano permanece autoridade de autenticação, perfil e dados consultados; a capacidade deve funcionar no plano Free. A tela evolui a fila e o detalhe Reflex existentes, sem redesign.

## Goals / Non-Goals

**Goals:**

- Oferecer uma fila global com filtros explícitos e escopos de consulta aprovados.
- Expor no detalhe o responsável atual, `atribuido_em` e a timeline com comentários e eventos legados em ordem cronológica.
- Manter um DTO canônico de consulta entre Xano, service, State e Reflex.

**Non-Goals:**

- Definir comandos independentes para assumir, atribuir, reatribuir ou liberar responsável.
- Criar nova tabela, endpoint de histórico, endpoint de lista de Técnicos ou jornada paralela de comentários.
- Modificar a jornada de comentários do Gerente.

## Decisions

### Evoluir os contratos de consulta existentes

- Ampliar `GET /tecnico/chamados` para Técnico, Diretoria e Administrador e aplicar os mesmos filtros explícitos da listagem do Gerente: número, status, Totem e período de abertura. A tela usa uma única tabela global: sem filtro, `Todos` é o conjunto global completo e não restringe status, responsável, origem, solicitante, data ou Loja. Para Técnico, `Atribuídos a mim` é um escopo rápido fora do painel de filtros operacionais e envia um parâmetro explícito que o Xano traduz para `tecnico_id == $auth.id`; esse escopo não é uma preferência de filtro persistente. Diretoria e Administrador permanecem em `Todos`. A interface não oferece escopo para chamados atribuídos a outros Técnicos ou não atribuídos.
- Ampliar `GET /tecnico/chamados/{id}` para os mesmos perfis e retornar o detalhe canônico, incluindo responsável atual, `atribuido_em` e timeline. O detalhe é um contrato de consulta global e não depende de CRUD genérico.
- Exigir sessão e perfil autorizado no Xano para lista e detalhe. O Gerente permanece fora da fila técnica global.

### Preservar dados de responsável e histórico legado

- Reutilizar `chamados.tecnico_id` e `chamados.atribuido_em` como dados de leitura do responsável atual, sem backfill ou inferência para registros históricos.
- Manter comentários legados e eventos `atribuicao`, `reatribuicao` e `liberacao` na timeline. Para ordenar interação legada sem `criado_em`, usar seu `created_at` persistido; para entradas que possuem `criado_em`, usar esse instante. A coleção combinada é ordenada descendentemente pelo instante efetivo e, em empate, pelo id da interação.
- Incluir na resposta do detalhe os comentários e eventos visíveis aos perfis da fila em uma única lista. A jornada do Gerente continua usando seus contratos próprios de comentários públicos.

### Reutilizar a tela e o State Reflex

- Adaptar a página de fila, `ChamadosTecnicoState`, service e detalhe atuais para os perfis autorizados, reutilizando a estrutura de tabela e filtros da listagem do Gerente e exibindo o responsável atual. O State separa valores de consulta enviados e filtros confirmados: somente uma resposta bem-sucedida substitui o resultado e altera sua indicação visual. Uma falha preserva o último resultado e seus filtros confirmados, sem apresentar o rascunho como aplicado.
- Respostas 401 encerram a sessão; 403 preservam a sessão e informam autorização negada. Falhas de contrato, rede ou filtro são mostradas como erro de carregamento ou de filtro, sem serem apresentadas como falha de identidade.
- O mesmo DTO canônico de chamado é usado pela lista, detalhe, service e State. Campos obrigatórios ausentes são falha de contrato, nunca valores silenciosamente convertidos em `undefined`.

### Gestão operacional posteriormente substituída

A gestão operacional do responsável foi posteriormente substituída pela change `tratativa-operacional-chamados`. Esta change preserva somente a consulta de fila, detalhe e histórico compatível; ela não define caminho funcional atual para mutar o responsável.

### Alternativas consideradas

- **Tabela de auditoria separada:** rejeitada porque `interacoes_chamado` já é a entidade de histórico do domínio e preserva os eventos legados necessários à consulta.
- **Duas listas visuais de comentários e eventos:** rejeitada porque exigiria compor e ordenar listas no Reflex e quebraria a cronologia única.

## Risks / Trade-offs

- **[Risco] Interações históricas podem não ter `criado_em`.** → Usar o `created_at` persistido como instante efetivo legado, sem backfill nem data inventada.
- **[Risco] A consulta global pode divergir da jornada do Gerente.** → Reutilizar filtros explícitos e validar o DTO e os estados de consulta contra respostas reais do Xano.

## Migration Plan

Não há migração de dados nesta sanitização documental. Registros existentes, `atribuido_em` e eventos legados permanecem preservados; a gestão operacional posterior é definida exclusivamente em `tratativa-operacional-chamados`.

## Open Questions

Nenhuma. O escopo sobrevivente desta change é consulta global de fila e detalhe.
