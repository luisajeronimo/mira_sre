# Auditoria pré-Apply

## Escopo e alvo

- Auditoria realizada em `2026-09-19T19:03:19-03:00`.
- Workspace: `Luisa's Workspace` (`152692`).
- Branch: `v1`, única branch existente e atualmente live.
- Operações remotas executadas: somente listagem e pull. Nenhum recurso ou dado remoto foi alterado.

## Snapshot e recuperação

Foi obtido um pull completo com records em `/tmp/mira-xano-audit-NyEKDW`. O diretório contém dados sensíveis e, por isso, permanece fora do repositório e não deve ser versionado nem exibido integralmente.

Assinaturas dos três recursos centrais antes de qualquer alteração:

| Recurso | SHA-256 |
|---|---|
| `table/categorias_servico.xs` | `cfe879dba340fb27d374da7c0bf74900323e86f93057884acc58dba0b09641e5` |
| `table/chamados.xs` | `46183bb89deb9a88b0d73eb36bd1a8c94c80b540d04c33aeaaf1238de8bca944` |
| `api/apis_from_table_telemetria_equipamentos/verificar_falhas_GET.xs` | `2c249d3ad5a1d08947e4497281f6c8c0ffa279756aac124ad613307687a2b1d8` |

Não há backup remoto existente. O rollback não deve substituir tabelas inteiras nem apagar chamados criados depois da implantação. Se for necessário restaurar o tipo ou os valores de SLA, a recuperação deverá usar os valores capturados abaixo e atualizar somente `categorias_servico.sla_horas` pelos IDs correspondentes, após novo dry-run e aprovação humana. Recursos XanoScript poderão ser restaurados seletivamente a partir do snapshot, também sem substituir records.

## Comparação do workspace remoto com o snapshot local

- Os oito grupos de API locais e remotos coincidem: CRUDs de ativos, categorias, chamados, interações, lojas, telemetria e usuários, além de `mira_auth`.
- Os schemas de `categorias_servico` e `chamados`, os CRUDs relacionados e `verificar-falhas` coincidem semanticamente entre local e remoto; as diferenças observadas são apenas formatação produzida pela versão do CLI e os records incluídos pelo pull.
- O remoto contém ainda `function/teste.xs`, ausente do snapshot local e fora do escopo desta change. Esse recurso não deve ser removido por uma sincronização futura.
- O schema remoto ainda não possui `permite_abertura_manual`, `descricao`, `origem` ou `sla_horas_aplicado`; `categorias_servico.sla_horas` continua sendo `text` opcional.
- O endpoint remoto `verificar-falhas` coincide com o local e localiza a categoria do heartbeat pelo nome exato `Totem Offline / Sem Heartbeat`.

## Consumidores atuais de `categorias_servico.sla_horas`

