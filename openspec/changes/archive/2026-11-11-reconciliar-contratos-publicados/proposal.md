# Proposal

## Why

O dry-run completo de 2026-11-08 (15:32, workspace `152692`, branch `v1`, somente leitura) mostrou quatro documentos em que o Xano publicado está **à frente** do repositório: o repositório tinha a versão do `HEAD` (`06cc763`) e o publicado acrescentava regras. Um `xano workspace push` desses arquivos reverteria o publicado, inclusive retirando um controle de segurança.

| Documento | O publicado acrescenta |
|---|---|
| `api/mira_service_desk/gerente/chamados_POST.xs` | `autorizacao/exigir_perfil` com `gerente: true` antes de `service_desk/abrir_chamado_manual` |
| `api/apis_from_table_telemetria_equipamentos/telemetria_equipamentos_POST.xs` | Guarda da credencial do Simulator na forma `var $resultado` + `else` (mesma de `verificar-falhas`), 401 sem `Content-Type` explícito e o mesmo corpo `{error: "Não autenticado."}` |
| `function/administracao/listar_opcoes_lojas.xs` | Opções de Loja somente com `status` `Ativa`, `ativa` ou `Ativo` |
| `function/administracao/validar_criacao_usuario.xs` | Gerente somente em Loja existente e ativa (`Ativa`, `ativa` ou `Ativo`), erro "Loja inexistente ou Inativa." e teste nativo da Loja legada `Ativo` |

Esses itens foram excluídos do escopo de `regularizar-loja-historica-totem` (design D2) para tratamento em change própria (task 4.3 daquela change). Esta change trata deles sem misturar a regra de Loja ativa com a regra de Loja histórica.

## What Changes

- Repositório passa a conter as versões publicadas dos quatro documentos (cópia fiel; linhas somente com espaços esvaziadas).
- `administracao-usuarios`: criação de Gerente exige Loja existente **e ativa**; opções de Loja para a criação listam somente Lojas ativas. `Ativo` é aceito por compatibilidade com Lojas legadas.
- `chamados-abertura-manual`: torna explícito que o Administrador também é negado no contrato funcional do Gerente, como o publicado já aplica em `POST /gerente/chamados`.
- `autenticacao-automacoes`: sem mudança de requisito. A spec exige o status 401 e o corpo exato; o publicado mantém ambos.
- Testes de contrato ajustados ao formato real do Xano e teste novo da regra de Loja ativa e do gate do Gerente.

Não muda: nada no Xano (nenhum push); dados; Reflex; Loja histórica.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `administracao-usuarios`: "Associação de Loja segue o perfil criado" e "Administração consulta opções mínimas de Loja para criar Gerente".
- `chamados-abertura-manual`: "Contratos funcionais preservam autenticação e negação por padrão".

## Decisões aprovadas (2026-11-08)

| ID | Decisão |
|---|---|
| RC-1 | Incorporar ao repositório as versões publicadas dos quatro documentos e ajustar os testes correspondentes, sem publicar nada no Xano |
| RC-2 | Preservar o gate `exigir_perfil(gerente)` antes de `abrir_chamado_manual` em `POST /gerente/chamados` |
| RC-3 | Preservar a filtragem de opções por Loja ativa (`Ativa`, `ativa` ou `Ativo`) |
| RC-4 | Preservar a rejeição de Gerente em Loja inativa e a compatibilidade com Lojas legadas `Ativo` |
| RC-5 | Reconciliar o contrato de resposta de `telemetria_equipamentos POST` com o publicado |

## Fora do escopo

- Rotas administrativas inicialmente identificadas como somente publicadas (`administracao/usuarios*`, `administracao/lojas*`, `administracao/categorias`, `administracao/chamados POST`): ficaram fora desta change. A integração posterior de `2026-11-08-administracao-mira` (`d75db38`) as versionou; pull e dry-run seletivo em 11/11/2026 confirmaram a correspondência com o Xano, sem necessidade de change futura para essa divergência.
- `abrir_chamado_manual`, que no publicado aceita Administrador (Loja de outro perfil); a abertura pelo Administrador por contrato próprio depende das rotas administrativas acima.
- Valores de `status` de Loja: esta change não define o cadastro nem a transição de status de Loja; só a regra de uso na criação de Gerente.
- Loja histórica do Totem (`regularizar-loja-historica-totem`) e A1 (`negar-gerente-gets-genericos-chamados`).

## Impact

- `xano/`: quatro documentos (já publicados; nenhum push).
- Testes: `tests/test_administracao_xanoscript.py`, `tests/test_automation_auth.py`, `tests/test_contratos_publicados_reconciliados.py`.
- `regularizar-loja-historica-totem` task 4.3: três das quatro divergências foram tratadas nesta change; as rotas administrativas foram versionadas pela change arquivada `2026-11-08-administracao-mira`, conforme pull e dry-run seletivo de 11/11/2026.
