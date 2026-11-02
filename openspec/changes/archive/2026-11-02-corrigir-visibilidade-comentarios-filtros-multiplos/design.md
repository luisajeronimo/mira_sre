# Design

## Context

O schema `interacoes_chamado` reúne comentários e eventos operacionais e possui `visibilidade` enum anulável. Hoje `validar_save_tratativa_chamado` grava `alteracao_chamado` como `interna`; `assumir_chamado_tecnico` faz o mesmo para `atribuicao`, `reatribuicao` e `liberacao`. Esse valor não autoriza os eventos: `obter_chamado_tecnico` já autoriza por perfil e chamado e retorna toda a timeline global. Porém, o DTO transporta a visibilidade e o Reflex cria badge para qualquer tipo.

O Gerente usa outro contrato: obtém o status atual do chamado autorizado e consulta separadamente comentários cuja interação tem conteúdo e `visibilidade == "publica"`. Ele não recebe hoje a timeline operacional global.

Em preferências, `preferencias_fila_chamados` contém escalares: `status` e `prioridade` são texto; Totem, Loja e Responsável são relações inteiras; `somente_nao_atribuido` é booleano. Número, períodos e ordenação também ficam no mesmo registro único por usuário+escopo. Não existe campo disponível para coleções.

## Goals / Non-Goals

**Goals:**

- Fazer visibilidade pertencer somente a comentários no armazenamento novo, DTO e UI.
- Preservar eventos históricos sem apagar nem reclassificar dados.
- Manter autorização no Xano independente da visibilidade de comentário.
- Persistir multisseleções com fonte de verdade inequívoca e compatibilidade escalar.
- Minimizar schema, contratos e código afetados.

**Non-Goals:**

- Remover a coluna `interacoes_chamado.visibilidade`, necessária aos comentários.
- Fazer backfill ou limpar valores históricos de eventos operacionais.
- Criar timeline operacional para Gerente, tabela de preferências ou filtros novos.
- Refatorar ordenação, autenticação ou regras de negócio não relacionadas.

## Decisions

### 1. Visibilidade é atributo condicional de comentário

Novos comentários continuam exigindo `publica` ou `interna`. Novos eventos `atribuicao`, `reatribuicao`, `liberacao` e `alteracao_chamado` omitem `visibilidade`, permanecendo `null` na coluna compartilhada. Não é necessária alteração de schema em `interacoes_chamado`.

O DTO global normaliza `visibilidade` para valor somente quando `tipo == "comentario"`; em eventos operacionais devolve `null`, inclusive quando o registro histórico contém `interna` ou `publica`. O parser Reflex valida comentário classificado e aceita evento operacional sem visibilidade. A UI renderiza badge somente para comentário, inclusive dentro do card agrupado.

Valores históricos não são apagados: deixam de ser fonte funcional e visual apenas para tipos operacionais. Comentário legado sem classificação não é promovido a Público; o contrato do Gerente continua falhando fechado.

`listar_comentarios_publicos_gerente` deve exigir explicitamente interação de comentário atual ou legado compatível, conteúdo não vazio e `visibilidade == "publica"`. Ausência de visibilidade em evento operacional nunca concede acesso. O status atual do Gerente continua vindo do chamado autorizado, não da timeline nem da visibilidade do comentário.

### 2. Comparação das alternativas de persistência

| Alternativa | Vantagens | Desvantagens e migração | Decisão |
|---|---|---|---|
| Evoluir campos atuais para coleções | Nenhum campo adicional | Converter textos e relações inteiras escalares para array/JSON é alteração destrutiva; exige migração dos registros, perde semântica de relação e quebra contratos escalares | Rejeitada |
| Adicionar campo por filtro | Tipos e leitura separados | Exige ao menos cinco novos campos e um indicador para `Não atribuído`; aumenta estados parciais e regras de precedência; ainda precisa fallback legado e migração por save | Rejeitada por maior superfície |
| Um JSON `filtros_multiplos` | Um campo aditivo, snapshot atômico, distingue `null` de objeto vazio e reutiliza o registro usuário+escopo | Validação estrutural fica nas funções Xano | Recomendada |

