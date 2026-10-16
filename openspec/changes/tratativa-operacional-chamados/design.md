# Design

## Context

Ver [proposal.md](proposal.md). A change `fila-distribuicao-chamados` permanece responsável por fila, filtros, detalhe de consulta e timeline existente. Ela já distribui responsável por comandos imediatos. Esta change substitui somente a jornada operacional de mutação, sem redesenhar a fila nem alterar os documentos de baseline.

O Xano é a autoridade de autenticação, autorização, validação, persistência e transação. O Reflex mantém o rascunho visual e consome DTOs canônicos; não decide permissão nem normaliza silenciosamente resposta incompatível.

## Goals / Non-Goals

**Goals:**

- Concentrar as quatro mudanças funcionais em um Save coerente e recuperável após falha.
- Distinguir comentário humano de auditoria automática estruturada.
- Preservar a linha do tempo e as interações históricas já persistidas.
- Fornecer evidência que atravesse Xano, REST autenticado e Reflex, além de testes locais.

**Non-Goals:**

- Alterar a tabela global, seus filtros, seus escopos ou a pesquisa.
- Fazer backfill, converter ou apagar interações históricas.
- Criar status novo, incluindo `Aguardando Terceiro`, ou matriz rígida de transições.
- Mudar outras regras de cálculo de SLA, identidade ou autenticação.
- Alterar `docs/project-overview.md`, `docs/domain-model.md` ou `openspec/config.yaml`.

## Decisions

### Contrato único de Save e DTO pós-commit

O Xano receberá um contrato funcional de Save do detalhe, distinto dos controles legados imediatos. O payload representa os quatro valores pendentes, `ultima_atualizacao_em` do detalhe confirmado e comentário de status quando necessário. O backend carrega o chamado atual, compara o timestamp recebido e calcula as diferenças; não confia em flags de alteração do cliente.

Isso permite que `null` represente `Não atribuído`, que a Categoria atual inativa seja mantida quando não foi modificada e que o servidor retorne o mesmo DTO canônico de detalhe após o commit. Reutilizar vários endpoints imediatos exigiria coordenação no Reflex e permitiria persistência parcial, por isso foi descartado.

### Transação operacional no Xano

O Save usa uma única operação transacional disponível no plano Free. A sequência interna é: autenticar e autorizar; carregar o estado; comparar `ultima_atualizacao_em`; bloquear terminal; calcular diferenças; validar valores e comentário; atualizar chamado; criar comentário obrigatório, quando houver; criar exatamente um `alteracao_chamado` se houver diferença funcional; atualizar `ultima_atualizacao_em`; retornar o detalhe pós-commit.

O evento só é criado para uma diferença funcional efetiva. Um Save sem diferença não escreve chamado, evento ou timestamp. A transação elimina a alternativa de atualizar primeiro o chamado e registrar a auditoria por requisições separadas, que já produziu inconsistência na distribuição anterior.

### Responsável e timestamps

O campo de payload é um identificador de usuário Técnico ou `null`. O Xano valida a função persistida do usuário escolhido, sem introduzir uma regra nova de usuário Técnico ativo. Atribuição e reatribuição definem `atribuido_em` com o tempo do backend; liberação persiste `tecnico_id = null` e `atribuido_em = null`. A troca de responsável não muda Status por si só.

Os botões imediatos antigos deixam de ser oferecidos pela UI de tratativa. Contratos legados podem existir temporariamente durante a migração técnica interna, mas, ao concluir esta change, não permanecem como caminho funcional alternativo autorizado: o Save transacional é a única autoridade da nova mutação operacional de Responsável.

### Comentário humano separado da auditoria

`interacoes_chamado` recebe um formato estruturado aditivo para `alteracao_chamado`, contendo ator, instante e pares anterior/resultante dos campos que mudaram. Comentários humanos continuam interações próprias com texto e visibilidade. Quando Status muda, ambas as interações coexistem na mesma transação: um comentário obrigatório e exatamente um evento automático agregado.

Comentários normais usam operação própria e somente atualizam `ultima_atualizacao_em`; não enviam os quatro campos. A projeção de timeline aceita tipos legados (`atribuicao`, `reatribuicao`, `liberacao` e comentários) e o novo tipo, ordenando a coleção final por instante efetivo descrescente e `id` decrescente no empate.

