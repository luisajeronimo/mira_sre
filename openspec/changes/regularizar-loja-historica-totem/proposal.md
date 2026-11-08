# Proposal

## Why

O workspace Xano publicado (`152692`, branch `v1`) implementa uma regra que não existe no repositório: a Loja de um chamado é a Loja **histórica** do Totem no instante do fato, resolvida por `historico_vinculos_totem_loja`. A autorização do Gerente, as listas e os detalhes publicados já usam essa regra. O repositório (`06cc763`) e as specs consolidadas descrevem a Loja atual do Totem ("relação persistida chamado, Totem e Loja").

Consequências observadas por leitura em 2026-11-07:

- `historico_vinculos_totem_loja` está **vazia**. A Loja histórica é `null` para os 10 chamados existentes, e nenhum Gerente consegue listar, detalhar, comentar ou consultar o histórico de status desses chamados.
- Um `xano workspace push` completo a partir do repositório atualizaria 10 funções, 5 endpoints e 1 tabela, e **descartaria** o campo `ativos_referencia.identificacao` (`DROP_FIELD`), revertendo a regra publicada.

Esta change traz a regra publicada para o repositório e para as specs, sem alterar o que está publicado.

## What Changes

- Nova capability `vinculo-historico-totem-loja`: registro de vínculos comprovados (`criacao`, `marco`, `transferencia`), resolução da Loja de um fato por instante, Loja histórica nos DTOs e ausência de vínculo retroativo automático.
- Regra do marco: ao criar um chamado novo (abertura manual ou incidente automático) para Totem sem nenhum vínculo, o Xano registra um `marco` com a Loja atual e o instante do chamado.
- Autorização e escopo do Gerente passam a usar a Loja histórica do chamado; chamado sem Loja histórica não pertence a nenhuma Loja para o Gerente.
- Regularização dos documentos XanoScript publicados que implementam a regra (cópia fiel do publicado; sem mudança de comportamento) e do campo `ativos_referencia.identificacao`.
- Domínio e documentação atualizados.

Não muda: nenhuma função ou endpoint publicado; nenhum registro; nenhuma interface Reflex.

## Capabilities

### New Capabilities

- `vinculo-historico-totem-loja`: vínculos históricos Totem–Loja, resolução por instante, marco na criação de chamado, ausência de retroatividade.

### Modified Capabilities

- `autorizacao-perfis`: "Gerente acessa somente sua unidade" passa a usar a Loja histórica para chamados.
- `chamados-abertura-manual`: "Gerente acompanha todos os chamados da própria Loja" passa a usar a Loja histórica.
- `chamados-acompanhamento-gerente`: "Gerente consulta comentários públicos do chamado da própria Loja" passa a usar a Loja histórica.

## Regra sobre chamados legados (fixada pela solicitação de 2026-11-07)

Chamados sem evidência histórica **não recebem vínculo retroativo automático**: nenhum backfill, nenhuma inferência pela Loja atual e nenhum fallback para a Loja atual. Eles permanecem sem Loja histórica (`null`).

## Decisões pendentes

| ID | Pergunta | Fato que a motiva | Impacto |
|---|---|---|---|
| DL-1 | A equipe aceita que chamados legados sem vínculo fiquem inacessíveis à jornada do Gerente? | Hoje, 10 de 10 chamados estão nessa situação | Jornada do Gerente sem dados até novos chamados |
| DL-2 | Como o Reflex apresenta Loja `null` (Técnico, solicitante, monitoramento)? | DTOs publicados devolvem `loja = null` sem vínculo | Texto de interface ("Não informado" é o atual) |
| DL-3 | As escritas dependentes (transferência; marco + chamado) são aceitas sem a prova E0.3? | Publicado grava em `db.transaction` sem atomicidade comprovada no Free | Risco de vínculo sem chamado ou Totem sem vínculo |
| DL-4 | Quem pode ver o histórico de vínculos (hoje: Gerente por `gerente/ativos-historicos`; Administrador pelas rotas de Totem)? | Rotas publicadas sem spec no repositório | Contratos de leitura |
| DL-5 | Tratamento dos chamados removidos (53–56 e 90) e das interações órfãs | Removidos fora da API; autoria não comprovada | Integridade de dados (exige autorização própria) |

## Fora do escopo

- Rotas administrativas publicadas de usuários, Lojas, categorias e chamados (`administracao/*` exceto as de Totem), regra de Loja "Ativa", ajuste de `telemetria_equipamentos POST` e `exigir_perfil` em `gerente/chamados POST`: divergências reais, registradas para change própria.
- `calcular_consumo_sla_chamado` (DE-8).
- Qualquer correção de dados, backfill ou restauração.

## Impact

- Repositório: `xano/` (documentos copiados do publicado), specs, `docs/domain-model.md`, `docs/project-overview.md`, testes de contrato.
- Xano: nenhum push nesta change sem autorização própria; após o Apply, o dry-run completo deve deixar de mostrar as diferenças da regra histórica e o `DROP_FIELD`.
- Interação com changes ativas: `acompanhamento-solicitante-historico-status` também modifica `autorizacao-perfis` e `chamados-acompanhamento-gerente` em requisitos diferentes; o detalhe do solicitante já foi reconciliado com a Loja histórica.
