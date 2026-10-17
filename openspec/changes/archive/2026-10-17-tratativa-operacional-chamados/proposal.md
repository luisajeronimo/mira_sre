# Proposal: tratativa-operacional-chamados

## Why

A fila global e o detalhe já permitem consultar e distribuir chamados, mas a tratativa permanece fragmentada em comandos imediatos de responsável e não oferece uma edição operacional coerente de status, prioridade, categoria e responsável. É necessário concentrar essas mudanças em uma operação auditável e atômica, sem alterar a fila já validada.

## What Changes

- Cria a tratativa operacional unificada para Técnico, Diretoria e Administrador, com edição pendente de Responsável, Status, Prioridade e Categoria.
- Substitui na jornada de tratativa os controles imediatos `Assumir`, `Atribuir`, `Reatribuir` e `Liberar` por um único campo `Responsável`, `Descartar mudanças` e `Salvar`.
- Define um contrato Xano transacional que valida, persiste e retorna o detalhe canônico pós-commit, sem efeitos parciais.
- Exige comentário humano em toda mudança de status e cria exatamente um evento automático estruturado `alteracao_chamado` por Save com diferença funcional efetiva.
- Protege o Save contra sobrescrita silenciosa pela comparação simples de `ultima_atualizacao_em`, sem introduzir lock, fila ou retry automático.
- Acrescenta comentários operacionais Público/Interno e permite comentários humanos em chamados terminais, mantendo os campos funcionais bloqueados.
- Atualiza o SLA aplicado quando a Categoria efetivamente muda, sem reiniciar a referência temporal do chamado.
- Preserva eventos e comentários históricos sem backfill, conversão ou alteração da fila global, de seus filtros, seus escopos ou sua pesquisa.

## Capabilities

### New Capabilities

- `tratativa-operacional-chamados`: edição pendente, Save atômico, comentário operacional e evento estruturado de alteração do chamado.

### Modified Capabilities

- `chamados-fila-atribuicao-tecnica`: substitui os comandos imediatos de responsável na jornada operacional e integra o novo evento à timeline existente.
- `autorizacao-perfis`: concede a Técnico, Diretoria e Administrador a tratativa operacional global e explicita o escopo de comentário do Gerente.
- `chamados-acompanhamento-gerente`: permite comentário público do Gerente em chamado terminal dentro do escopo já autorizado.
- `chamados-abertura-manual`: altera o snapshot de SLA somente quando a Categoria for efetivamente modificada na tratativa operacional.

## Impact

- **Xano:** novo contrato autenticado de Save, catálogo de categorias para edição, validação de permissões e persistência transacional de chamado, comentário e evento.
- **Dados:** extensão estruturada das interações para `alteracao_chamado`, sem backfill ou conversão de interações antigas.
- **Reflex:** State de edição pendente, controles de Salvar/Descartar, comentário independente e renderização compatível da timeline.
- **Integração e validação:** testes de contrato, Xano, persistência, REST autenticado, Reflex integrado e validação humana. Testes unitários isolados não comprovam atomicidade nem fluxo REST real.
