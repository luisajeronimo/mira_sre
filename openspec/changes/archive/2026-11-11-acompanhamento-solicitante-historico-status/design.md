# Design

## Context

Ver [proposal.md](./proposal.md) para motivação, decisões e escopo. Estado verificado em `06cc763`:

- **Interações:** `interacoes_chamado.tipo_evento` ∈ {`comentario`, `atribuicao`, `reatribuicao`, `liberacao`, `alteracao_chamado`}; `visibilidade` ∈ {`publica`, `interna`} é atributo exclusivo de comentários. Eventos operacionais novos não gravam visibilidade; valores históricos em eventos são ignorados para classificação e autorização.
- **Comentários públicos do Gerente:** `listar_comentarios_publicos_gerente` já exige `tipo_evento` ∈ {`comentario`, nulo, `""`}, `visibilidade == "publica"` e mensagem não vazia. Nada muda nesta change.
- **Autorização:** `autorizacao/obter_identidade` exige perfil oficial; `autorizacao/exigir_perfil` bloqueia troca de senha pendente e aplica a permissão por perfil; `obter_chamado_gerente_autorizado` autoriza pela Loja (404 inexistente, 403 outra Loja).
- **GETs genéricos:** `interacoes_chamado_GET.xs` aceita Gerente (filtro por Loja) e Técnico; `interacoes_chamado_id_GET.xs` lê o registro e depois aplica `exigir_escopo_loja` (Gerente da Loja ou Técnico). Nenhum filtra tipo ou visibilidade. Consumidores: somente testes estáticos; Simulator e Fiscal usam outros endpoints do grupo operacional.
- **Reflex:** `TIPOS_EVENTO_TIMELINE` rejeita tipos desconhecidos; rotas registradas em `app/app.py`; menu no registro central `app/components/navegacao.py`; componentes visuais compartilhados em `app/components/visual.py`.
- **Save:** grava um único `alteracao_chamado` por Save efetivo; mudança de Status registra `alteracoes.status = {anterior, resultante}` somente quando `status` difere do persistido.
- **Transação:** a prova de rollback do Save foi bloqueada por decisão humana em `2026-10-17-tratativa-operacional-chamados` (task 2.3) por ausência de ambiente isolado.

## Goals / Non-Goals

**Goals:**

- Acompanhamento somente leitura do solicitante, autorizado no Xano e sem revelar chamados de terceiros.
- Contrato de leitura do histórico público de status, projetado de `alteracao_chamado`, independente de comentários e da visibilidade, sem nenhuma gravação.
- Remover a leitura de interações pelo Gerente nos GETs genéricos.
- Corrigir a confirmação de publicação de comentário do Gerente.
- Não alterar nenhuma função, endpoint ou tela existente além dos dois GETs genéricos, de `publicar_comentario` e da inclusão da seção de histórico no detalhe do Gerente (K-B).

**Non-Goals:**

- Gravar `alteracao_status`, alterar o enum, o Save ou `TIPOS_EVENTO_TIMELINE`.
- Liberar a exibição do histórico antes da validação exigida por K-B.
- Rejeição de solução, `Reaberto` e qualquer mudança em `Solução Rejeitada`.
- Refatorar funções do Gerente ou do Técnico.
- Qualquer escrita pela interface do solicitante.

## Decisions

### D1. Autorização do solicitante: vínculo no próprio filtro

Função interna `service_desk/obter_chamado_solicitante_autorizado(usuarios_id, chamados_id)`:

1. `autorizacao/exigir_perfil` com os quatro perfis habilitados. Cobre usuário inexistente, perfil não oficial e troca de senha pendente (403), sem consultar chamados.
2. `db.query chamados` com `where id == $input.chamados_id && solicitante_id == $usuario.id`, retorno único. O vínculo integra o filtro: chamado inexistente, chamado de outra pessoa e chamado sem solicitante produzem o mesmo resultado vazio.
3. Resultado vazio → 404 "Recurso não encontrado." em todos os casos. Não existe caminho 403 que confirme a existência do chamado.
4. Defesa em profundidade: `precondition ($registro.solicitante_id != null && $registro.solicitante_id == $usuario.id)`.

A Loja do usuário não é consultada. A identidade vem somente de `$auth.id`; os endpoints recebem `int chamados_id filters=min:1`.

**Alternativa rejeitada:** ampliar `obter_chamado_gerente_autorizado` (mistura escopo por Loja e por vínculo e altera função publicada).

### D2. Contratos do solicitante

Nomes finais confirmados no Apply, sem alterar comportamento:

