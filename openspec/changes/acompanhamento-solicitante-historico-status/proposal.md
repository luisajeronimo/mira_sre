# Proposal

## Why

A equipe revisou formalmente o escopo da Sprint 3 ("Acompanhamento e retorno do solicitante"). Permanecem nesta change: o acompanhamento, somente leitura, dos chamados pelo solicitante associado; o histórico público de status como funcionalidade independente, projetado do evento operacional já gravado pelo Save; a correção da exposição de interações pelos GETs genéricos; e correções pontuais da jornada do Gerente. A rejeição de solução foi retirada do escopo e adiada para Sprint futura. A gravação de novos eventos de status permanece bloqueada (R1) até existir estratégia transacional comprovadamente segura no Xano.

Estado verificado em `06cc763` (branch atualizada com `origin/main`, recursos correspondentes já publicados no Xano):

- não existe contrato próprio do solicitante: um solicitante transferido de Loja perde o acesso ao chamado que abriu, e um solicitante que não é Gerente não tem acompanhamento;
- não existe histórico público de status; desde a implantação do Save operacional, cada mudança efetiva de status fica registrada em `alteracao_chamado` com `alteracoes.status = {anterior, resultante}`, fato operacional exibido apenas na timeline técnica;
- a visibilidade Público/Interno pertence exclusivamente a comentários; eventos operacionais novos não a gravam (`2026-11-02-corrigir-visibilidade-comentarios-filtros-multiplos`);
- `GET /interacoes_chamado` e `GET /interacoes_chamado/{id}` (grupo genérico) atendem o Gerente pelo escopo da Loja e retornam comentários internos e eventos operacionais por acesso direto; nenhum código Reflex, Simulator ou Fiscal os consome;
- `publicar_comentario` trata o POST e a recarga posterior do detalhe no mesmo bloco de erro;
- a spec `frontend-chamados-gerente` ainda afirma que o Gerente não comenta em chamado terminal, embora o comportamento implementado (`a61f426`) e o contrato Xano o permitam.

## What Changes

