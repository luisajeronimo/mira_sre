# Design

## Context

Veja `proposal.md`. A fila global é comum a Técnico, Diretoria e Administrador,
mas o Gerente possui tabela e State próprios. A consulta técnica já aceita
`responsavel`, persiste a preferência e pede ao Xano para ordenar o alias
`tecnico_ordenavel`. A cobertura atual tem só um nome atribuído por direção;
logo, ela não demonstra a ordem alfabética entre Técnicos nem permite atribuir
o defeito observado unicamente ao alias. A mudança elimina essa dependência no
caminho de Responsável.

## Goals / Non-Goals

**Goals:**

- Produzir ordem determinística pelo texto exibido de `tecnico.nome` ou `Não
  atribuído`, sem caixa e com empate por id em ASC e DESC.
- Usar os helpers de cabeçalho já existentes para mostrar somente a seta da
  direção ativa nas duas tabelas.
- Conservar parâmetros, handlers, filtros e preferência de ordenação atuais.

**Non-Goals:**

- Não alterar API, schema, autorização, paginação, Fiscal, Simulator ou
  monitoramento.
- Não introduzir componente compartilhado, filtro, coluna ou persistência nova.
- Não alterar o fluxo nem a ordenação de `Aberto por`.

## Decisions

### Ordenação de Responsável é determinada sobre o nome retornado

O Xano manterá a consulta e seus filtros atuais, mas o caminho de
`responsavel` ordenará toda a coleção por uma chave formada pelo texto exibido:
`tecnico_nome` normalizado quando houver Técnico e `Não atribuído` quando não
houver, seguido do id. ASC/DESC será aplicado à mesma chave, sem partição de
não atribuídos. Isso preserva os demais critérios no backend.

Alternativa rejeitada: ordenar pelo id do Técnico. Ela não corresponde à coluna
exibida. Alternativa rejeitada: ordenar no Reflex. Ela quebraria a autoridade
do Xano, a estabilidade com filtros e a preferência já existente.

### Indicadores são locais aos helpers atuais

Cada helper de cabeçalho existente comporá o rótulo e somente o `rx.icon` da
direção ativa; cabeçalhos inativos não renderizarão ícone. O botão e seu handler
permanecem os mesmos; os textos `ASC`, `DESC` e o rótulo auxiliar atual do
Gerente deixam de ser renderizados.

Alternativa rejeitada: criar componente compartilhado entre as duas jornadas.
Os States e nomes de direção são distintos, e um componente novo ampliaria a
mudança sem ganho necessário.

## Risks / Trade-offs

- [Chaves textuais no Xano tratarem nomes iguais de forma inesperada] → incluir
  teste com nomes em ordem inversa aos ids, mesmo nome e ids diferentes, e o
  rótulo `Não atribuído` nas duas direções.
- [Ícone comunicar direção apenas por cor] → usar o glifo direcional da coluna
  ativa e preservar o rótulo acessível do botão.

## Migration Plan

1. Alterar somente a função Xano e os dois helpers Reflex definidos na proposta.
2. Executar validação XanoScript e os testes focados; compilar Reflex em modo
   seco.
3. Antes de publicar, executar dry-run Xano e confirmar que somente
   `service_desk/listar_chamados_tecnico` aparece. A publicação exige
   autorização humana específica; não há migração de dados.
4. Em falha, reverter os três arquivos da implementação, sem tocar em
   preferências persistidas ou em `Aberto por`.
