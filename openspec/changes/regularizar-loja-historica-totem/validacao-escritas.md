# Validação pendente das escritas da Loja histórica

Preparado em 2026-11-08. Nada aqui foi executado: as operações abaixo gravam registros e só podem ser validadas em ambiente isolado autorizado, com dados de teste. O workspace `152692` é o único da conta e é compartilhado; `xano sandbox` exige plano pago e `xano ephemeral` cria tenant dentro desse workspace ([validação de 05/11](../acompanhamento-solicitante-historico-status/validacao-xano-2026-11.md#prova-e03-ambiente-isolado)).

## Situação no repositório

| Documento | Escrita | Versionado | Validação |
|---|---|---|---|
| `service_desk/abrir_chamado_manual` | `marco` (sem vínculo e com Loja atual) e chamado | Não (local, igual ao publicado) | Testes nativos não executados |
| `verificar-falhas` | `marco`, Totem `offline` e incidente | Não (local, igual ao publicado) | Sem testes nativos |
| `administracao/transferir_totem` | `transferencia` e Totem, em `db.transaction` | Não (local, igual ao publicado) | Testes nativos não executados |
| `administracao/totens` (GET, POST, PATCH, DELETE) | `criacao` no POST; exclusão do vínculo `criacao` no DELETE | Não (local, igual ao publicado) | Sem testes nativos |
| `listar_ativos_historicos_gerente` e `gerente/ativos-historicos` | Somente leitura | Não | Sem testes; DL-4 aberta |

A parte de leitura (resolvedor, autorizador, listas e detalhes) está versionada desde o commit `63f864d`.

## Pré-requisitos

1. Ambiente Xano isolado autorizado (ou outro meio aprovado), sem dados reais.
2. Prova E0.3 executada e aprovada, porque `transferir_totem`, a abertura manual e o heartbeat fazem escritas dependentes (DL-3; DT-1).
3. Decisões DL-1 a DL-5 registradas (abaixo).

## Testes nativos publicados (executar somente no ambiente isolado)

| Função | ID | Teste |
|---|---|---|
| `abrir_chamado_manual` | `83bbba4f711c77a6cd1d9e02a94c6004` | cria chamado manual |
| `abrir_chamado_manual` | `44ddabe8cbb93bff71316dd2f6df4b9a` | administrador abre em outra loja |
| `abrir_chamado_manual` | `d003d3fb45819999411ec1211c95f154` | rejeita titulo ausente |
| `abrir_chamado_manual` | `e737430282314b48ccf777e6f4c96390` | rejeita titulo somente espacos |
| `abrir_chamado_manual` | `ab75fc79f52ca0f1b01e806ba040f3a1` | rejeita descricao vazia |
| `abrir_chamado_manual` | `f15527f666adb0d55c5216bbca0a39f4` | rejeita descricao somente espacos |
| `abrir_chamado_manual` | `f7712ea3a581a92193cb513c553eabde` | rejeita prioridade invalida |
| `abrir_chamado_manual` | `c44dd51993a654b5453558229b5c63b9` | rejeita ativo inexistente |
| `abrir_chamado_manual` | `0022f42445d57b904875cedb4dbe295e` | rejeita ativo de outra loja |
| `abrir_chamado_manual` | `0f4096978a949172200d1c36852c7e5a` | rejeita categoria inexistente |
| `abrir_chamado_manual` | `81a5031f0d0249e8f20b05f8d053e565` | rejeita categoria bloqueada |
| `abrir_chamado_manual` | `999d84469b9a7a8db2df9a8d57f53817` | rejeita categoria sem sla |
| `transferir_totem` | `a4f8f0e910419f59ff5327ca23e5deb8` | transfere para loja ativa |
| `transferir_totem` | `e042dd3fb7c4056b9d3306c8cb25f0c6` | rejeita loja inativa |

Os IDs pertencem ao workspace `152692`; num ambiente isolado novo, os testes terão outros IDs (`xano unit_test list --obj-type function`). Antes de executar, confirmar se os `mock` desses testes substituem as escritas ou se `db.add` persiste: a documentação disponível não garante, e esse é o motivo de não executá-los no workspace compartilhado.

## Cenários HTTP após os testes nativos

| # | Cenário (spec `vinculo-historico-totem-loja`) | Esperado |
|---|---|---|
| T1 | Chamado de Totem com vínculo anterior | Loja do vínculo mais recente até `criado_em` |
| T2 | Totem transferido depois da abertura | Chamado continua na Loja da abertura; Gerente da Loja nova recebe 403 |
| T4 | Chamado novo para Totem sem vínculo e com Loja atual | Um `marco` com `efetivado_em = criado_em` |
| T4b | Chamado novo para Totem sem vínculo e sem Loja atual | Abertura manual rejeitada; heartbeat cria incidente sem `marco` e com Loja histórica nula |
| T5 | Gerente consulta chamado da própria Loja histórica | 200 em lista, detalhe, comentários e histórico |
| — | `administracao/totens` POST, PATCH com troca de Loja e DELETE | `criacao` no POST; `transferencia` somente quando a Loja muda; DELETE recusado com dependências |
| — | Falha entre as escritas | Nenhum registro parcial (depende da conclusão da E0.3) |

## Decisões pendentes (somente a responsável pelo projeto)

| ID | Pergunta | O que destrava |
|---|---|---|
| DL-1 | Chamados legados sem vínculo podem ficar fora da jornada do Gerente? | Aceite do estado atual (hoje todos os chamados existentes) |
| DL-2 | Texto da Loja nula no Reflex | Apresentação para Técnico, solicitante e monitoramento |
| DL-3 | Escritas dependentes aceitas sem a prova E0.3? | Versionar e validar `abrir_chamado_manual`, `verificar-falhas`, `transferir_totem` e `totens*` |
| DL-4 | Quem consulta o histórico de vínculos | Versionar `gerente/ativos-historicos` |
| DL-5 | Chamados removidos (53–56 e 90) e interações órfãs | Tratamento de dados (exige autorização própria) |