| Área/contrato | Uso atual | Impacto da mudança para decimal | Verificação/adaptação necessária |
|---|---|---|---|
| `xano/table/categorias_servico.xs` | Define armazenamento e normalização como `text` com `trim`. | O schema e a representação persistida mudam. | Alterar para decimal somente depois do gate de dados e validar os records convertidos. |
| `GET categorias_servico` genérico | Serializa o registro completo, incluindo `sla_horas`, para os três perfis autenticados. | O JSON passa de string para número. | Tratar como alteração de contrato e cobrir o retorno numérico em regressão; nenhum cliente local chama este endpoint atualmente. |
| `GET categorias_servico/{id}` genérico | Serializa o registro completo, incluindo `sla_horas`. | O JSON passa de string para número. | Mesma regressão do contrato de lista. |
| `POST categorias_servico` e `PATCH categorias_servico/{id}` genéricos | O `dblink` deriva o input do schema da tabela. As mutações são interrompidas por `negar_mutacao_generica`. | O contrato schema-driven passaria a aceitar decimal, embora a execução continue negada. | Confirmar a negação por padrão após a alteração e que nenhuma escrita genérica foi reaberta. |
| `verificar-falhas` | Busca a categoria do heartbeat, mas hoje consome somente o `id`; não lê `sla_horas`. | Não há dependência textual atual. A própria change introduzirá a leitura numérica para o snapshot do chamado. | Validar o novo uso decimal e preservar toda a lógica atual do heartbeat. |
| Relação `chamados.categorias_servico_id` | Referencia a categoria pelo ID. | Nenhum impacto do tipo de SLA sobre a relação. | Regressão de integridade referencial. |
| Simulator Python | Nenhum uso encontrado. | Sem impacto direto. | Executar regressão final sem adicionar regra de SLA. |
| Fiscal Python | Nenhum uso encontrado. | Sem impacto direto. | Executar regressão final sem adicionar regra de SLA. |
| Reflex e testes Python atuais | Nenhum uso nem parser de `sla_horas` encontrado. | Sem consumidor existente a adaptar; o novo cliente deverá modelar o retorno como numérico. | Cobrir o novo DTO e manter os testes de autenticação/sessão. |
| Documentação e contratos locais (`AGENTS.md`, `README.md`, `docs/`, `openspec/config.yaml`) | Referenciam semanticamente o SLA da categoria, sem parsear a representação. | Não há quebra executável. | Preservar a regra e consolidar a mudança por meio desta change. |

Não foi identificado consumidor executável local que dependa de `sla_horas` como string. Consumidores externos dos CRUDs genéricos não podem ser provados ausentes pelo repositório; por isso, a alteração string → número permanece registrada como breaking e os dois contratos de leitura integram a matriz obrigatória de regressão.

## Valores atuais e categoria do heartbeat

Todos os 12 valores atuais são strings inteiras positivas sem unidade, espaço interno, separador ou ambiguidade; a equivalência decimal é direta e preserva o valor.

| ID | Nome | Tipo atual | SLA atual (`text`) | Categoria do heartbeat | `permite_abertura_manual` atual | Valor proposto |
|---:|---|---|---:|:---:|---|---|
| 1 | Totem Offline / Sem Heartbeat | Incidente | `"1"` | Sim | Campo inexistente | `false` |
| 2 | Falha de Rede | Incidente | `"2"` | Não | Campo inexistente | `true` |
| 3 | Tela / Display com Defeito | Incidente | `"4"` | Não | Campo inexistente | `true` |
| 4 | Periférico com Defeito | Incidente | `"4"` | Não | Campo inexistente | `true` |
| 5 | Falha de Energia | Incidente | `"2"` | Não | Campo inexistente | `true` |
| 6 | Cabo / Conexão Física | Incidente | `"4"` | Não | Campo inexistente | `true` |
| 7 | Dano Físico no Totem | Incidente | `"8"` | Não | Campo inexistente | `true` |
| 8 | Alta Temperatura | Incidente | `"2"` | Não | Campo inexistente | `false` |
| 9 | Alto Uso de CPU | Incidente | `"4"` | Não | Campo inexistente | `false` |
| 10 | Alto Uso de Memória | Incidente | `"4"` | Não | Campo inexistente | `false` |
| 11 | Solicitação de Manutenção | Requisição | `"24"` | Não | Campo inexistente | `true` |
| 12 | Solicitação Operacional | Requisição | `"24"` | Não | Campo inexistente | `true` |

A associação do heartbeat ao ID 1 foi confirmada pela consulta por nome em `verificar-falhas` e pelo record remoto correspondente. A descrição persistida dessa categoria menciona cinco minutos, enquanto a implementação e a regra consolidada usam 15 minutos; a descrição não controla o comportamento, mas a inconsistência deve permanecer visível e não será corrigida por inferência nesta change.

## Gate aprovado

A decisão humana aprovou `true` para os IDs 2–7 e 11–12 e `false` para os IDs 1 e 8–10. O ID 1 permanece exclusivo do heartbeat; os IDs 8–10 permanecem fora do formulário manual por representarem condições técnicas de telemetria. Esta change não criará automações novas para os IDs 8–10 e não alterará a descrição divergente do ID 1.
