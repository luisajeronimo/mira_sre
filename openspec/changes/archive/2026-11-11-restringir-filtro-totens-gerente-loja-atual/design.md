# Design

## Context

Ver `proposal.md`. A lista do Gerente usa `GET /gerente/ativos-historicos` como catálogo do filtro, enquanto a abertura manual já usa `GET /gerente/ativos`, restrito à Loja atual. A consulta filtrada e a gravação da preferência aceitam vínculo histórico; a leitura da preferência exige Loja atual. O registro persistido de um Gerente pode, portanto, conter um Totem transferido e impedir a carga da lista. A autorização de cada chamado continua resolvida pelo vínculo histórico no instante de sua abertura.

## Goals / Non-Goals

**Goals:**

- Aplicar a mesma elegibilidade pela Loja atual nas opções, na consulta filtrada, na gravação e na projeção de leitura da preferência.
- Manter a lista utilizável quando uma preferência salva contém Totem que deixou a Loja, sem mutação automática do registro.

**Non-Goals:**

- Alterar a autorização histórica dos chamados, o detalhe ou os comentários.
- Excluir o endpoint histórico, apagar preferências ou executar backfill.

## Decisions

1. **Reutilizar `GET /gerente/ativos` na lista.** O contrato já restringe os Totens à Loja atual pelo Xano e é usado na abertura manual. O State troca apenas a fonte do catálogo do filtro e preserva o cache durante ordenação e aplicação. A alternativa de filtrar no Reflex foi descartada porque o frontend não é autoridade de autorização; alterar o endpoint histórico também afetaria outros usos.
2. **Validar Totens informados pela Loja atual no Xano.** A consulta de chamados com `ativo_ids` e o PUT da preferência recusam Totem cuja `lojas_id` atual difere da Loja da sessão, mesmo com passagem histórica. A lista sem filtro mantém sua regra histórica por chamado. A alternativa de aceitar filtro histórico perpetuaria uma opção não elegível pelo novo contrato.
3. **Projetar a preferência sem Totens transferidos ao lê-la.** O GET verifica cada ID salvo, devolve somente os atuais da Loja e preserva os demais campos. Não grava a projeção. Isso evita 403 e perda de filtros válidos; o registro original só muda quando o próprio Gerente aplica ou limpa filtros. A alternativa de apagar dados na leitura contrariaria a disciplina de dados do projeto, e manter 403 bloquearia a lista.

## Risks / Trade-offs

- **Totem salvo deixa a Loja entre leitura e aplicação** → o Xano revalida no GET filtrado e no PUT; uma falha de escopo não persiste a nova preferência.
- **Totem transferido de volta pode reaparecer na preferência** → o registro é preservado até Aplicar ou Limpar; a projeção sempre usa a Loja atual naquele acesso.
- **Catálogo histórico continua disponível por API** → a lista deixa de consumi-lo; não excluir o recurso remoto evita alterar consumidores fora desta change.

## Migration Plan

Validar XanoScript e os cenários de transferência, executar `xano workspace push --dry-run` seletivo e revisar o diff. Publicar apenas as funções alteradas após o gate de publicação aplicável; repetir o dry-run e validar a leitura sem reescrever preferências. O rollback consiste em restaurar as versões anteriores dessas funções e do State, mediante nova revisão de diff; os registros persistidos permanecem intactos.
