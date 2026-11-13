# Tasks

## 1. Contrato e autorização

- [x] 1.1 Criar contratos de leitura e catálogo para a Diretoria com período, Loja e Categoria; verificar em testes nativos Diretoria autorizada, demais perfis negados, sessão inválida, datas/IDs inválidos e ausência de filtro por Prioridade. Evidência: testes nativos de autorização/entrada e HTTP anônimo 401; contratos sem parâmetro Prioridade, em `evidencias.md`.
- [x] 1.2 Resolver a Loja histórica do chamado no `criado_em` para os recortes e manter sem vínculo fora de Loja filtrada; verificar com chamado anterior à transferência, vínculo ausente e visão global. Evidência: testes nativos de transferência e dos dois cenários sem vínculo, em `evidencias.md`.

## 2. Volumetria por status

- [x] 2.1 Agregar uma vez cada chamado aberto em `[t0,t1)` pelo status atual e contar status ausente/não canônico separadamente; verificar com mudança posterior de status, chamado anterior ao período e conjunto de contagens conhecidas. Evidência: teste nativo `volume e risco antigo`, em `evidencias.md`.

## 3. Conformidade e risco de SLA

- [x] 3.1 Calcular conformidade do período reutilizando o consumo por estados e a parada vigente, com Cancelados do período e não calculáveis separados; verificar 8/10 = 80%, cancelamento no período, rejeição com nova resolução, ausência de elegíveis e nenhuma duplicação de chamado. Evidência: testes nativos do resumo e da consulta executiva, em `evidencias.md`.
- [x] 3.2 Calcular risco atual de todos os chamados em estados que consomem SLA, sem corte pela data de abertura, nas quatro faixas aprovadas; verificar limites 70/90/100%, chamado antigo, `Resolvido`/terminais fora das faixas e não calculáveis em contagem própria. Evidência: testes nativos da função de consumo consolidada, resumo e consulta executiva, em `evidencias.md`.
- [x] 3.3 Integrar os três agregados numa resposta com período, filtros e instante do retrato de risco; validar XanoScript pelo Xano Developer MCP e testar que nenhum agregado é persistido nem calculado no frontend. Evidência: sete XanoScripts válidos no Developer MCP e teste de contrato/arquitetura em `tests/test_indicadores_operacao.py`, registrados em `evidencias.md`.

## 4. Página executiva

- [x] 4.1 Adicionar cliente HTTP tipado e State com validação da resposta, atualização por filtros, erro e descarte de resposta tardia; verificar com testes de contrato e estado, inclusive risco atual independente do período. Evidência: `tests/test_indicadores_operacao.py` e `make check`, registrados em `evidencias.md`.
- [x] 4.2 Apresentar volumetria, conformidade e risco em painéis distintos na rota de Indicadores, com Loja/Categoria, período, instante do risco e escopo de Totem/Categoria visíveis; verificar estados sem dados/erro, filtros específicos sem efeito cruzado, foco e leitura sem depender só da cor, testes de apresentação e compilação Reflex. Evidência: componentes com rótulos de escopo e seleção acessível, testes de apresentação e compilação Reflex, em `evidencias.md`.

## 5. Integração

- [ ] 5.1 Executar OpenSpec strict, testes Python relevantes e suíte completa, `git diff --check`, testes nativos Xano e dry-run seletivo; registrar resultados, volume e latência de uma consulta real sem credenciais ou dados sensíveis.
- [ ] 5.2 Revisar o diff remoto integral e, somente após autorização de publicação, publicar seletivamente os recursos desta change; verificar por HTTP com conjunto conhecido, acesso direto negado aos outros perfis e dry-run final sem alterações não aprovadas.
