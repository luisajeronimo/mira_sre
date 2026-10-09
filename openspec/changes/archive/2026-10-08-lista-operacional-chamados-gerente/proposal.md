# Proposal

## Why

A jornada atual do Gerente permite listar e abrir chamados, mas a lista é uma
coleção de cards sem filtros, ordenação controlada, total filtrado ou dados
suficientes para o acompanhamento operacional. O formulário também não separa
as semânticas de limpar, descartar e voltar, e sua confirmação de sucesso pode
sumir durante a navegação para o detalhe.

## What Changes

- Evoluir `GET /gerente/chamados` para retornar o resumo operacional necessário
  à tabela, total filtrado e contrato preparado para paginação futura, sem
  implementá-la nesta change.
- Aplicar no Xano, sob whitelist, filtros por número exato, status canônico,
  Totem da Loja e período inclusivo de abertura, além de ordenação server-side
  determinística por campos autorizados, com texto case-insensitive. Chamados válidos possuem
  obrigatoriamente `criado_em` e `ultima_atualizacao_em`; na criação os dois
  recebem o mesmo instante funcional definido pelo backend.
- Substituir a apresentação de cards da listagem do Gerente por tabela com
  colunas aprovadas, contadores, filtros aplicados e ordenação ASC/DESC.
- Derivar no Reflex a ocorrência resumida dos primeiros 80 caracteres de
  `descricao`, sem campo ou resumo persistido.
- Refinar a abertura manual com ações distintas de Salvar, Limpar, Descartar e
  Voltar, mantendo a autoridade já consolidada do backend e tornando o sucesso
  observável após a criação.
- Preservar uma sessão já confirmada diante de falhas transitórias, de contrato
  ou de consulta da lista; somente uma falha real de autenticação pode limpá-la.

## Capabilities

### New Capabilities

_Nenhuma._

### Modified Capabilities

- `chamados-abertura-manual`: ampliar o contrato funcional de consulta da Loja
  com filtros, ordenação, total filtrado e resumo de dados preparado para
  paginação futura, sem novo endpoint ou mudança de escopo.
- `frontend-chamados-gerente`: substituir a listagem básica por tabela
  operacional e completar as ações locais e o feedback observável da abertura
  manual.
- `chamados-acompanhamento-gerente`: tornar explícita a invariável funcional
  dos dois timestamps e remover a compatibilidade operacional com datas nulas,
  sem backfill de dados existentes.
- `chamados-fila-atribuicao-tecnica`: expor os mesmos timestamps funcionais
  obrigatórios quando o DTO técnico representa um chamado válido, sem mudar as
  visões, a autorização ou a tratativa técnica.

## Impact

- Função existente de listagem e fluxos já existentes de criação manual e
  automática, sem schema, tabela, relação ou endpoint adicional.
- DTO e cliente Reflex, `ChamadosGerenteState`, página de lista e formulário de
  abertura do Gerente.
- Testes de XanoScript, cliente/State, UI e regressões de autorização por Loja.
- Não altera comentários, regras de detalhe, tratativa técnica, paginação ou
  dados remotos. O DTO técnico somente passa a transportar os timestamps
  funcionais obrigatórios já persistidos, sem nova capability de perfil.
