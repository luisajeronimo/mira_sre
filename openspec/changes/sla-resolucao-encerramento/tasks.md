# Tasks

## 1. Decisões e gates

- [x] 1.1 DS-1 aprovada: SLA em tempo corrido.
- [x] 1.2 DE-1 aprovada: 72 horas corridas após a entrada em `Resolvido`.
- [x] 1.3 DE-2 aprovada: sem encerramento em massa de chamados já resolvidos; regra técnica de vigência no design D3.
- [x] 1.4 DE-3 aprovada: comentário público de sistema no encerramento automático.
- [ ] 1.5 Decidir DE-3a (texto) e DE-3b (autor do comentário de sistema no DTO público).
- [ ] 1.6 Decidir DE-4 e DE-5 (mecanismo e frequência do job). Evidência para a decisão (2026-11-08, `xano workspace pull` somente leitura de 16:28): o workspace `152692` contém somente documentos `api`, `function`, `table` e `workspace`, sem nenhuma tarefa agendada; hoje não existe mecanismo que dispare o encerramento. A disponibilidade de tarefas agendadas no plano Free não foi verificada.
- [ ] 1.7 Decidir DE-6, DE-7 e DE-9. DE-8 decidida em 2026-11-08 (design D5).
- [ ] 1.8 Executar a prova E0.3 (DT-1) antes de 3.1 e obter aprovação do relatório. Em 2026-11-08 foi autorizado datasource próprio de teste no workspace `152692`, branch `v1`, como alternativa ao workspace separado; os registros são separados, mas schema e recursos publicados são compartilhados. Pacote e [plano de execução e rollback](../rejeicao-solucao-gerente/prova-e03/plano-execucao-rollback.md) preparados. **Não executado:** runtime, persistência e rollback continuam sem prova; o acesso à UI `app.xano.com` foi recusado pelo gate automático de navegador em 2026-11-08, e nenhum recurso remoto foi alterado.
- [ ] 1.9 Esclarecer as dependências externas "4", "5" e "D3" do planejamento.
- [ ] 1.10 Obter aprovação formal do Apply.

## 2. Xano — consumo de SLA

- [x] 2.1 Função somente leitura de linha do tempo e consumo (design D1–D2). Evidência: testes XanoScript dos exemplos e cenários do design (sem pausa, rejeição, múltiplas pausas, espera, `Encerrado` direto, `Cancelado`, troca de Categoria, linha do tempo inconsistente, limites de 70%, 90% e 100%); teste estático sem escrita.

> Progresso de 2.1 (2026-11-05 a 07, Apply local autorizado): `xano/function/service_desk/calcular_consumo_sla_chamado.xs` implementa D1–D2 somente para leitura, com entrada `chamados_id` e `instante_referencia` opcional (padrão: instante atual) e saída `{chamados_id, calculavel, motivo, consumo_ms, sla_horas_aplicado, fracao_consumida, faixa, estado_contagem, calculado_em}`; faixas do domínio §12. É **interna**: nenhum endpoint a chama, porque a exposição depende de DE-8. Possui 17 blocos `test` XanoScript (exemplo do design, sem pausa, múltiplas pausas, espera, `Encerrado`, `Cancelado`, linha do tempo inconsistente, status fora da lista, limites de 70%, 90% e 100%, sem SLA, sem `criado_em`, transição anterior à abertura, inexistente). Validação MCP: válida após substituir `num_min` e `num_max`, inexistentes no XanoScript, por condicionais. `tests/test_consumo_sla_xanoscript.py` (21 testes) recalcula os esperados com um modelo de referência das regras e verifica que a função é somente leitura e sem chamadores; a checagem de mutação detectou 3 de 3 valores alterados. **Runtime (2026-11-08, publicação autorizada):** dry-run imediatamente anterior com exatamente `+1 created` (`CREATE function service_desk/calcular_consumo_sla_chamado`), sem update nem remoção; publicação somente deste arquivo; dry-run posterior "No changes to push"; `xano workspace pull` confirmou `db.query chamados` e `db.query interacoes_chamado` reais (o aviso de referência não resolvida do push parcial era falso positivo). Os 17 testes nativos (função `358602`) passaram: **17/17 PASS**. A função continua interna, sem endpoint. **Aberta:** troca de Categoria é coberta somente por usar o `sla_horas_aplicado` vigente, sem teste dedicado. O motivo `ordem_temporal_inconsistente` (transição anterior a `criado_em`) é uma salvaguarda técnica para não somar intervalo negativo e precisa de confirmação na revisão.

> Atualização de 2026-11-08 (local, não publicada): 3 testes novos, totalizando 20 blocos `test`: "troca de categoria usa sla vigente" (SLA anterior de 8 h resultaria em `normal`; reinício na troca, em 1 h), "instante omitido usa o instante atual" e "instante zero e tratado como ausente" (achado M-4). A ausência de `instante_referencia` passa a ser reconhecida também quando o inteiro chega como 0, com o instante atual lido uma vez em `$agora` (mockável); a regra de cálculo não muda. Modelo de referência atualizado (26 testes locais) e verificação de mutação (remoção da guarda e alteração do instante mockado detectadas). **Não executado no Xano:** a versão publicada tem 17 testes (17/17 PASS); a nova exige publicação autorizada.

> Runtime (2026-11-08, publicação autorizada da atualização): dry-run `~1 updated` somente desta função; delta de lógica restrito a `$agora` e à guarda `$t == null || $t == 0`; dry-run posterior "No changes to push". Testes nativos **20/20 PASS** (os 17 anteriores, "troca de categoria usa sla vigente" com 4 asserções, "instante omitido usa o instante atual" com 4 e "instante zero e tratado como ausente" com 2). Mutações locais detectadas: SLA anterior na troca, remoção da guarda de zero e ausência convertida em 0. Observação para revisão, sem bloquear a task: o motivo `ordem_temporal_inconsistente` é salvaguarda técnica. A função segue interna; a exposição (DE-8) está na seção 6.

## 3. Xano — encerramento automático

- [ ] 3.1 Somente após 1.8: função e endpoint de automação (design D3). Evidência: elegível, prazo não vencido (71 h 59 min), limite exato de 72 h, fora da vigência na primeira execução, nova resolução após a vigência, comentário público de sistema criado, entrada desconhecida, rejeição concorrente simulada pela revalidação, execução repetida, credencial ausente ou inválida, perfil humano negado.
- [ ] 3.2 Validar no MCP, dry-run seletivo e publicação somente com aprovação.

## 4. Job

- [ ] 4.1 Implementar o job conforme DE-4 e DE-5, sem registrar credenciais. Evidência: testes Python com cliente simulado (sucesso, falha de rede, resposta inválida).
- [ ] 4.2 Documentar a variável de credencial em `.env.example` com placeholder, após aprovação.

## 5. Validação

- [ ] 5.1 Suíte completa, `openspec validate sla-resolucao-encerramento --strict` e `git diff --check`, com classificação dos resultados.
- [ ] 5.2 Teste integrado em ambiente autorizado; sem autorização, registrar como não executado.

## 6. Exposição do consumo (DE-8, design D5)

- [ ] 6.1 Contratos Xano por perfil (Técnico, Gerente pela Loja histórica, Administrador), sem campos de SLA para o solicitante. Evidência: testes nativos e de contrato para cada perfil, inclusive negação.
- [ ] 6.2 Apresentação no Reflex das situações do design D5 (dentro, próximo, vencido, pausado, encerrado, não calculável). Evidência: testes de State e página.
- [ ] 6.3 Indicadores do Gerente e da Diretoria, depois de DS-2 e DI-1 a DI-5.
