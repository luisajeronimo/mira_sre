# Inventário dos endpoints acessíveis ao Gerente (task 2.4)

Revisão estática de `xano/api/**` e das funções chamadas, na branch `explore-monitoramento-xano` (base `06cc763`), em 2026-11-04. Não houve consulta ao runtime Xano.

Critério: endpoint com `auth = "usuarios"` cujo gate aceita `role = "gerente"` (`exigir_perfil` com `gerente: true`, `exigir_escopo_loja` ou função funcional do Gerente). Mutações genéricas (`POST`/`PATCH`/`DELETE` em `apis_from_table_*`) são negadas por `autorizacao/negar_mutacao_generica` e não constam da tabela.

## Contratos funcionais (`MIRA Service Desk`)

| Endpoint | Autorização e escopo | Campos retornados | Interações | Risco |
|---|---|---|---|---|
| `GET gerente/chamados` | `exigir_perfil(gerente)` + Loja da sessão | Item: id, título, descrição, status, prioridade, origem, datas, ativo, categoria | Não | Nenhum identificado |
| `GET gerente/chamados/{id}` | `exigir_perfil(gerente)` + Loja (404 inexistente, 403 outra Loja) | Detalhe com `solicitante {id, nome}`, `tecnico {id, nome}`, `resumo_totem` com telemetria | Não | 403/404 distingue existência entre Lojas (comportamento consolidado) |
| `GET gerente/chamados/{id}/comentarios` | `obter_chamado_gerente_autorizado` | `id`, `conteudo`, `criado_em`, `autor {nome}` | Somente comentários `publica` com tipo comentário/legado | Nenhum identificado |
| `POST gerente/chamados/{id}/comentarios` | `obter_chamado_gerente_autorizado` | DTO sanitizado do comentário criado | Cria somente Público | Nenhum identificado |
| `GET/PUT gerente/preferencias-fila` | `exigir_perfil(gerente)`; dono autenticado | Preferência da Loja | Não | Nenhum identificado |
| `GET gerente/ativos`, `GET gerente/categorias` | `exigir_perfil(gerente)` + Loja / catálogo manual | Totens da Loja; categorias manuais | Não | Nenhum identificado |
| `POST gerente/chamados` | `exigir_perfil(gerente)` + Loja do Totem | Chamado criado | Não | Fora do escopo desta revisão |
| `GET gerente/chamados/{id}/historico-status` *(novo, local)* | `obter_chamado_gerente_autorizado` | Par de status, momento e autor sanitizado | Projeção de `alteracao_chamado` | Pendente de validação runtime |
| `GET solicitante/**` *(novos, local)* | Vínculo `solicitante_id` + perfil oficial; 404 uniforme | Ver specs delta | Somente comentários públicos e projeção de status | Pendente de validação runtime |

`GET tecnico/**`, `GET monitoramento/**` e a timeline técnica (`obter_chamado_tecnico`) negam o Gerente.

## Consultas genéricas (`APIS from table *`)

| Endpoint | Autorização e escopo do Gerente | Retorno | Interações | Risco |
|---|---|---|---|---|
| `GET interacoes_chamado` | **Negado** após a correção local (somente Técnico) | — | — | **Exposição ativa no ambiente publicado até o push** |
| `GET interacoes_chamado/{id}` | **Negado** após a correção local, antes de qualquer leitura | — | — | **Exposição ativa no ambiente publicado até o push** |
| `GET chamados` | `exigir_perfil(gerente)` + Loja | Registro bruto do chamado | Não | Registro bruto inclui identificadores (`solicitante_id`, `tecnico_id`); sem dado de interação |
| `GET chamados/{id}` | Lê o registro e depois `exigir_escopo_loja` | Registro bruto | Não | Leitura antes da autorização; resposta somente após autorizar |
| `GET ativos_referencia`, `GET ativos_referencia/{id}` | Loja do Gerente | Registro bruto do Totem | Não | `{id}` lê antes de autorizar; resposta somente após autorizar |
| `GET telemetria_equipamentos`, `GET telemetria_equipamentos/{id}` | Loja do Gerente | Telemetria bruta | Não | `{id}` lê antes de autorizar; resposta somente após autorizar |
| `GET lojas`, `GET lojas/{id}` | Somente a própria Loja | Registro da Loja | Não | Nenhum identificado |
| `GET categorias_servico`, `GET categorias_servico/{id}` | Catálogo | Categoria | Não | Nenhum identificado |
| `GET usuarios`, `GET usuarios/{id}` | Negado a todos os perfis | — | — | Nenhum |
| `GET mira-administracao/lojas` | `listar_opcoes_lojas` exige Administrador | — | — | Nenhum |

## Conclusão

- A única exposição de interações privadas ao Gerente estava nos dois GETs genéricos de `interacoes_chamado`, corrigidos localmente e ainda publicados na versão antiga.
- Nenhum outro endpoint acessível ao Gerente retorna comentários internos ou eventos operacionais.
- Pontos de endurecimento sem spec aprovada, não alterados: leitura antes da autorização em `chamados/{id}`, `ativos_referencia/{id}` e `telemetria_equipamentos/{id}` (sem vazamento na resposta); registros brutos nos GETs genéricos de chamados.