| Endpoint | Função | Resposta |
|---|---|---|
| `GET /solicitante/chamados` | `listar_chamados_solicitante` | `{items}` com o mesmo DTO de item da lista do Gerente, filtrado por `solicitante_id == $usuario.id`, ordenado por `ultima_atualizacao_em` DESC e `id` DESC, sem filtros, preferências ou paginação |
| `GET /solicitante/chamados/{chamados_id}` | `obter_chamado_solicitante` | `{chamado}` com os campos funcionais do detalhe do Gerente, exceto `resumo_totem = null`, `solicitante` e `tecnico` limitados a `{nome}` (nulos quando ausentes), e sem `sla_horas_aplicado` conforme DE-8 |
| `GET /solicitante/chamados/{chamados_id}/comentarios` | `listar_comentarios_publicos_solicitante` | `{items}` com filtro e DTO idênticos aos de `listar_comentarios_publicos_gerente` |
| `GET /solicitante/chamados/{chamados_id}/historico-status` | `listar_historico_status` (D3) | `{items}` |

Para não alterar funções publicadas do Gerente, as funções do solicitante replicam a projeção do detalhe e o filtro de comentários. Testes estáticos de paridade garantem que filtro e campos permaneçam idênticos.

**Alternativa considerada:** extrair um construtor comum de DTO (precedente `construir_dto_chamado_tecnico`). Mais enxuta, mas modifica funções publicadas e testadas; não adotada nesta Sprint.

### D3. Histórico público de status: projeção de `alteracao_chamado` (H-1)

Fonte: `validar_save_tratativa_chamado` grava, desde sua implantação (`2026-10-17-tratativa-operacional-chamados`), um único `alteracao_chamado` por Save efetivo; quando o Status muda, `alteracoes` contém `status: {anterior, resultante}` além de eventuais `responsavel`, `prioridade`, `categoria`, `sla_horas_aplicado` e `comentario_interacao_id`. O Save não é alterado.

Função interna `service_desk/listar_historico_status(chamados_id)`, somente leitura, sem autorização própria e sem endpoint direto; recebe somente `chamados_id` já autorizado pelo chamador:

- `db.query interacoes_chamado` com `where chamados_id == $input.chamados_id && tipo_evento == "alteracao_chamado"`; nenhum termo de `visibilidade`, inclusive para eventos históricos que armazenam `interna`;
- transição válida: `alteracoes.status` é objeto com `anterior` e `resultante` textuais não vazios e diferentes, e `criado_em` preenchido; demais registros ignorados, sem completar valores nem usar `created_at` como substituto;
- join com `usuarios` projetando somente `nome` e `role`;
- DTO: `id` da interação, `status_anterior`, `status_resultante`, `criado_em`, `autor`;
- `autor`: `{nome, perfil}` com rótulo oficial (`Gerente`, `Técnico`, `Diretoria`, `Administrador`); `{nome: "Sistema", perfil: null}` quando `usuarios_id` é nulo; `{nome, perfil: null}` para usuário existente com perfil nulo ou não oficial; `null` quando `usuarios_id` está preenchido e o usuário não é encontrado;
- ordenação `criado_em` DESC, `id` DESC;
- sem `alteracoes` bruto, demais chaves de `alteracoes`, `usuarios_id`, e-mail, Loja, comentários (inclusive o correlacionado) ou outros eventos;
- nenhum `db.add`, `db.edit`, `db.patch` ou `db.del`.

O filtro de transição válida é aplicado na função após a consulta por chamado e tipo, para não depender de filtro sobre caminho interno de campo `json`; a forma exata é validada no MCP.

Chamadores: `GET /gerente/chamados/{chamados_id}/historico-status` (após `obter_chamado_gerente_autorizado`, inalterado) e o endpoint do solicitante (após D1).

**Cobertura temporal:** somente transições feitas pelo Save desde sua implantação. Criação de chamado e transições anteriores não geram entradas e não são reconstruídas.

**Relação com R1:** a projeção não grava nada e não depende de `alteracao_status` nem de alteração do enum. Ela herda, sem agravar, o risco transacional existente do Save: se uma falha deixasse estado parcial, o histórico refletiria o que foi persistido. H-1 não comprova rollback e não torna o Save transacionalmente seguro.

**Interface (K-B):** seção própria no detalhe do Gerente, liberada somente após a validação de autorização, segurança e contrato dos endpoints de histórico. O endpoint do solicitante permanece disponível no Xano, sem página Reflex própria após a revisão de 10/11/2026.

**Alternativas registradas:** evento próprio `alteracao_status` gravado pelo Save (versão anterior; bloqueado por R1 e substituído por H-1); gravação após o commit com reconciliação (consistência eventual; não adotada).

### D4. GETs genéricos negam o Gerente

- `interacoes_chamado_GET.xs`: `exigir_perfil` somente com `tecnico: true`; remover o ramo do Gerente do filtro.
- `interacoes_chamado_id_GET.xs`: autorizar somente Técnico **antes** do `db.get`, eliminando leitura antes da autorização.
- Diretoria e Administrador permanecem negados, como hoje; Técnico mantém o comportamento atual.

Negar em vez de filtrar: não há consumidor e os contratos funcionais cobrem a leitura pública com DTO sanitizado.

### D5. Reflex