O campo de comentário da tratativa permanece sempre visível. Quando houver
diferença funcional, texto opcional acompanha o mesmo Save; a mudança de
Status continua exigindo texto. O Save persiste no máximo um comentário humano
e o evento `alteracao_chamado` guarda `comentario_interacao_id` dentro de seus
dados estruturados quando aquele comentário pertence à mesma transação. O
Reflex usa somente essa referência explícita para agrupá-los em um único card;
eventos históricos sem a referência continuam individuais.

### Categoria, catálogo e SLA

`categorias_servico` recebe `ativo` booleano com padrão `true`, preservando as categorias existentes como ativas na introdução do campo. O catálogo próprio da edição retorna somente Categorias ativas e válidas para nova seleção. O detalhe retém a Categoria persistida mesmo se inativa. O Save somente exige Categoria ativa quando `categoria_id` é diferente do persistido; `ativo` é independente de `permite_abertura_manual`, cuja regra não se aplica à tratativa.

Quando há troca válida, o SLA aplicado é copiado da Categoria resultante na mesma transação. O cálculo posterior continua usando a data de criação e as regras vigentes de pausa e retomada; não há reinício do relógio. Alterar o SLA de uma Categoria sem trocar a Categoria do chamado não reescreve chamados já existentes.

### Estado Reflex e erros

O State mantém valores confirmados, incluindo `ultima_atualizacao_em`, e rascunho separados. `Descartar mudanças` copia o confirmado para o rascunho. Só a resposta canônica de sucesso substitui ambos. Em erro, a UI mantém o detalhe confirmado, deixa explícito que o Save falhou e não exibe rascunho como confirmado. Se o Xano rejeitar timestamp desatualizado, a UI informa atualização concorrente e recarrega o detalhe; não há lock, fila, retry automático, versionamento complexo ou garantia forte de concorrência.

Se Status não mudou, o formulário independente de comentário permanece separado. Se mudou no rascunho, o State exige comentário associado para habilitar Salvar ou mostra validação clara; Resolvido, Aguardando Solicitante e Cancelado fixam Público, e os demais destinos permitem Público ou Interno. O Xano continua a validação definitiva.

O cliente HTTP reutiliza a autenticação de sessão já usada pela fila. O mapeamento preserva 401 como sessão inválida, 403 como permissão negada, 404 como inexistência, 422 como erro funcional e 5xx/conexão como indisponibilidade. A validação de contrato do service não é substituída por valores vazios de conveniência.

### Autorização e escopo

O Xano autoriza Técnico, Diretoria e Administrador para consulta global e tratativa operacional. Gerente continua na própria Loja e jornada autorizada: só adiciona comentário Público e nunca edita os quatro campos, recebe comentário Interno ou ganha fila global. Chamados Encerrado e Cancelado bloqueiam os campos para todos, mas não comentários permitidos pelo perfil.

## Risks / Trade-offs

- **Transação Free pode divergir da sintaxe local conhecida** → validar XanoScript e executar cenários de persistência e rollback no workspace live antes de considerar a task concluída.
- **Registros legados têm tipos e campos ausentes** → projetar DTO discriminado por tipo de interação e validar exemplos reais, sem backfill nem fallback que esconda contrato quebrado.
- **Rascunho pode divergir após falha ou concorrência** → só confirmar com DTO pós-commit e recarregar o detalhe após conflito ou incompatibilidade de contrato.
- **Categoria atual inativa pode ser confundida com escolha inválida** → comparar com o valor persistido antes de aplicar a validação de categoria ativa.
- **Duas interações em Save de Status podem parecer duplicidade** → apresentar comentário humano e `alteracao_chamado` com tipos visíveis e distintos.
- **Save pode sobrescrever edição alheia silenciosamente** → comparar somente `ultima_atualizacao_em`, rejeitar divergência e recarregar detalhe; não introduzir mecanismos complexos de concorrência.

## Migration Plan

1. Adicionar schema/contrato aditivo do evento, catálogo e Save sem converter interações existentes.
2. Validar XanoScript e dry-run seletivo antes de sincronizar recursos afetados.
3. Sincronizar o backend e verificar o REST autenticado real com estados atribuídos, não atribuídos, Categoria inativa e terminal.
4. Publicar o Reflex que consome o novo contrato e remove os controles imediatos da jornada de tratativa.
5. Se for necessário rollback, retirar o novo contrato/UI e preservar os registros `alteracao_chamado`, que continuam legíveis na timeline; não apagar histórico.

## Open Questions

Nenhuma. A forma concreta de serialização do campo estruturado do evento será escolhida na implementação conforme o schema Xano existente, preservando os dados obrigatórios definidos pelas specs.