- **Acompanhamento do solicitante, somente leitura:** contratos Xano próprios de lista, detalhe e comentários públicos dos chamados em que o usuário é o solicitante associado; interface Reflex em `/chamados/solicitados` e `/chamados/solicitados/[chamado_id]`; item de menu "Chamados solicitados" para os quatro perfis oficiais.
- **Autorização do solicitante:** cumulativamente autenticação válida, troca de senha não pendente, um dos quatro perfis oficiais, `solicitante_id` não nulo e igual à identidade autenticada. Independe da Loja atual. Chamado inexistente e chamado de outra pessoa recebem a mesma resposta de recurso não encontrado.
- **Histórico público de status (somente leitura, decisão H-1):** contratos do Gerente e do solicitante que projetam, das interações `alteracao_chamado` do chamado autorizado, somente as transições válidas de status (par anterior/resultante, momento e autor sanitizado), sem usar `visibilidade` e sem gravar nada. Interações sem transição de status são ignoradas; sem transições, a resposta é lista vazia. Transições anteriores à implantação do Save não são reconstruídas.
- **Segurança:** os GETs genéricos de `interacoes_chamado` deixam de atender o Gerente; demais perfis preservados.
- **Gerente:** confirmação de publicação de comentário independente da recarga do detalhe; spec do comentário em chamado terminal alinhada ao implementado.
- **Documentos de domínio:** separam o implementado, o aprovado nesta Sprint, o adiado e o bloqueado.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-acompanhamento-gerente`: histórico público projetado de `alteracao_chamado` (leitura) para Gerente e solicitante; consulta do solicitante; visibilidade restrita a comentários na regra de falha fechada; segurança dos contratos de comentários por contrato; título do requisito de comentário.
- `autorizacao-perfis`: autorização do solicitante pelo vínculo com perfil oficial; GETs genéricos de interações negam o Gerente.
- `frontend-chamados-gerente`: interface somente leitura do solicitante; confirmação de publicação; comentário em chamado terminal.
- `navegacao-lateral-perfis`: item "Chamados solicitados" para os quatro perfis oficiais.
- `frontend-sessao-navegacao`: proteção e resolução estática das rotas do solicitante.

## Perfis

| Perfil | Efeito |
|---|---|
| Gerente | Perde acesso aos GETs genéricos de interações; ganha o histórico projetado no detalhe (interface liberada somente após a validação exigida por K-B); como solicitante, usa também a interface própria |
| Técnico, Diretoria, Administrador | Sem mudança na fila, tratativa, Save ou timeline; acessam a interface do solicitante somente para chamados em que são o solicitante |
| Solicitante (qualquer perfil oficial) | Acompanhamento somente leitura dos chamados associados |

## Entregas

1. Xano: GETs genéricos de interações sem acesso do Gerente.
2. Xano: contratos do solicitante (lista, detalhe, comentários públicos, histórico projetado) e do histórico projetado do Gerente.
3. Reflex: cliente e DTOs dos contratos do solicitante; State e páginas somente leitura; rotas; item de menu.
4. Reflex: correção de `publicar_comentario`.
5. Reflex: seção de histórico público no detalhe do Gerente e do solicitante, liberada somente após a validação de autorização, segurança e contrato (K-B).

Ordem de segurança: a entrega 1 (GETs genéricos) é prioritária e independente das demais, porque hoje o Gerente consegue ler comentários internos por acesso direto.

## Critérios de aceite

- Cada cenário das specs delta possui teste rastreável (XanoScript, estático ou Python).
- O histórico retorna somente transições válidas projetadas de `alteracao_chamado`, sem `alteracoes` bruto nem suas demais chaves, sem filtro por `visibilidade`, ordenadas por `criado_em` e `id` decrescentes, e lista vazia quando não houver transições.
- Os contratos de histórico não criam, alteram nem gravam interações.
- Nenhum contrato acessível ao Gerente ou ao solicitante retorna comentário interno, evento operacional além do par de status projetado, e-mail, identificadores de usuário ou telemetria indevida.
- Os contratos do solicitante não distinguem chamado inexistente de chamado de outra pessoa; o detalhe do solicitante não expõe identificador de solicitante nem de técnico.
- Nenhum recurso de escrita grava `alteracao_status`; `validar_save_tratativa_chamado`, a tabela `interacoes_chamado` e `TIPOS_EVENTO_TIMELINE` permanecem inalterados.
- `Solução Rejeitada`, listas canônicas, filtros múltiplos, preferências, fila técnica e autenticação permanecem inalterados.
- `openspec validate --strict`, `reflex compile --dry` e `git diff --check` passam; resultados runtime são classificados conforme o `AGENTS.md`.

## Fora do escopo

- **Em outra change:** rejeição de solução pelo Gerente da Loja, com destino `Solução Rejeitada` (`rejeicao-solucao-gerente`, Sprint 3, condicionada à prova E0.3 — DR2-0 e DT-1); SLA e encerramento automático (`sla-resolucao-encerramento`). `Reaberto` não será criado. A versão anterior desta change, com `Reaberto`, está preservada, inativa, em [no histórico Git (commit `1f27556`, pasta `referencias/rejeicao-solucao-versao-anterior/`, removida da árvore em 2026-11-08)](no histórico Git (commit `1f27556`, pasta `referencias/rejeicao-solucao-versao-anterior/`, removida da árvore em 2026-11-08)README.md).
- **Bloqueado (R1, segurança transacional):** gravação de `alteracao_status` pelo Save ou por qualquer outro fluxo; valor `alteracao_status` no enum; aceitação do tipo em `TIPOS_EVENTO_TIMELINE`. H-1 não depende dessa gravação e não comprova rollback nem segurança transacional do Save.
- **Liberação condicionada (K-B):** a seção de histórico na interface é planejada nesta change, mas só é liberada depois de validados autorização, segurança e contrato dos endpoints de histórico (tasks 4 e 5.6).
- **Não incluído:** comentário, rejeição, aceitação ou qualquer escrita pela interface do solicitante; filtros, preferências ou paginação na lista do solicitante; telemetria ao solicitante; cálculo de SLA; encerramento automático; alteração dos GETs genéricos para Técnico, Diretoria ou Administrador.

## Decisões aprovadas

1. Acompanhamento do solicitante exclusivamente somente leitura.
2. Histórico público de status independente da rejeição.
3. ~~Rejeição de solução adiada~~ — substituída por DR2-0 (abaixo). Permanece: preservar integralmente `Solução Rejeitada`, suas listagens, preferências e comportamento de Save; não criar `Reaberto`.
4. Gravação de `alteracao_status` bloqueada; nenhum fluxo pode contorná-la; liberação somente após demonstração verificável de segurança transacional e nova autorização humana.
5. ~~Histórico não exibido na interface enquanto o bloqueio R1 vigorar~~ — substituída por K-B (abaixo).
6. Eventos operacionais não possuem visibilidade; a exposição decorre do tipo do evento e do contrato autorizado.
7. Gerente autorizado conforme contrato e escopo de Loja; solicitante por autenticação, perfil oficial e vínculo `solicitante_id`, independente da Loja atual.
8. Lista do solicitante ordenada por `ultima_atualizacao_em` DESC e `id` DESC, sem filtros, preferências ou paginação.
9. Detalhe do solicitante com `resumo_totem = null`, sem drawer, e sem expor `solicitante.id`.
10. Menu "Chamados solicitados" para os quatro perfis oficiais, sem que a visibilidade conceda autorização; deltas de `navegacao-lateral-perfis` e `frontend-sessao-navegacao` incluídos.
11. Spec do comentário do Gerente em chamado terminal alinhada ao comportamento implementado.
12. Autor no histórico: `{nome, perfil}` com rótulo oficial; `Sistema` sem usuário; `{nome, perfil: null}` para perfil não reconhecido; `null` para usuário não encontrado.
13. **H-1:** o histórico público de status é projetado de `alteracao_chamado`, somente para transições válidas de status. Substitui a decisão anterior que proibia derivar o histórico da auditoria e a previsão de um evento próprio `alteracao_status` para leitura.

### Decisões aprovadas em 2026-11-04 (replanejamento da Sprint 3)

| ID | Decisão | Efeito nesta change |
|---|---|---|
| DR2-0 | Rejeição de solução incluída na Sprint 3, condicionada à segurança | Substitui a decisão 3 quanto ao adiamento; a operação fica em `rejeicao-solucao-gerente` |
| DT-1 | Prova E0.3 obrigatória antes de novas escritas que dependam de atomicidade | Nenhuma escrita nova nesta change; R1 (decisão 4) permanece |
| DS-1 | SLA em tempo corrido | Sem efeito nesta change |
| DR2-1 | Somente o Gerente da própria Loja rejeita; o solicitante permanece somente leitura | Confirma a decisão 1 |
| DR2-2 | `Solução Rejeitada` permanece canônico | Confirma a decisão 3 quanto aos status |
| K-B | Histórico exibido na interface após validação | Substitui a decisão 5; entrega 5 e tasks 5.6–5.8 |
| DE-1, DE-2, DE-3 | Encerramento automático: 72 h corridas, sem encerramento em massa de chamados já resolvidos, comentário público de sistema | Sem efeito nesta change (`sla-resolucao-encerramento`); comentários de sistema aparecem no histórico de comentários com `autor` conforme o DTO público vigente |

### Consolidação documental desta revisão

- Pela mesma regra de mínimo necessário da decisão 9, o detalhe do solicitante também expõe `tecnico` somente com `nome`, sem identificador de usuário. O detalhe do Gerente permanece inalterado.

## Comportamentos existentes a preservar

- Lista, detalhe, filtros múltiplos, preferências e comentários do Gerente pela Loja persistida (chamado → Totem → Loja).
- Comentário do Gerente sempre Público, inclusive em `Encerrado` e `Cancelado`.
- Save exclusivo de Técnico, Diretoria e Administrador, com a lista canônica vigente (incluindo `Solução Rejeitada`) e um único `alteracao_chamado` sem visibilidade; o histórico apenas lê esse registro.
- Timeline técnica, fila global, filtros múltiplos e preferências dos perfis globais.
- Mutações genéricas negadas por `autorizacao/negar_mutacao_generica`; Técnico mantém os GETs genéricos de interações.
- Autenticação, troca obrigatória de senha e casca visual vigentes.

## Gates

- Aprovação formal do Apply.
- Validação XanoScript no Xano Developer MCP das funções novas, inclusive da leitura de `alteracoes.status` em campo `json` (ver design D3), em sessão com o MCP disponível.
- Dry-run e push seletivos somente a partir da branch atualizada com `origin/main`, com aprovação explícita do diff.
- O bloqueio R1 só é reavaliado com o relatório do plano de prova E0.3 e nova decisão humana.
