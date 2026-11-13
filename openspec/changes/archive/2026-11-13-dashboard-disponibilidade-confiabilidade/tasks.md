# Tasks

## 1. Gates e contrato executivo

- [x] 1.1 Confirmar com a responsável pelo projeto o período inicial, a granularidade diária, o acesso exclusivo da Diretoria e o descarte das referências “2” e “D4”; verificar que proposal, design e deltas refletem a decisão antes do Apply. Evidência: decisão explícita da responsável em 12/11/2026, registrada em `proposal.md` e `design.md`.
- [x] 1.2 Definir e implementar os contratos de leitura e catálogo com autenticação e validação de período/IDs no Xano; verificar com testes nativos Diretoria autorizada, demais perfis 403, sessão inválida 401 e entradas inválidas rejeitadas. Evidência: testes nativos de autorização e filtros, E2E Diretoria 200, anônimo 401 e entradas inválidas 400 em `evidencias.md`.

## 2. Disponibilidade

- [x] 2.1 Implementar no Xano a reconstrução dos intervalos por Totem, a primeira telemetria, o estado anterior a `t0`, o corte de 05/10/2026 e índices de leitura por Totem/timestamp; verificar com testes nativos intervalo cruzando cortes, Offline aberto e Totem sem observação. Evidência: testes nativos do cálculo e índices publicados, em `evidencias.md`.
- [x] 2.2 Implementar repartição por vínculo histórico de Loja e agregação ponderada da rede/Loja; verificar o exemplo `92/1.560 = 94,10%`, transferência entre Lojas e trecho sem vínculo comprovado. Evidência: testes nativos de ponderação, transferência e trecho sem vínculo, em `evidencias.md`.
- [x] 2.3 Implementar invalidação da disponibilidade por evento necessário inconsistente e as contagens da resposta; verificar que Totem e agregado afetado retornam valor indisponível, sem imputar Online. Evidência: testes nativos de evento inválido e agregado sem percentual, em `evidencias.md`.

## 3. MTTD, MTTR e série

- [x] 3.1 Implementar soma, contagem e média de MTTD por período e dia de detecção; verificar 18 e 20 minutos resultando em 19, limite de heartbeat incluído e evento inválido contado fora da média. Evidência: testes nativos de médias conhecidas e marcos ausentes, em `evidencias.md`.
- [x] 3.2 Implementar pares de recuperação e MTTR por período e dia de retorno; verificar 62 e 40 minutos resultando em 51, recuperação iniciada antes de `t0`, indisponibilidade aberta fora da média e Online sem timestamp contado como inconsistência na Loja histórica de `detectado_em`. Evidência: testes nativos de médias, período cruzado, Offline aberto e Loja histórica, em `evidencias.md`.
- [x] 3.3 Integrar totais e série diária numa resposta estável com valores nulos e motivos para dias sem dados; verificar que o total usa todos os eventos elegíveis, sem média das médias diárias, que a inconsistência Online sem timestamp aparece no total e dia de detecção, e que o XanoScript afetado passa na validação do Xano Developer MCP. Evidência: testes nativos da série e total, mensagens de ausência na página, sintaxe validada pelo MCP e E2E com 30 dias, em `evidencias.md`.

## 4. Página da Diretoria