O XanoScript aceita arrays tipados nos inputs, mas o schema local das preferências usa campos escalares/relações e já comprova suporte a JSON em outras tabelas. Um JSON opcional é a menor evolução aditiva comprovada. Não há alternativa sem alteração de schema que armazene múltiplos IDs sem serialização indevida ou conversão destrutiva.

### 3. Formato exato e fonte de verdade da preferência

Adicionar, somente após aprovação humana, `json? filtros_multiplos?` ao fim da tabela existente. Quando presente, o objeto tem formato completo:

```json
{
  "status": ["Novo", "Resolvido"],
  "ativo_ids": [1, 2],
  "loja_ids": [3],
  "prioridades": ["Alta", "Urgente"],
  "responsavel_ids": [12, 15],
  "incluir_nao_atribuido": true
}
```

- `filtros_multiplos == null`: registro ainda legado; GET converte cada escalar elegível em lista unitária e converte `somente_nao_atribuido` no booleano novo.
- Objeto presente: única fonte de verdade dos cinco filtros, mesmo quando todas as listas estão vazias e o booleano é `false`.
- Objeto presente e inválido: erro de contrato; nunca fazer fallback para escalares, pois isso poderia reviver filtro antigo.
- Primeiro save válido, inclusive Aplicar, Limpar ou persistir ordenação global: grava o objeto completo e neutraliza no mesmo upsert `status`, `ativos_referencia_id`, `lojas_id`, `prioridade`, `responsavel_id` e `somente_nao_atribuido`.
- Número, períodos, `ordenar_por` e `direcao` continuam nas colunas atuais e no mesmo save.

Assim, Limpar escreve listas vazias/booleano falso e limpa os escalares elegíveis; novo login não pode restaurar valor antigo. Não há backfill: cada linha migra de forma preguiçosa somente no próximo save confirmado.

`Não atribuído` não usa `0` nem outro sentinela. `responsavel_ids` contém apenas IDs positivos de Técnicos; `incluir_nao_atribuido` controla, no mesmo filtro, a inclusão de chamados com responsável nulo.

### 4. Payloads GET/PUT

As funções Xano recebem arrays (`text[]`/`int[]`). Nos GETs, cada coleção é transmitida uma única vez como texto JSON, decodificado e validado como array pelo endpoint antes de chamar a função. Isso evita depender da interpretação de chaves repetidas pelo servidor. Exemplo global (sem a codificação de URL para facilitar a leitura):

```text
GET /tecnico/chamados?status=["Novo","Resolvido"]&ativo_ids=[1,2]&loja_ids=[3]&prioridades=["Alta"]&responsavel_ids=[12]&incluir_nao_atribuido=true&ordenar_por=numero&direcao=DESC
```

O GET do Gerente aceita somente `status` e `ativo_ids` em texto JSON entre os filtros múltiplos. Loja, Responsável e Prioridade não integram seu input e tentativa explícita é rejeitada com 422. Número, datas e ordenação mantêm nomes e semântica atuais.

O PUT global recebe:

```json
{
  "escopo": "todos",
  "numero": null,
  "status": ["Novo", "Resolvido"],
  "ativo_ids": [1, 2],
  "data_inicio": null,
  "data_fim": null,
  "ultima_atualizacao_inicio": null,
  "ultima_atualizacao_fim": null,
  "loja_ids": [3],
  "prioridades": ["Alta"],
  "responsavel_ids": [12],
  "incluir_nao_atribuido": true,
  "ordenar_por": "numero",
  "direcao": "DESC"
}
```

O PUT do Gerente recebe o mesmo conjunto escalar vigente de número e períodos, mais `status: []` e `ativo_ids: []`; não recebe escopo, Loja, Prioridade ou Responsável. Os GETs de preferência retornam `{ "preferencia": ... }` com o mesmo formato canônico de cada PUT, inclusive arrays vazios. Nunca devolvem o JSON bruto nem os escalares legados.

### 5. Validação e combinação no Xano

