# Integração de `main` na branch do PR #26 (2026-11-08)

Merge de `origin/main` (`64f2790`) em `explore-monitoramento-xano` (`f861306`), feito em worktree separado; commit `b19d4b4`. Nenhum merge em `main`.

## Método

Para cada objeto Xano em conflito foram comparados: a versão do PR (ours), a de `main` (theirs), a do working tree local e a publicada (`xano workspace pull` somente leitura do mesmo dia), em forma canônica (sem diferenças de espaço, vírgulas separadoras, cercas de mock e parênteses que o servidor reescreve), além dos conjuntos de testes nativos de cada lado. Origem: `main` versionou os mesmos objetos publicados pela change arquivada `2026-11-08-administracao-mira` (commit `d75db38`); o PR os versionou nos commits `63f864d`, `9276048`, `6afb174` e `c9ede3c`. São versões independentes dos mesmos objetos de produção.

## Resultado por arquivo

| # | Arquivo | Tipo | Comparação | Resolução |
|---|---|---|---|---|
| 1 | `docs/domain-model.md` | conteúdo | 4 blocos | Blocos 1, 2 e 4: texto do PR (mais completo, cobre o de `main`). Bloco 3: integra a regra operacional implementada em `main` (Técnico, Diretoria e Administrador selecionam `Solução Rejeitada` no Save) e a rejeição pelo Gerente aprovada no PR |
| 2 | `tests/test_automation_auth.py` | conteúdo | 2 blocos | Mantém o teste novo do Simulator de `main` e a parametrização ampliada das guardas do PR |
| 3 | `tests/test_lista_operacional_gerente.py` | conteúdo | 3 blocos | Asserções do PR (tolerantes ao layout publicado) e verificações de `main` (422 antes da consulta, ordem do `else`) em forma compacta |
| 4 | `api/.../interacoes_chamado_id_GET.xs` | conteúdo | ours = theirs = publicado | ours |
| 5 | `api/.../interacoes_chamado_GET.xs` | conteúdo | ours = theirs | ours |
| 6 | `api/.../telemetria_equipamentos_POST.xs` | conteúdo | ours = theirs | ours |
| 7 | `api/.../verificar_falhas_GET.xs` | conteúdo | ours = theirs = publicado | ours |
| 8–12 | `api/mira_administracao/totens*` (5 rotas) | add/add | ours = theirs = publicado | ours (sem duplicação de rota) |
| 13 | `api/mira_service_desk/gerente/chamados_GET.xs` | conteúdo | ours = theirs = publicado | ours |
| 14 | `api/mira_service_desk/gerente/chamados_POST.xs` | conteúdo | ours = theirs = publicado | ours |
| 15 | `api/mira_service_desk/tecnico/chamados_GET.xs` | conteúdo | ours = theirs = publicado | ours |
| 16 | `function/administracao/obter_loja_historica_fato.xs` | add/add | ours = theirs = publicado | ours |
| 17 | `function/administracao/resolver_loja_totem_no_instante.xs` | add/add | ours = theirs = publicado | ours |
| 18 | `function/administracao/transferir_totem.xs` | add/add | ours = theirs = publicado | ours |
| 19 | `function/administracao/validar_criacao_usuario.xs` | conteúdo | ours = theirs = publicado | ours |
| 20 | `function/service_desk/abrir_chamado_manual.xs` | conteúdo | ours = theirs = publicado | ours |
| 21 | `function/service_desk/listar_ativos_historicos_gerente.xs` | add/add | ours = theirs = publicado | ours |
| 22 | `function/service_desk/listar_chamados_gerente.xs` | conteúdo | ours ≠ theirs ≠ publicado; publicado = working tree | ours no merge; versão publicada no commit `fc2c696` (+3 testes nativos de Loja histórica; `main` sem teste exclusivo) |
| 23 | `function/service_desk/listar_chamados_tecnico.xs` | conteúdo | ours = publicado; theirs difere só em forma (mesmos 11 testes) | ours |
| 24 | `function/service_desk/obter_chamado_gerente.xs` | conteúdo | publicado = working tree | ours no merge; versão publicada em `fc2c696` |
| 25 | `function/service_desk/obter_chamado_gerente_autorizado.xs` | conteúdo | ours = publicado; theirs difere só em ordem de cláusulas (mesmos 4 testes) | ours |
| 26 | `function/service_desk/obter_chamado_tecnico.xs` | conteúdo | publicado = working tree | ours no merge; versão publicada em `fc2c696` (alias `tecnico_usuario`) |
| 27 | `function/service_desk/obter_detalhe_ativo_monitoramento.xs` | conteúdo | ours = publicado; theirs difere em ordem de cláusulas e `type: "inner"` padrão (mesmos 3 testes) | ours |
| 28 | `table/historico_vinculos_totem_loja.xs` | add/add | ours = theirs | ours |

## Preservado de `main`

- Rotas administrativas publicadas e ausentes do PR (11; a auditoria contou 12 por engano, pois `administracao/lojas` GET e `administracao/usuarios` POST já existiam no PR): `administracao/categorias` GET, `administracao/chamados` POST, `administracao/lojas/registros` GET e POST, `administracao/lojas/{lojas_id}` GET, PATCH e DELETE, `administracao/usuarios` GET, `administracao/usuarios/{usuarios_id}` GET, PATCH e DELETE. Entraram sem conflito; as versões de `main` já estavam no repositório de origem dessas rotas.
- Interface administrativa Reflex, ajustes do Simulator e do Fiscal, change arquivada `2026-11-08-administracao-mira` e specs consolidadas por ela.

## Ajustes decorrentes da nova base OpenSpec

As specs consolidadas por `main` passaram a conter cenários que os deltas MODIFIED do PR omitiam. Foram incorporados sem alterar regra: "Gerente com Loja Inativa" (o cenário do PR tinha o mesmo nome com outra caixa), "Loja histórica indeterminada" e "Loja histórica não demonstrável".

## Pendência registrada

`obter_chamado_tecnico` publicado usa o alias `tecnico_usuario`, enquanto `docs/xanoscript-language-server.md` recomenda não renomear aliases sem justificativa funcional. Não há justificativa registrada para a troca; os campos de saída não mudam. Decisão humana: manter (como publicado) ou reverter numa publicação futura.