- Cliente: manter métodos e DTOs já testados dos contratos publicados do solicitante, além do histórico do Gerente. Os contratos de solicitante continuam no Xano e são validados por testes HTTP, sem página Reflex consumidora nesta Sprint.
- Remover `ChamadosSolicitanteState`, páginas em `app/chamados/solicitante/`, rotas `/chamados/solicitados**`, item "Chamados solicitados" e gate local de publicação da interface. Preservar a composição e as consultas da página `/inicio` de cada perfil.
- `publicar_comentario`: POST e recarga do detalhe em tratamentos separados.
- Sem alteração em `TIPOS_EVENTO_TIMELINE`, `_evento_timeline` ou páginas do Técnico; o detalhe do Gerente recebe somente a seção de histórico, sem novas ações.

### D6. Segurança transacional (E0.3)

| Classe | Conteúdo |
|---|---|
| Documentado (fornecedor, divergente) | A referência oficial ([Database Transaction](https://docs.xano.com/the-function-stack/functions/database-requests/database-transaction)) afirma que somente operações de banco são consideradas para decidir o rollback e que outras funções podem falhar sem afetar a transação; o guia [Xano Learn](https://www.xano.com/learn/database-transaction/) afirma que qualquer falha, inclusive `precondition`, desfaz toda a transação. A documentação XanoScript do Developer MCP (2.2.6) descreve atomicidade e níveis de `isolation`, sem tratar `precondition` ou `throw` |
| Observado | Parser aceita `db.transaction`, mas rejeitou `isolation` (`2026-09-24-chamados-fila-atribuicao-tecnica`); `db.direct_query` indisponível no Free; o Save grava e depois verifica por `precondition`; mocks de falha; conflito otimista real sem efeito parcial ocorre antes das escritas e não prova rollback |
| Inferido | Comentário em `assumir_chamado_tecnico` e troca de `error_type` sugerem expectativa de rollback, sem evidência anexada |
| Desconhecido | Rollback runtime após escrita seguida de `precondition`, `throw` ou erro em `function.run`; isolamento; concorrência; influência de `error_type` |

O plano de prova previa datasource próprio de teste no workspace `152692`, branch `v1`, sem registros reais e sem torná-lo ativo. A API do Xano recusou a publicação do `workflow_test` temporário com `Please upgrade to access workflow tests`; a prova de rollback em runtime ficou **bloqueada por restrição do plano Free**. Em 2026-11-08 a responsável aceitou formalmente essa limitação para prosseguir sem upgrade pago. Os experimentos planejados e o rollback não foram executados; concorrência também permanece desconhecida. Esta decisão não transforma análise estática em prova de rollback e não libera R1 por inferência. Detalhes: [plano-execucao-rollback.md](../rejeicao-solucao-gerente/prova-e03/plano-execucao-rollback.md).

## Risks / Trade-offs

- [Revelar existência de chamado de terceiro] → vínculo no filtro e 404 uniforme (D1).
- [Divergência futura entre projeções do Gerente e do solicitante] → testes de paridade.
- [Formato de `alteracoes` divergente em registros existentes] → transição válida definida estritamente; registros malformados são ignorados e testados (D3).
- [Vazamento das demais chaves de `alteracao_chamado`] → DTO fechado e testes com `alteracao_chamado` que altera status, responsável, prioridade, Categoria e SLA no mesmo evento.
- [Vazamento de comentário interno ou evento operacional] → testes com comentário interno, comentário correlacionado e atribuição no mesmo chamado.
- [Estado parcial herdado do Save] → risco existente e não agravado; R1 permanece bloqueado e o plano E0.3 permanece pendente.
- [Branch defasada reverter recursos publicados] → dry-run e push somente a partir de branch atualizada.
- [Ambiente Windows] → `rx.asset(shared=True)` exige symlink e testes que usam `read_text()` sem codificação falham; executar a suíte em ambiente com permissão de symlink e registrar bloqueio de ambiente quando não houver.
- [Histórico incompleto] → limitação registrada: transições anteriores à implantação do Save e a criação do chamado não aparecem.
- [Identificadores de usuário no detalhe do solicitante] → `solicitante` e `tecnico` somente com `nome` (D2).

## Migration Plan

| # | Etapa | Gate |
|---|---|---|
| 1 | Aprovar o Apply | Humano |
| 2 | Xano: GETs genéricos (D4) | — |
| 3 | Xano: `obter_chamado_solicitante_autorizado`, contratos do solicitante e `listar_historico_status` com endpoints (D1–D3); validação MCP em sessão com o MCP disponível | Parar se a validação de D3 falhar |
| 4 | Dry-run seletivo e revisão do diff | Aprovação do push |
| 5 | Push seletivo e novo dry-run sem diferenças não aprovadas | — |
| 6 | Reflex (D5) | — |
| 7 | Validação integrada e classificação dos resultados | Aceite de limitações |
| 8 | Conferência documental, revisão independente e Archive | Humano |

Sem schema, sem backfill, sem migração. Reversão futura dos contratos Xano exigiria decisão humana própria; a revisão de interface de 10/11/2026 não apaga endpoints publicados. Restaurar os GETs genéricos somente por decisão humana.
