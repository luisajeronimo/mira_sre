# Proposal

## Why

O Gerente já pode abrir e consultar chamados da própria Loja, mas não dispõe de
acompanhamento público da evolução nem de uma data funcional confiável da última
alteração observável. A tabela física `interacoes_chamado` não distingue conteúdo
público de informação interna e, portanto, não pode ser exposta diretamente.

Esta change estabelece a fatia segura de acompanhamento: comentários públicos
autorizados por Loja, atualização temporal observável e detalhe completo do
Gerente, sem antecipar a lista operacional, filtros ou paginação.

## What Changes

- Adicionar `chamados.ultima_atualizacao_em`, inicialmente igual a `criado_em`
  nas criações novas e preservado como nulo nos legados sem fato confiável.
- Atualizar esse timestamp quando houver atribuição de Técnico e criação de
  comentário público; uma futura operação funcional de mudança de status deverá
  atualizá-lo no mesmo ato, sem esta change criar tratativa ou alteração de
  status.
- Evoluir `interacoes_chamado` com visibilidade explícita e comportamento
  fechado: registros sem classificação não são públicos nem retornados ao
  Gerente.
- Criar contratos funcionais específicos para o Gerente ler comentários públicos
  de um chamado da própria Loja e publicar comentário público não vazio em
  chamado não terminal. Autor, horário e visibilidade serão definidos pelo
  backend.
- Expor no detalhe do Gerente os dados já consolidados de Totem, Categoria,
  solicitante, Técnico, SLA, origem, abertura, `ultima_atualizacao_em` e autoria
  de sistema quando aplicável, além dos comentários públicos; data legada nula
  permanece explicitamente não informada.
- Preservar a leitura de comentários públicos em chamados `Encerrado` e
  `Cancelado`, bloqueando a criação nesses estados no backend.
- Manter fora do escopo a tabela operacional da lista, filtros, ordenação,
  contadores, paginação, rejeição de solução, edição/exclusão de comentários,
  anexos, notas privadas do Gerente e tratativa técnica.

## Capabilities

### New Capabilities

- `chamados-acompanhamento-gerente`: comentários públicos escopados por Loja,
  autoria derivada da sessão, visibilidade segura e semântica funcional da última
  atualização observável pelo Gerente.

### Modified Capabilities

- `chamados-abertura-manual`: inicializar `ultima_atualizacao_em` nas criações
  manual e automática, preservar nulos legados e estender o detalhe autorizado.
- `chamados-fila-atribuicao-tecnica`: atualizar `ultima_atualizacao_em` apenas
  quando uma assunção efetivamente altera a atribuição.
- `frontend-chamados-gerente`: completar o detalhe consolidado e disponibilizar
  leitura, postagem e descarte local de rascunho de comentários públicos.
- `monitoramento-disponibilidade-totens`: inicializar a última atualização no
  incidente automático criado pelo heartbeat, sem alterar suas regras.

## Impact

- Schema Xano de `chamados` e `interacoes_chamado`, sem backfill inferido.
- Funções e endpoints específicos no grupo `MIRA Service Desk`; os CRUDs
  genéricos permanecem bloqueados para mutação e não serão usados como contrato
  público.
- Fluxos existentes de criação manual, criação automática e assunção técnica,
  para gravação atômica da data funcional quando aplicável.
- Cliente tipado, DTOs, State e página de detalhe do Gerente no Reflex.
- Testes XanoScript, cliente/State Reflex e regressões de autorização, dados
  legados, visibilidade e estados terminais.
- Somente recursos compatíveis com o plano Free do Xano; sem credenciais, tokens
  ou alterações em dados remotos nesta fase de planejamento.
