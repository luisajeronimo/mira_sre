# Pacote de publicação seletiva da C-1 (executado em 2026-11-08)

Situação: **publicado em 2026-11-08** com autorização específica, na ordem abaixo, com dry-run individual antes e depois de cada objeto (ver `tasks.md`, 2.2–2.5). Este documento permanece como registro do procedimento e da reversão. A A1 (`negar-gerente-gets-genericos-chamados`) e a prova E0.3 não fazem parte deste pacote.

## Arquivos e ordem

| Ordem | Arquivo (relativo a `xano/`) | Objeto | Operação esperada |
|---|---|---|---|
| 1 | `function/service_desk/listar_chamados_loja_historica_gerente.xs` | função nova | `CREATE` |
| 2 | `api/apis_from_table_chamados/chamados_GET.xs` | `GET /chamados` | `UPDATE` |
| 3 | `api/apis_from_table_chamados/chamados/chamados_id_GET.xs` | `GET /chamados/{chamados_id}` | `UPDATE` |

A função deve existir antes do endpoint que a chama; publicar 1 antes de 2. O endpoint 3 depende somente de `obter_chamado_gerente_autorizado`, já publicada (sem alteração neste pacote).

Dependências já publicadas e não alteradas: `autorizacao/exigir_perfil`, `administracao/resolver_loja_totem_no_instante`, `service_desk/obter_chamado_gerente_autorizado`, tabela `historico_vinculos_totem_loja`.

## Diferença em relação ao publicado

- Lista: remove o join com `ativos_referencia` e o `where` pela Loja atual; o Gerente passa pela função nova; Técnico e Diretoria fazem a mesma consulta global de antes.
- Detalhe: remove `db.get ativos_referencia` e `exigir_escopo_loja`; adiciona `exigir_perfil` e, para o Gerente, `obter_chamado_gerente_autorizado` antes de `db.get chamados`.

## Comandos (para execução somente após autorização)

```bash
# 1. Dry-run individual; aceitar somente o resultado indicado.
xano workspace push --dry-run --no-guids --no-fast -d xano -w 152692 -b v1 -i function/service_desk/listar_chamados_loja_historica_gerente.xs   # esperado: +1 created
xano workspace push --dry-run --no-guids --no-fast -d xano -w 152692 -b v1 -i api/apis_from_table_chamados/chamados_GET.xs                      # esperado: ~1 updated
xano workspace push --dry-run --no-guids --no-fast -d xano -w 152692 -b v1 -i api/apis_from_table_chamados/chamados/chamados_id_GET.xs          # esperado: ~1 updated
# 2. Publicar na mesma ordem, um arquivo por vez, com novo dry-run imediatamente antes.
# 3. Dry-run pós-push de cada arquivo: "No changes to push".
```

Qualquer `DELETE`, `DROP_FIELD`, criação ou atualização de outro objeto interrompe a publicação.

## Testes posteriores

1. Testes nativos da função nova (7) e de `obter_chamado_gerente_autorizado` (4), pelos IDs listados com `xano unit_test list`.
2. `tests/test_e2e_c1_gets_genericos.py` com as variáveis `MIRA_E2E_*` (somente login e GET).
3. Registrar cada resultado como passou, falhou ou não executado em `tasks.md`.

## Riscos

- Entre a publicação da função e a dos endpoints, nada muda para os usuários (a função não é chamada até o passo 2).
- Gerente que hoje lê pela rota genérica chamados de outra Loja histórica deixa de lê-los (efeito pretendido). O Reflex não usa os GETs genéricos de `chamados` (verificado em 2026-11-08: `app/` chama somente os contratos funcionais `gerente/chamados*` e `tecnico/chamados*`).
- Custo linear da lista do Gerente (design D4).

## Reversão

Republicar as versões anteriores dos dois endpoints a partir do commit `f861306` (`git show f861306:xano/api/apis_from_table_chamados/chamados_GET.xs` e `.../chamados/chamados_id_GET.xs`), com dry-run `~1 updated` cada. A reversão reabre a vulnerabilidade C-1 e só deve ser usada diante de falha funcional comprovada. A função nova pode permanecer publicada sem efeito; sua remoção exige autorização própria (operação destrutiva).
