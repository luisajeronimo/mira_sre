# Design — Causas e recorrência

## Context

Ver `proposal.md`. As fórmulas de recorrência e a Loja histórica já estão consolidadas. A página executiva tem duas abas e filtros reutilizáveis. Existem alterações locais prévias nessa página que serão preservadas. A referência visual é `DESIGN.md` e `docs/design/references/diretoria-dashboard.png`.

## Goals / Non-Goals

Entregar consultas somente leitura e apresentação dos agregados com os contratos existentes de autenticação e a mesma linguagem visual. Não adicionar tabelas, snapshots de classificação, jobs, cache, locks ou controle de concorrência adicional: a consulta não grava dados e o volume é acadêmico.

## Decisions

- Criar `GET /indicadores/causas-recorrencia` e `/filtros`, com funções próprias autorizadas para Técnico, Diretoria e Administrador. Reutilizar autorização e resolução de Loja; não ampliar os contratos de operação/SLA com filtros incompatíveis.
- Separar consulta de fatos e resumo determinístico XanoScript. Consultar chamados desde t0 menos 30 dias até o corte observado e registros sem data para a contagem identificada separadamente. Carregar cadastros e vínculos em lote, sem uma consulta por chamado. Resolver a Loja no instante da abertura. O resumo recebe esses fatos para testes nativos com conjuntos conhecidos; nenhum agregado é persistido.
- Normalizar elegíveis e localizar predecessores por Totem/Categoria antes de filtrar a Loja do chamado atual. Assim, transferências não destroem a recorrência. O predecessor não usa a Loja do recorte. Consultas/cálculo simples em memória são suficientes para o volume acadêmico; não introduzir arquitetura de materialização.
- Contagens de exclusão se referem aos chamados do período após os filtros aplicáveis; registros sem data têm contagem própria sem atribuição temporal e não pertencem a Loja filtrada. Sem Categoria não se atribui classificação; Categoria inválida e Totem ausente são inconsistências, sem reparo histórico.
- Contrato tipado estrito no Python e State apenas para apresentação. Aba nova compartilha período/Loja e reutiliza Totem/Categoria, preservando os escopos das abas anteriores. Listas, tabela acessível e gráfico de Pareto exibem valores calculados pelo Xano; taxas vazias permanecem indisponíveis.

## Risks / Trade-offs

- Classificação e status são os valores vigentes → publicar a regra, não prometer snapshot histórico inexistente.
- Histórico ausente → contar sem Loja comprovada; não preencher nem usar Loja atual.
- Volume crescente → consulta limitada ao período mais janela e carregamento em lote; validar latência real quando houver credenciais, sem exigir infraestrutura adicional.
- Credencial ou navegador indisponível → registrar verificação como bloqueada e nunca como passou.

## Migration Plan

Validar XanoScript pelo Developer MCP, testes nativos com fatos conhecidos, Python, Reflex, OpenSpec strict e diff. Revisar e mostrar dry-run somente dos novos arquivos antes de publicar; executar novo dry-run após o push. Sem alteração de dados. Publicar backend antes de disponibilizar a nova aba. Archive depende de solicitação própria.
