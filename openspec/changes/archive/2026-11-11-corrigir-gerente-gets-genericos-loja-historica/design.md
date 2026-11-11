# Design

## Contexto

| Contrato | Antes (publicado) | Depois |
|---|---|---|
| `GET /chamados`, Gerente | `where` com `$db.ativo.lojas_id == $usuario.lojas_id` (Loja atual) | `listar_chamados_loja_historica_gerente` (Loja histórica) |
| `GET /chamados/{id}`, Gerente | `exigir_escopo_loja` com `$ativo.lojas_id` (Loja atual), depois da leitura do registro | `obter_chamado_gerente_autorizado` (Loja histórica), antes da leitura |
| Técnico e Diretoria | Global | Global (inalterado) |
| Administrador e perfis não oficiais | Negados por `exigir_perfil` | Inalterado |

## Decisões

**D1. Não alterar `exigir_escopo_loja`.** A função compara a Loja informada pelo chamador e é usada pelos GETs genéricos de `ativos_referencia`, `lojas` e `telemetria_equipamentos`, que tratam dados atuais. Mudar sua semântica afetaria contratos fora do escopo.

**D2. Detalhe reutiliza `obter_chamado_gerente_autorizado`.** Entradas (`usuarios_id`, `chamados_id`) coincidem com as da rota; a função exige o perfil Gerente com Loja, localiza o chamado, resolve a Loja em `criado_em` e falha fechada sem Loja demonstrável. Está publicada e coberta por testes nativos (`autoriza chamado da loja`, `rejeita gerente sem loja`, `rejeita chamado inexistente`, `rejeita chamado de outra loja`). Ela retorna somente `{id, status, autor_nome}` e a rota só lê o registro completo depois dela.

**D3. Lista usa função nova sem join com `ativos_referencia`.** O GET genérico devolve os registros crus da tabela `chamados`; `listar_chamados_gerente` devolve DTO funcional e não serve ao contrato. A função nova consulta `chamados` sem join, portanto não tem acesso à Loja atual do Totem, e chama `resolver_loja_totem_no_instante` somente quando `ativos_referencia_id` e `criado_em` existem. A inclusão exige Loja resolvida não nula e igual à do Gerente.

**D4. Paginação, filtros e desempenho.** O contrato genérico não aceita entrada (`input {}`), logo não há paginação nem filtro que contorne o escopo. O custo é linear no total de chamados, com uma consulta ao histórico por chamado (mesmo padrão de `listar_chamados_gerente`, achado M-3 da auditoria). Reduzir esse custo exige consulta por conjunto ou paginação, o que muda contratos; fica fora desta correção de segurança.

**D5. Respostas.** A lista do Gerente sem escopo devolve `[]`; Gerente sem Loja recebe 403. No detalhe, Gerente recebe 404 para chamado inexistente e 403 para chamado sem Loja histórica ou de outra Loja, como no contrato funcional `gerente/chamados/{id}`.

## Riscos

- O comportamento só passa a valer no Xano após publicação autorizada; até lá a vulnerabilidade permanece no workspace publicado.
- Os testes nativos da função nova e o E2E ainda não foram executados (dependem da publicação).
