# Proposal

## Why

A fila técnica usa hoje um alias calculado do nome do Técnico, mas a cobertura
disponível tem somente um responsável em cada direção e não comprova a ordem
entre nomes. A correção torna determinística a ordem pelo mesmo texto exibido,
inclusive `Não atribuído`, e a interface ainda comunica a direção de modos
diferentes, expondo `ASC`/`DESC` ao Gerente.

## What Changes

- Substituir, somente para `Responsável`, a dependência da ordenação por alias
  por uma ordem determinística da coleção retornada pelo mesmo texto exibido
  na coluna, incluindo `Não atribuído`, sem distinguir maiúsculas de minúsculas
  em ASC e DESC.
- Manter filtros, demais critérios, desempate por identificador e preferências de ordenação já persistidas, inclusive `Aberto por`.
- Exibir somente a seta da direção ativa nos cabeçalhos ordenáveis das filas Técnica/Diretoria/Administrador e Gerente; remover a seta das colunas inativas e os textos literais de direção.
- Preservar os handlers e contratos de ordenação existentes, sem adicionar filtros, colunas, permissões ou recursos de infraestrutura.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-fila-atribuicao-tecnica`: garante a ordenação de Responsável pelo nome exibido e os indicadores visuais da fila global operacional.
- `frontend-chamados-gerente`: padroniza os indicadores visuais da ordenação na lista do Gerente.

## Impact

- XanoScript: `service_desk/listar_chamados_tecnico`, somente no caminho de ordenação por `responsavel`.
- Reflex: os helpers de cabeçalho em `app/chamados/tecnico/pages.py` e `app/chamados/gerente/pages.py`.
- Testes focados de XanoScript, State/UI de Técnico e Gerente; sem mudança de API, schema, autenticação, preferências ou outros sistemas.