- [x] 4.1 Criar cliente HTTP tipado e State para filtros, catálogos, carregamento e proteção de resposta tardia; verificar testes de contrato, alteração de filtros e falha sem métricas antigas. Evidência: `tests/test_indicadores_diretoria.py` (contrato, filtros, estado e falha) e `make check` em 12/11/2026.
- [x] 4.2 Criar `/indicadores/disponibilidade` com disponibilidade, evolução MTTD/MTTR, unidades e estados de vazio, erro e inconsistência; verificar testes de apresentação e compilação Reflex sem cálculo de indicadores no State. Evidência: testes de apresentação do State e compilação Reflex por `make check` em 12/11/2026.
- [x] 4.3 Adicionar `Indicadores` à navegação somente da Diretoria, com estado ativo e proteção da rota; verificar matriz dos quatro perfis, acesso direto e foco/semântica de navegação. Evidência: `tests/test_sidebar_global.py`, matriz de acesso direto em `tests/test_indicadores_diretoria.py` e `aria_current` existente em `app/components/layout.py`.
- [x] 4.4 Destacar os atalhos “Últimos 30 dias” e “Hoje” no cabeçalho, manter período personalizado e recortes de Loja/Totem, consultar somente ao clique e indicar o atalho ativo; verificar limites civis, preservação dos recortes, ausência de atualização automática e compilação Reflex. Evidência: `tests/test_indicadores_diretoria.py` (um request por clique, limites, recortes e personalizado), compilação Reflex e OpenSpec strict em `evidencias.md`.

## 5. Integração e evidências

- [x] 5.1 Executar testes Python relevantes e suíte completa, validação OpenSpec strict, compilação Reflex e `git diff --check`; registrar resultados e qualquer bloqueio de ambiente sem tratar não executado como aprovado. Evidência: `make check` (671 passed, 35 skipped por credenciais E2E ausentes; Reflex compilou), `openspec validate dashboard-disponibilidade-confiabilidade --strict` e `git diff --check` passaram em 12/11/2026.
- [x] 5.2 Validar XanoScript pelo Xano Developer MCP e executar testes nativos pelo Xano CLI, executar `xano workspace push --dry-run` e revisar o diff integral antes de publicação; após publicação autorizada, repetir dry-run e conferir que não restaram alterações fora do escopo. Evidência: nove arquivos válidos, 31 testes nativos sem falha e dry-run final limpo, em `evidencias.md`.
- [x] 5.3 Conferir contratos com dados conhecidos e, se houver credenciais autorizadas, com dados reais: resultados reproduzíveis, recortes históricos, contagens e tempo de resposta; registrar evidências sem credenciais nem dados sensíveis. Evidência: testes sintéticos nativos, quatro E2E com conta da Diretoria e medição pontual de latência, em `evidencias.md`.

## 6. Visão horária exclusiva de Hoje

- [x] 6.1 Estender o contrato autenticado com seleção explícita da visão Hoje, aceitando o intervalo do dia civil completo somente nessa visão e retornando o instante de observação efetiva; verificar rejeição de parâmetro inválido, período futuro fora de Hoje e período que não seja o dia atual completo. Evidência: testes nativos da função publicados e aprovados em 13/11/2026, em `evidencias.md`.
- [x] 6.2 Agregar disponibilidade ponderada em 24 posições horárias a partir dos fatos já consultados, com hora corrente parcial, horas futuras sem valor, Loja histórica e Totem aplicados e nulidade por ausência de observação ou histórico necessário inválido; verificar com testes nativos conjunto conhecido, transferência de Loja, Offline cruzando horas e invalidade localizada. Evidência: quatro testes nativos positivos publicados e aprovados em 13/11/2026, em `evidencias.md`.
- [x] 6.3 Atualizar cliente tipado, State e página: Hoje usa o gráfico horário de disponibilidade e período 00h–23h59, mantendo MTTD/MTTR como médias do dia; demais períodos mantêm a evolução diária. Verificar contrato de resposta, atualização por clique, filtros, estados vazios, apresentação de horas futuras e compilação Reflex. Evidência: 19 testes focados, `make check` e compilação Reflex em 13/11/2026, registrados em `evidencias.md`.
- [ ] 6.4 Executar OpenSpec strict, testes Python relevantes e suíte completa, validação XanoScript pelo Developer MCP, testes nativos, `git diff --check` e dry-run seletivo; registrar resultados, volume e latência real sem credenciais ou dados sensíveis.
- [ ] 6.5 Revisar o diff remoto completo e publicar somente após autorização de publicação; verificar por HTTP os dois modos, autorização, período inválido e dry-run final sem alterações fora do escopo.