Antes de consultar ou salvar, o Xano:

- remove duplicatas e normaliza cada Status para o literal canônico vigente;
- aceita somente prioridades canônicas;
- exige IDs positivos e existentes para Totem/Loja e IDs de usuários com perfil Técnico para Responsável;
- valida todos os Totens do Gerente contra a Loja da sessão;
- rejeita a coleção inteira se qualquer valor for inválido ou não autorizado;
- combina valores do mesmo filtro por pertencimento OR e filtros distintos, número, períodos e escopo rápido por AND;
- aplica `responsavel_id IS NULL OR responsavel_id IN (...)` quando o booleano e IDs coexistirem;
- preserva ordenação e desempate atuais antes de formar o DTO.

Aplicar/Limpar mantêm a sequência existente: consultar candidato, salvar preferência após sucesso e somente então confirmar State/lista. `Todos` e `Atribuídos a mim` continuam registros separados do Técnico; Diretoria/Administrador permanecem apenas em `Todos`.

### 6. Dropdown multisseleção

Um componente controlado compartilhado em `app/components/visual.py` usará primitivas Reflex para trigger/resumo, menu e check textual/visual por opção. O State mantém listas de rascunho, confirmadas e aplicadas. Alternar opção não consulta nem persiste; Aplicar e Limpar continuam as únicas confirmações de filtro.

### 7. Recursos Xano realmente afetados

Visibilidade/timeline:

- funções `validar_save_tratativa_chamado.xs`, `assumir_chamado_tecnico.xs`, `obter_chamado_tecnico.xs` e `listar_comentarios_publicos_gerente.xs`;
- nenhum endpoint novo e nenhuma alteração na tabela `interacoes_chamado`.

Filtros/preferências:

- tabela `preferencias_fila_chamados.xs`: somente o campo JSON recomendado;
- endpoints `gerente/chamados_GET.xs` e `tecnico/chamados_GET.xs`;
- endpoints GET/PUT `gerente/preferencias-fila` e `tecnico/preferencias-fila`;
- funções `listar_chamados_gerente.xs`, `listar_chamados_tecnico.xs`, `obter_preferencia_filtros_gerente.xs`, `salvar_preferencia_filtros_gerente.xs`, `obter_preferencia_fila_tecnica.xs` e `salvar_preferencia_fila_tecnica.xs`.

## Risks / Trade-offs

- [JSON inválido poderia reviver legado] → objeto não nulo inválido falha; fallback existe somente para `null`.
- [Limpeza parcial deixaria escalar antigo] → objeto completo e neutralização dos escalares ocorrem no mesmo upsert.
- [Retirar visibilidade poderia ampliar acesso] → autorização continua por endpoint/perfil/chamado; consulta pública exige explicitamente comentário Público.
- [Histórico contém metadado antigo] → preservar armazenamento, mas normalizar DTO operacional para `null` e nunca renderizar badge.
- [Serialização de arrays diverge] → cada coleção usa um parâmetro JSON único; os testes do cliente cobrem a serialização e a validação do endpoint exige array. A execução HTTP real continua pendente.
- [Dropdown perde acessibilidade] → check e texto além da cor, foco visível e teste de teclado/compilação.

## Migration Plan

1. Obter aprovação humana específica do campo `filtros_multiplos`; sem ela, não iniciar Apply.
2. No Apply autorizado, alterar primeiro escrita/leitura de eventos e seus testes, sem migrar histórico.
3. Adicionar o campo JSON de forma aditiva e evoluir contratos com fallback escalar; não executar backfill.
4. Atualizar DTOs/States/componentes Reflex de forma coordenada e executar testes focados, compilação, validação XanoScript e dry-run.
5. Não remover colunas escalares nem o campo de visibilidade. Em rollback, preservar dados novos e corrigir adiante; publicação e reversão remotas exigem autorização própria.

## Decisão humana necessária

A nova regra de visibilidade já foi decidida pelo usuário. Permanece pendente somente aprovar ou rejeitar a adição do campo JSON opcional `filtros_multiplos` antes do Apply.
