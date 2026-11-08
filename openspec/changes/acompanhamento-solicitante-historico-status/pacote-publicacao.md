# Pacote seletivo de publicação

Preparado em 07/11/2026 na branch `explore-monitoramento-xano` (base `06cc763`, sem commit). Publicar exige autorização explícita (AGENTS.md, seção Xano). Destino: workspace `152692`, branch `v1` (live).

Situação: **Pacote A publicado em 07/11/2026** (seção [Publicação do Pacote A](#publicação-do-pacote-a-2026-11-07)). **Pacote B publicado em 07/11/2026** (seção [Publicação do Pacote B](#publicação-do-pacote-b-2026-11-07)).

## Pacote A — correção de segurança (prioridade 1)

Motivação original: o `HEAD` (`06cc763`) concede `gerente: true` nos dois GETs. Correção de 07/11/2026: a versão então publicada já negava o Gerente (comparação somente leitura com `xano workspace pull`); o pacote endurece a autorização (antes de qualquer leitura), corrige o 500 do id inexistente e alinha repositório e publicado.

| Arquivo | Operação | Dependências (já publicadas) |
|---|---|---|
| `api/apis_from_table_interacoes_chamado/interacoes_chamado_GET.xs` | UPDATE | `autorizacao/exigir_perfil` → `autorizacao/obter_identidade` |
| `api/apis_from_table_interacoes_chamado/interacoes_chamado/interacoes_chamado_id_GET.xs` | UPDATE | idem |

Evidências antes da publicação:

| Categoria | Resultado |
|---|---|
| Teste local (contrato estático) | `tests/test_interacoes_genericas_seguranca.py`: 15/15. Contra a versão do `HEAD` (`06cc763`, diferente da publicada): 5 falhas, todas de autorização (mutação detectada) |
| Validação estática MCP | Válidos |
| Dry-run (07/11) | `~2 updated`, nenhuma outra diferença; arquivos locais inalterados |
| Teste de runtime | Não executado |
| Publicação | Não executada |

Comportamento esperado após a publicação: Técnico mantém a lista e o detalhe brutos de antes; Gerente, Diretoria e Administrador recebem 403 antes de qualquer leitura; nenhum consumidor do MIRA usa esses endpoints (o Reflex usa os contratos funcionais).

## Publicação do Pacote A (2026-11-07)

Autorização específica da responsável pelo projeto, restrita aos dois arquivos, ao plano Free e às condições abaixo.

| Item | Registro |
|---|---|
| Data e horário | 2026-11-07, dry-run às 17:41:10 e push às 17:41:31 (-03:00) |
| Destino | Workspace `152692`, branch `v1` (live), instância `x8ki-letl-twmt.n7.xano.io` |
| Endpoints publicados | `GET interacoes_chamado` e `GET interacoes_chamado/{interacoes_chamado_id}` (grupo "APIS from table interacoes_chamado") |
| Comando | `xano workspace push --force --no-guids --no-fast -d xano -w 152692 -b v1` com somente os dois `-i`; sem `--sync`, `--delete` ou `--records`. `--force` só suprimiu o prompt interativo, indisponível no terminal usado; a prévia foi o dry-run 21 s antes |
| Ajuste prévio autorizado | Remoção do filtro redundante `where = $usuario.role == "tecnico"` da listagem (padrão publicado de `categorias_servico_GET`) e ajuste correspondente de `test_tecnico_preserva_lista_completa_e_resposta_bruta` |
| Hashes SHA-256 locais | `interacoes_chamado_GET.xs` `bec93359350353beaa4effbf10c08d93df15c877bf396398e8340079c708b7cb`; `interacoes_chamado_id_GET.xs` `e9551da25ea73ab16554c9f4ebdccaf4a9aaa75172add0cd4c938ce37776be1d`. Iguais antes e depois do push; os 121 arquivos de `xano/` inalterados; nenhum GUID gravado; nenhum `.xano/` criado |

Evidências por categoria:

| Categoria | Resultado |
|---|---|
| Teste local | Suíte completa 606/606; `tests/test_interacoes_genericas_seguranca.py` 15/15; `git diff --check` sem problemas |
| Validação estática MCP | 2/2 válidos; `xano/` 121/121 |
| Dry-run antes do push | 2 de 121 arquivos; `~2 updated` (`UPDATE query interacoes_chamado/{interacoes_chamado_id} GET`, `UPDATE query interacoes_chamado GET`); nenhuma criação, exclusão ou registro |
| Publicação | `Pushed 2 documents to workspace 152692 from xano in 1.5s`; código de saída 0 |
| Escopo no workspace | `pull` somente leitura das 17:16 comparado ao de depois do push: somente os dois documentos diferem; nenhum documento de terceiros alterado |
| Dry-run depois do push | `No changes to push` |
| Teste de runtime (HTTP) | Tabela abaixo |
| Teste de persistência/rollback | Não se aplica (endpoints somente leitura) |

Aviso do CLI durante o push: "Unresolved References" informou que `function "autorizacao/exigir_perfil"` e `table "interacoes_chamado"` "não existem" e virariam placeholders. Investigação, somente leitura: (a) o `pull` posterior mostra os dois endpoints com `function.run "autorizacao/exigir_perfil"`, `db.query` e `db.get` íntegros, sem placeholders; (b) o comportamento HTTP confirma a execução da autorização (403 para Gerente, Diretoria e Administrador) e das consultas. Interpretação: verificação do lado do CLI limitada aos documentos do push parcial; sem impacto observado no servidor.

### Testes HTTP (contas de teste fornecidas pela responsável; sem senha ou token registrados)

| Perfil | Teste | Antes (versão anterior publicada) | Depois (Pacote A) | Situação |
|---|---|---|---|---|
| Técnico | Listagem | 200, 28 itens | 200, 28 itens | APROVADO |
| Técnico | Detalhe existente | 200, mesmo id (120) | 200, mesmo id (107) | APROVADO |
| Técnico | Id inexistente (999999999) | **500** "Unable to locate var: interacoes_chamado.chamados_id" | 404 "Not Found." | APROVADO |
| Técnico | Id zero | 400 | 400 | APROVADO |
| Gerente | Listagem | 403 | 403 | APROVADO |
| Gerente | Detalhe existente | 403 | 403 | APROVADO |
| Gerente | Id inexistente | **500** (mesmo erro) | 403 | APROVADO |
| Diretoria | Listagem e detalhe | 403 | 403 | APROVADO |
| Administrador | Listagem e detalhe | 403 | 403 | APROVADO |
| Sem token | Listagem | 401 | 401 | APROVADO |
| Troca de senha pendente | Listagem e detalhe | — | — | NÃO EXECUTADO: sem conta de teste; contas não foram alteradas para simular |
| Gerente | Interação pública e interna da própria Loja | — | — | NÃO EXECUTADO: os endpoints do pacote não permitem identificar a Loja da interação |

Limitações da listagem do Técnico:

- A quantidade (28) é igual antes e depois. **Não se afirma que sejam os mesmos 28 registros**: os ids individuais não foram registrados antes do push e não houve comparação item a item.
- A ordem mudou: o primeiro item passou de 120 para 107 (a consulta não define ordenação; a versão anterior usava joins).
- Composição **parcialmente confirmada** nas duas execuções (antes e depois da publicação): 13 itens com `visibilidade = "interna"` e 13 com `tipo_evento` diferente de comentário, critérios independentes que podem se sobrepor. Medição posterior (tasks 2.2/2.3, mesmo dia) classificou os 28 itens em 14 comentários públicos, 1 comentário não público e 13 eventos operacionais; como no máximo 1 dos 13 itens com `visibilidade = "interna"` é comentário, pelo menos 12 eventos operacionais têm essa visibilidade armazenada. Essa medição não compara ids com a versão anterior à publicação.

## Pacote B — contratos do solicitante e do histórico

Pode ser publicado junto com A ou depois. Não depende de schema novo nem de backfill.

| Tipo | Itens | Dependências (já publicadas) |
|---|---|---|
| Funções (+7) | `obter_chamado_solicitante_autorizado`, `listar_chamados_solicitante`, `obter_chamado_solicitante`, `listar_comentarios_publicos_solicitante`, `listar_historico_status`, `listar_historico_status_gerente`, `listar_historico_status_solicitante` | `autorizacao/exigir_perfil`, `service_desk/obter_chamado_gerente_autorizado`; tabelas `chamados`, `interacoes_chamado`, `usuarios`, `ativos_referencia`, `lojas`, `categorias_servico` |
| Endpoints (+5) | `GET solicitante/chamados`, `GET solicitante/chamados/{id}`, `GET solicitante/chamados/{id}/comentarios`, `GET solicitante/chamados/{id}/historico-status`, `GET gerente/chamados/{id}/historico-status` | funções acima |

Evidências antes da publicação:

| Categoria | Resultado |
|---|---|
| Teste local (contrato estático) | `tests/test_contratos_solicitante_historico.py` (35 testes) |
| Teste com mock (cliente/State Reflex) | `tests/test_solicitante_historico_reflex.py` |
| Validação estática MCP | Válidos |
| Dry-run (07/11) | `+7` funções e `+5` endpoints criados; nenhuma outra diferença |
| Blocos `test` XanoScript (mocks) | Escritos; **não executados** (exigem runtime) |
| Teste de runtime / HTTP | Não executado |
| Publicação | Não executada |

## Publicação do Pacote B (2026-11-07)

Autorização da responsável pelo projeto: publicação seletiva dos documentos seguros do Pacote B, no plano Free, preservando o histórico de vínculo Totem–Loja e a regra de Loja histórica.

| Item | Registro |
|---|---|
| Data e horário | 2026-11-07, dry-run às 19:19:24 e push às 19:19:40 (-03:00) |
| Destino | Workspace `152692`, branch `v1` (live) |
| Comando | `xano workspace push --force --no-guids --no-fast -d xano -w 152692 -b v1` com somente os 12 `-i` do pacote; sem `--sync`, `--delete` ou `--records`. `--force` só suprimiu o prompt interativo; a prévia foi o dry-run 16 s antes |
| Publicado | Funções `obter_chamado_solicitante_autorizado`, `listar_chamados_solicitante`, `obter_chamado_solicitante`, `listar_comentarios_publicos_solicitante`, `listar_historico_status`, `listar_historico_status_gerente`, `listar_historico_status_solicitante`; endpoints `GET solicitante/chamados`, `GET solicitante/chamados/{chamados_id}`, `GET solicitante/chamados/{chamados_id}/comentarios`, `GET solicitante/chamados/{chamados_id}/historico-status`, `GET gerente/chamados/{chamados_id}/historico-status` |
| Não publicado | `calcular_consumo_sla_chamado.xs` (DE-8), pacote da prova E0.3 e qualquer outro documento |

Reconciliação com o publicado antes do push (`xano workspace pull` somente leitura):

- O publicado autoriza e exibe o Gerente pela Loja **histórica** do Totem (`administracao/resolver_loja_totem_no_instante`, existente só no Xano). `obter_chamado_solicitante` passou a calcular `loja` da mesma forma (Totem e `criado_em` do chamado; `null` sem vínculo histórico), sem o join pela Loja atual. Novo teste de contrato: `test_detalhe_do_solicitante_usa_loja_historica_como_o_gerente_publicado`.
- `listar_historico_status_gerente` usa o `obter_chamado_gerente_autorizado` publicado (Loja histórica); assinatura e resposta compatíveis.
- O item da lista publicada do Gerente tem os mesmos campos do item da lista do solicitante; sem ajuste.
- Todos os 12 documentos eram **novos** (somente CREATE): nenhum documento existente podia ser sobrescrito.

Evidências por categoria:

| Categoria | Resultado |
|---|---|
| Teste local | Suíte 607 passaram e 21 pulados (E2E sem variáveis); contratos do solicitante e histórico 35/35 |
| Validação estática MCP | `obter_chamado_solicitante.xs` válido; `xano/` 121/121 |
| Dry-run antes do push | 12 de 121 arquivos; `+7` funções e `+5` endpoints **criados**; nenhuma atualização ou exclusão |
| Publicação | `Pushed 12 documents to workspace 152692 from xano in 3.7s`; código de saída 0 |
| Escopo no workspace | `pull` antes (130 documentos) e depois (142): somente os 12 novos; nenhum documento existente alterado; referências dos novos íntegras, sem placeholders |
| Dry-run depois do push | `No changes to push` |
| Arquivos locais | 121 arquivos de `xano/` com SHA-256 iguais antes e depois; nenhum GUID gravado; nenhum `.xano/` |
| Testes nativos XanoScript (runtime, com mocks) | 14/14 PASS: `listar_chamados_solicitante` (2), `listar_comentarios_publicos_solicitante` (2), `listar_historico_status` (3), `listar_historico_status_gerente` (1), `listar_historico_status_solicitante` (1), `obter_chamado_solicitante` (2), `obter_chamado_solicitante_autorizado` (3) |
| Teste de runtime (HTTP) | Tabela abaixo (`tests/test_e2e_pacote_b.py`) |

O CLI repetiu o aviso "Unresolved References" (funções e tabelas existentes apontadas como inexistentes); o `pull` posterior e os testes nativos e HTTP confirmaram que as referências foram resolvidas no servidor, como no Pacote A.

### Testes HTTP (contas de teste da responsável; sem senha ou token registrados)

| Teste | Resultado |
|---|---|
| `GET solicitante/chamados` com Técnico, Gerente, Diretoria e Administrador | 200 para os quatro; envelope `{items}`, item com exatamente os campos contratados e ordem por `ultima_atualizacao_em` e `id` decrescentes. PASSOU (4) |
| Detalhe, comentários e histórico de chamado do próprio solicitante | PULADO (não executado): nenhuma das quatro contas é solicitante de chamado |
| Chamado de outra pessoa e chamado inexistente nos três endpoints `solicitante/chamados/{id}` | 404 em todos, sem conteúdo do chamado. PASSOU (3). Uma execução falhou por erro de DNS da máquina local (`getaddrinfo failed`), não do endpoint; a repetição passou |
| `GET gerente/chamados/{id}/historico-status`: Gerente em chamado de outra Loja, Técnico no contrato do Gerente, Gerente em id inexistente | 403, 403 e 404. PASSOU |
| `GET solicitante/chamados` sem token | 401. PASSOU |

Pendências de validação: detalhe, comentários e histórico de um chamado do próprio solicitante, e histórico do Gerente em chamado da própria Loja. As contas de teste não têm chamados solicitados e a Loja do Gerente de teste não tem chamados; os dados não foram criados. A interface Reflex continua desligada (`MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO` não foi alterada).

**Fora dos pacotes:** `calcular_consumo_sla_chamado.xs` (interna, sem chamador; exposição depende de DE-8) e o pacote da prova E0.3 (`rejeicao-solucao-gerente/prova-e03/`, que nunca deve ir ao workspace compartilhado).

## Execução (somente após autorização)

```bash
# A (publicado em 2026-11-07; registro acima)
xano workspace push --dry-run --no-guids --no-fast -d xano -w 152692 -b v1 \
  -i "api/apis_from_table_interacoes_chamado/interacoes_chamado_GET.xs" \
  -i "api/apis_from_table_interacoes_chamado/interacoes_chamado/interacoes_chamado_id_GET.xs"
# revisar: exatamente ~2 updated; então repetir sem --dry-run

# B
xano workspace push --dry-run --no-guids --no-fast -d xano -w 152692 -b v1 \
  -i "function/service_desk/listar_chamados_solicitante.xs" \
  -i "function/service_desk/listar_comentarios_publicos_solicitante.xs" \
  -i "function/service_desk/listar_historico_status*.xs" \
  -i "function/service_desk/obter_chamado_solicitante*.xs" \
  -i "api/mira_service_desk/solicitante/**" \
  -i "api/mira_service_desk/gerente/chamados/chamados_id_historico-status_GET.xs"
# revisar: exatamente +7 funções e +5 endpoints; então repetir sem --dry-run
```

Sem `--sync`, `--delete`, `--records` ou `--truncate`. A decisão sobre `--no-guids` (não gravar GUIDs do servidor nos arquivos) fica com quem publicar.

## Validação após a publicação

1. Repetir os dois dry-runs: nenhuma diferença pendente.
2. `xano unit_test list -w 152692` e `xano unit_test run <id>` para os testes das 7 funções e dos 2 GETs; registrar PASS/FAIL (task 6.2).
3. HTTP com usuários de teste autorizados (task 6.6): Gerente → 403 nos dois GETs genéricos; Técnico → resultado anterior; solicitante → somente os próprios chamados, e 404 igual para inexistente e de outra pessoa; histórico sem `alteracoes` bruto nem ids.
4. Somente depois disso: `MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO=true` no `.env` do ambiente que servirá o Reflex (gate K-B, task 5.8).

## Reversão

- A: republicar os dois arquivos da versão `06cc763` (`git show 06cc763:<arquivo>`), somente por decisão humana, porque reabre a exposição.
- B: manter `MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO` desligado; desativar os endpoints novos no Xano. Não há dados gravados a desfazer.
