# Design

## Context

Fonte: `xano workspace pull` somente leitura de 2026-11-07 (workspace `152692`, branch `v1`), Metadata API (`GET table/content`) e dry-run completo. Nada foi alterado.

### Comportamento publicado

| Elemento | Publicado | Repositório (`06cc763`) |
|---|---|---|
| Tabela `historico_vinculos_totem_loja` | `ativos_referencia_id`, `loja_origem_id?`, `loja_destino_id`, `tipo` ∈ {`criacao`, `marco`, `transferencia`}, `efetivado_em`; índice único (`ativos_referencia_id`, `efetivado_em`) | Ausente |
| `administracao/resolver_loja_totem_no_instante` | Vínculo mais recente com `efetivado_em <= instante`; sem vínculo ou sem instante → `{lojas_id: null}` | Ausente |
| `administracao/obter_loja_historica_fato` | Projeta `{loja: {id, nome}}` ou `{loja: null}` | Ausente |
| `administracao/transferir_totem` | Administrador; em `db.transaction`: grava `transferencia` somente se a Loja muda e edita `ativos_referencia` (`identificacao`, `nome_ativo`, `lojas_id`) | Ausente |
| `service_desk/listar_ativos_historicos_gerente` e `GET gerente/ativos-historicos` | Totens historicamente vinculados à Loja do Gerente | Ausentes |
| `abrir_chamado_manual` | Sem nenhum vínculo do Totem → grava `marco` (Loja atual, `efetivado_em = criado_em`) antes do chamado | Sem marco |
| `verificar-falhas` (incidente automático) | Mesma regra de marco para Totem sem vínculo | Sem marco |
| `obter_chamado_gerente_autorizado`, `obter_chamado_gerente`, `listar_chamados_gerente` | Autorizam e listam pela Loja histórica; `null` → não pertence à Loja do Gerente (403 / fora da lista) | Loja atual |
| `listar_chamados_tecnico`, `obter_chamado_tecnico`, `obter_detalhe_ativo_monitoramento`, `obter_chamado_solicitante` | Exibem a Loja histórica (`null` sem vínculo); sem efeito de autorização | Loja atual (exceto o solicitante, já reconciliado) |
| `administracao/totens` (GET/POST/PATCH/DELETE) | POST grava `criacao`; PATCH chama `transferir_totem`; DELETE recusa Totem com chamados, telemetria, disponibilidade, preferência ou transferência e remove só o vínculo `criacao` | Ausentes |
| `ativos_referencia.identificacao` | Campo `text?` | Ausente (push completo faria `DROP_FIELD`) |

### Dados em 2026-11-07

- `historico_vinculos_totem_loja`: 0 registros.
- `chamados`: 10 registros (49, 50, 51, 52, 77, 83–87), todos sem vínculo anterior ao `criado_em`.
- Interações órfãs dos chamados removidos 53–56 e 90 (remoção não registrada nos logs de API e Metadata API do período).

## Goals / Non-Goals

**Goals:** repositório e specs iguais ao comportamento publicado da regra histórica; regra de não retroatividade explícita; testes planejados para os cenários da regra.

**Non-Goals:** mudar o comportamento publicado; fallback para a Loja atual; backfill; corrigir dados; publicar; rotas administrativas fora de Totem.

## Decisions

### D1. Fonte da verdade

Os documentos XanoScript serão **copiados do publicado** (`xano workspace pull` em diretório temporário, comparação documento a documento e cópia somente dos itens do escopo para `xano/`), sem reescrita. Diferenças de formatação são aceitas; diferenças de lógica não.

### D2. Escopo dos documentos

Incluídos: tabela `historico_vinculos_totem_loja`; campo `ativos_referencia.identificacao`; funções `resolver_loja_totem_no_instante`, `obter_loja_historica_fato`, `transferir_totem`, `listar_ativos_historicos_gerente`; atualizações publicadas de `abrir_chamado_manual`, `listar_chamados_gerente`, `obter_chamado_gerente`, `obter_chamado_gerente_autorizado`, `listar_chamados_tecnico`, `obter_chamado_tecnico`, `obter_detalhe_ativo_monitoramento`; endpoints `verificar-falhas`, `gerente/chamados GET`, `tecnico/chamados GET`, `gerente/ativos-historicos GET` e `administracao/totens*`.

