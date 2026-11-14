# Proposta — Causas e recorrência

## Why

A Diretoria já acompanha disponibilidade e operação/SLA, mas ainda não identifica as Lojas com mais incidentes nem a concentração de causas e repetição de chamados. A Sprint 5 entrega esses três indicadores sobre os fatos existentes, com regras públicas e cálculo reproduzível.

## What Changes

- Top 5 Lojas por Incidentes não cancelados, Pareto por Categoria e recorrência de 30 dias conforme `indicadores-operacionais`.
- Nova aba Causas e recorrência na página atual, com período, Loja histórica, Totem e Categoria; padrão de 30 dias, Hoje e personalizado.
- Exclusões e ausência de Loja histórica explícitas; consultas somente leitura e agregação no Xano Free.
- Testes, validação e publicação seletiva dos novos contratos e funções; sem novas tabelas, backfill, agregados persistidos, mecanismos de concorrência ou dependências de sprint como gate.

## Capabilities

### New Capabilities

- `dashboard-causas-recorrencia`: autorização, filtros, Top 5, Pareto e apresentação da recorrência com suas bases e detalhamentos.

### Modified Capabilities

- `dashboard-operacao-sla`: ampliar a navegação compartilhada para a terceira aba, preservando os escopos dos indicadores existentes.

## Impact

`xano/function/indicadores/`, dois novos GETs em `xano/api/mira_service_desk/indicadores/`, cliente HTTP, contrato tipado, State e página em `app/indicadores/`, testes e documentação de entrega. Reutiliza Categoria, chamados e vínculo histórico existentes.

## Decisões do Explore

Em 14/11/2026, a responsável aprovou o conjunto apresentado no Explore e autorizou seguir até concluir o Apply e a publicação seletiva. Os três indicadores usam Incidentes não cancelados com Categoria válida, Totem e data; Categoria vigente, inclusive inativa; sem snapshot novo. Sem Loja comprovada, os fatos entram globalmente em causas/recorrência e ficam fora do ranking e do recorte por Loja. Pareto destaca o menor prefixo que alcança 80%, sem impor 20% das Categorias; empates usam ID crescente. O predecessor de recorrência mantém validade entre transferências. Não há decisão humana funcional pendente; Archive não integra este pedido.

## Atualização de autorização

A decisão humana posterior desta mesma sessão equiparou Técnico, Diretoria e
Administrador nos acessos operacionais, preservando Gestão exclusiva e
responsáveis somente Técnicos. O delta desta change foi reconciliado; a
implementação e as evidências da correção pertencem à change
`unificar-acessos-perfis-operacionais`.
