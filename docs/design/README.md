# Referências visuais do MIRA

Esta pasta reúne referências visuais sanitizadas para orientar a apresentação da
interface. A autoridade e as regras de uso estão em [`DESIGN.md`](../../DESIGN.md).

## Precedência

Ao projetar ou revisar UI, siga esta hierarquia:

1. requisitos funcionais autorizados;
2. `DESIGN.md`;
3. PNG relacionado;
4. componentes Reflex existentes.

Requisito funcional vence qualquer contradição visual. Sem PNG relacionado,
derive a solução de `DESIGN.md` e das referências existentes, reutilizando os
componentes Reflex antes de criar novos padrões.

Os PNGs não são pixel-perfect e servem somente para composição, hierarquia,
densidade, identidade, navegação, aparência de componentes, espaçamento e
linguagem visual. Textos, nomes, números, métricas, prioridades, status, SLAs,
perfis, entidades, exemplos, ações e comportamentos retratados são ilustrativos
e nunca requisitos funcionais.

## Arquivos

- `references/abrir-chamado.png` — composição de abertura de chamado.
- `references/login.png` — composição de autenticação.
- `references/fila-tecnica.png` — composição de fila técnica.
- `references/chamados-gerente.png` — composição de chamados gerenciais.
- `references/administracao.png` — composição administrativa.
- `references/diretoria-dashboard.png` — composição de dashboard.

As referências não definem dados, ações, permissões, fluxos ou comportamentos
do MIRA.
