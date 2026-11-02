# Proposal

## Why

O modelo atual atribui `publica`/`interna` tanto a comentários quanto a eventos automáticos, embora essa classificação só tenha significado para comunicação humana; a timeline acaba apresentando um fato operacional como se fosse comentário privado. Além disso, os filtros existentes aceitam apenas um valor por critério e não permitem consultas operacionais múltiplas persistidas entre sessões.

## What Changes

- Definir que somente comentários possuem visibilidade Público/Interno. `atribuicao`, `reatribuicao`, `liberacao` e `alteracao_chamado` passam a ser fatos operacionais sem classificação de visibilidade e sem badge correspondente.
- Parar de gravar visibilidade em novos eventos operacionais e normalizar o DTO da timeline para expor visibilidade somente em comentários. Metadados de visibilidade já existentes em eventos históricos permanecem armazenados, mas deixam de ter significado funcional e de ser apresentados.
- Manter comentários correlacionados a alterações com sua classificação real, sem copiar essa classificação para o evento nem esconder comentário Interno de perfis globais autorizados.
- Preservar a autorização por contrato, perfil e escopo de chamado no Xano. O Gerente continua recebendo somente comentários explicitamente públicos e o status atual autorizado; esta change não cria para ele a timeline operacional global.
- Transformar somente filtros já existentes em multisseleção: Status e Totem para Gerente; Status, Totem, Loja, Responsável e Prioridade para Técnico, Diretoria e Administrador.
- Combinar opções do mesmo filtro com OR e filtros diferentes com AND, preservando número, períodos, ordenação, Aplicar, Limpar e o isolamento `Todos`/`Atribuídos a mim`.
- Evoluir os contratos autenticados para arrays validados e persistir o conjunto completo por usuário e escopo.
- Recomendar, sujeito a aprovação humana antes do Apply, um único campo JSON opcional na preferência existente. `null` identifica registro legado; objeto presente, inclusive com listas vazias, é a fonte canônica após o primeiro save.
- Restaurar escalares legados como coleções unitárias sem backfill. Aplicar/Limpar grava a representação nova completa e neutraliza os escalares multisseleção no mesmo save, impedindo o reaparecimento de filtros antigos.
- Representar `Não atribuído` por `incluir_nao_atribuido: true`, separado de `responsavel_ids`, sem usar ID sentinela.
- Fora do escopo: nova tabela, backfill, remoção de colunas ou histórico, novos filtros, timeline operacional para Gerente, alteração de autenticação, regras de status, paginação ou dependência externa.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `tratativa-operacional-chamados`: somente comentários possuem visibilidade; eventos operacionais novos e históricos são apresentados sem essa classificação.
- `chamados-acompanhamento-gerente`: visibilidade de comentário permanece distinta da autorização do chamado, mantendo comentário Interno fora do contrato público e o status atual autorizado disponível.
- `chamados-fila-atribuicao-tecnica`: os cinco filtros globais existentes passam a aceitar coleções, aplicar OR interno/AND externo e persistir todas as seleções por usuário e escopo.
- `preferencias-filtros-gerente`: Status e Totem passam a ser persistidos como coleções, com fallback escalar inequívoco e sem ampliar o escopo da Loja.
- `frontend-chamados-gerente`: os dois filtros elegíveis existentes passam a usar dropdown multisseleção, preservando critérios e ações atuais.

## Impact

- Reflex: DTO/modelo da timeline, apresentação global, cliente Service Desk, States, páginas de filtros e um componente visual compartilhado.
- Xano da timeline: `validar_save_tratativa_chamado`, `assumir_chamado_tecnico`, `obter_chamado_tecnico` e endurecimento de `listar_comentarios_publicos_gerente`; a tabela `interacoes_chamado` não muda.
- Xano dos filtros: endpoints/funções de listagem e preferências do Gerente e da fila global; tabela existente `preferencias_fila_chamados`.
- Schema recomendado: adicionar somente `json? filtros_multiplos?`; não converter campos escalares, criar tabela ou migrar registros em massa.
- Contratos: arrays canônicos em GET/PUT, `responsavel_ids` separado de `incluir_nao_atribuido`, e preferência GET devolvendo sempre coleções normalizadas.
- Testes: modelo da timeline, autorização pública, eventos históricos, payloads, OR/AND, validação, Limpar, compatibilidade legada e isolamento por escopo.
- Dependências: nenhuma nova.
- Decisão humana pendente: aprovar ou rejeitar o campo JSON recomendado antes de qualquer Apply; esta revisão não concede essa aprovação.