Excluídos (change própria): `administracao/usuarios*`, `administracao/lojas*`, `administracao/categorias`, `administracao/chamados POST`, `listar_opcoes_lojas`, `validar_criacao_usuario`, `telemetria_equipamentos POST`, `gerente/chamados POST`.

Se um documento incluído depender de um excluído, a dependência é registrada e o documento permanece fiel ao publicado.

### D3. Não retroatividade

Nenhuma task cria, edita ou remove registros. Nenhuma lógica nova infere Loja para chamado sem vínculo. A spec torna isso requisito.

### D4. Critério de conclusão do Apply

`xano workspace push --dry-run` completo (somente leitura) sem diferenças para os documentos do escopo e sem `DROP_FIELD`. Diferenças restantes devem ser apenas as excluídas em D2 e `calcular_consumo_sla_chamado` (não publicada, DE-8).

## Risks / Trade-offs

- [Jornada do Gerente sem dados legados] → consequência da regra publicada; decisão DL-1.
- [Escritas dependentes sem prova E0.3] → `transferir_totem`, marco + chamado e `administracao/totens POST` já publicados; registrado em DL-3, sem novas escritas nesta change.
- [Workspace editado por terceiros] → copiar do `pull` mais recente e repetir a comparação antes de concluir.
- [Changes ativas] → `acompanhamento-solicitante-historico-status` modifica outros requisitos das mesmas specs; arquivar na ordem e consolidar sem perder texto.

## Resultado do Apply local (2026-11-07)

- 22 documentos copiados do `pull` das 19:58 (12 criados, 10 atualizados); nenhum dos 10 atualizados tinha alteração local em relação ao `HEAD`. Linhas somente com espaços foram esvaziadas (formatação); nenhuma linha com conteúdo foi alterada.
- Dry-run completo (somente leitura) depois da cópia: sem `DROP_FIELD`, sem diferença em 21 dos 22 documentos. Restam somente as exclusões de D2 (`listar_opcoes_lojas`, `validar_criacao_usuario`, `telemetria_equipamentos POST`, `gerente/chamados POST`) e `calcular_consumo_sla_chamado` (DE-8).
- Exceção: `obter_detalhe_ativo_monitoramento` continua como UPDATE no dry-run, embora o arquivo local seja byte a byte igual ao `pull` antes da normalização de espaços. A causa da discrepância não foi determinada; não publicar este documento enquanto ela não for investigada.
- Diferenças semânticas copiadas fielmente e registradas: `abrir_chamado_manual` autoriza os perfis Gerente e Administrador. O teste nativo `administrador abre em outra loja` demonstra que a função aceita um Administrador e um Totem associado a outra Loja; o endpoint administrativo correspondente está fora do escopo D2 e não foi trazido, portanto nenhuma conclusão sobre seu contrato HTTP é inferida. `verificar-falhas` publicado responde 401 sem `Content-Type` e com `$resultado` em ramo `else`, mantendo corpo e ordem do guarda.
- A comparação posterior do `abrir_chamado_manual` local com o pull publicado confirmou igualdade após normalização de espaços; o comportamento de Administrador descrito acima permanece confirmado.
- Dry-run completo posterior aos ajustes locais de M1-M6 e A1: 1 função criada, 5 funções atualizadas e 4 endpoints atualizados; nenhum `DROP_FIELD` foi reportado. As atualizações foram `administracao/listar_opcoes_lojas`, `administracao/validar_criacao_usuario`, `service_desk/listar_chamados_gerente`, `service_desk/obter_chamado_gerente` e `service_desk/obter_detalhe_ativo_monitoramento`; o item criado foi `service_desk/calcular_consumo_sla_chamado`. Os endpoints atualizados foram `chamados GET`, `chamados/{chamados_id} GET`, `telemetria_equipamentos POST` e `gerente/chamados POST`. As mudanças de A1 nos GETs e os testes nativos adicionados às duas funções do Gerente são locais e ainda não publicados; os demais itens permanecem sujeitos às exclusões de D2 ou DE-8. O UPDATE de `obter_detalhe_ativo_monitoramento` continua sem causa determinada e não deve ser publicado até investigação. Onze endpoints existentes somente no remoto não foram incluídos; como o dry-run não usou `--delete`, nenhuma remoção foi proposta.

## Migration Plan

Sem migração de dados. Ordem do Apply: pull somente leitura → cópia dos documentos do escopo → validação MCP → testes locais e nativos (somente funções de leitura) → dry-run completo → docs. Reversão: restaurar os arquivos locais pelo Git; nada no servidor muda.
