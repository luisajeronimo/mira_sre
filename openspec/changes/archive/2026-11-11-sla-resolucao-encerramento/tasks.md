# Tasks

> Encerramento do Apply por decisão humana em 11/11/2026: as tasks 3.1, 5.2 e 6.3 foram fechadas com dispensa das provas ou da entrega restante. O `[x]` registra a decisão de escopo, não comprova encerramento elegível em runtime nem entrega indicadores. Archive não autorizado.

## 1. Decisões e gates

- [x] 1.1 DS-1 aprovada: SLA em tempo corrido.
- [x] 1.2 DE-1 aprovada: 72 horas corridas após a entrada em `Resolvido`.
- [x] 1.3 DE-2 aprovada: sem encerramento em massa de chamados já resolvidos; regra técnica de vigência no design D3.
- [x] 1.4 DE-3 aprovada: comentário público de sistema no encerramento automático.
- [x] 1.5 DE-3a e DE-3b aprovadas: texto exato do comentário público registrado no design D3 e autor `Sistema` no DTO público.
- [x] 1.6 DE-4 e DE-5 revistas: disparo manual único por `make encerrar-resolvidos`, script Python que chama a API; sem job periódico, frequência ou agendamento. O Xano decide e executa o encerramento.
- [x] 1.7 DE-7 aprovada: preservar encerramento manual pelo Save; DE-9 aprovada: constante versionada de vigência, fixada na publicação; DE-8 já decidida (design D5). Nenhum trabalho adicional sobre status legado fora da lista canônica.
- [x] 1.8 Resolver o gate E0.3 (DT-1) antes de 3.1. Em 2026-11-08 a API do Xano recusou `workflow_test` com `Please upgrade to access workflow tests`; a responsável aceitou formalmente a limitação funcional no plano Free para prosseguir. **Bloqueado por restrição de ambiente/plano:** runtime, persistência e rollback não foram comprovados. Pacote, validação estática e [plano de execução e rollback](../rejeicao-solucao-gerente/prova-e03/plano-execucao-rollback.md) registrados sem publicar recursos temporários.
- [x] 1.9 Esclarecer as referências externas "4", "5" e "D3" do planejamento. Em 11/11/2026, a responsável confirmou que não há fonte disponível; o significado permanece desconhecido e não é usado para ampliar ou bloquear o escopo aprovado. Registro em `proposal.md`.
- [x] 1.10 Apply autorizado pela responsável ao pedir execução até antes do Archive, com uso do Xano MCP e CLI e escopo acadêmico. Archive permanece fora desta autorização.

## 2. Xano — consumo de SLA

- [x] 2.1 Função somente leitura de linha do tempo e consumo (design D1–D2). Evidência: testes XanoScript dos exemplos e cenários do design (sem pausa, rejeição, múltiplas pausas, espera, `Encerrado` direto, `Cancelado`, troca de Categoria, linha do tempo inconsistente, limites de 70%, 90% e 100%); teste estático sem escrita.

> Progresso de 2.1 (2026-11-05 a 07, Apply local autorizado): `xano/function/service_desk/calcular_consumo_sla_chamado.xs` implementa D1–D2 somente para leitura, com entrada `chamados_id` e `instante_referencia` opcional (padrão: instante atual) e saída `{chamados_id, calculavel, motivo, consumo_ms, sla_horas_aplicado, fracao_consumida, faixa, estado_contagem, calculado_em}`; faixas do domínio §12. É **interna**: nenhum endpoint a chama, porque a exposição depende de DE-8. Possui 17 blocos `test` XanoScript (exemplo do design, sem pausa, múltiplas pausas, espera, `Encerrado`, `Cancelado`, linha do tempo inconsistente, status fora da lista, limites de 70%, 90% e 100%, sem SLA, sem `criado_em`, transição anterior à abertura, inexistente). Validação MCP: válida após substituir `num_min` e `num_max`, inexistentes no XanoScript, por condicionais. `tests/test_consumo_sla_xanoscript.py` (21 testes) recalcula os esperados com um modelo de referência das regras e verifica que a função é somente leitura e sem chamadores; a checagem de mutação detectou 3 de 3 valores alterados. **Runtime (2026-11-08, publicação autorizada):** dry-run imediatamente anterior com exatamente `+1 created` (`CREATE function service_desk/calcular_consumo_sla_chamado`), sem update nem remoção; publicação somente deste arquivo; dry-run posterior "No changes to push"; `xano workspace pull` confirmou `db.query chamados` e `db.query interacoes_chamado` reais (o aviso de referência não resolvida do push parcial era falso positivo). Os 17 testes nativos (função `358602`) passaram: **17/17 PASS**. A função continua interna, sem endpoint. **Aberta:** troca de Categoria é coberta somente por usar o `sla_horas_aplicado` vigente, sem teste dedicado. O motivo `ordem_temporal_inconsistente` (transição anterior a `criado_em`) é uma salvaguarda técnica para não somar intervalo negativo e precisa de confirmação na revisão.

> Atualização de 2026-11-08 (local, não publicada): 3 testes novos, totalizando 20 blocos `test`: "troca de categoria usa sla vigente" (SLA anterior de 8 h resultaria em `normal`; reinício na troca, em 1 h), "instante omitido usa o instante atual" e "instante zero e tratado como ausente" (achado M-4). A ausência de `instante_referencia` passa a ser reconhecida também quando o inteiro chega como 0, com o instante atual lido uma vez em `$agora` (mockável); a regra de cálculo não muda. Modelo de referência atualizado (26 testes locais) e verificação de mutação (remoção da guarda e alteração do instante mockado detectadas). **Não executado no Xano:** a versão publicada tem 17 testes (17/17 PASS); a nova exige publicação autorizada.

> Runtime (2026-11-08, publicação autorizada da atualização): dry-run `~1 updated` somente desta função; delta de lógica restrito a `$agora` e à guarda `$t == null || $t == 0`; dry-run posterior "No changes to push". Testes nativos **20/20 PASS** (os 17 anteriores, "troca de categoria usa sla vigente" com 4 asserções, "instante omitido usa o instante atual" com 4 e "instante zero e tratado como ausente" com 2). Mutações locais detectadas: SLA anterior na troca, remoção da guarda de zero e ausência convertida em 0. Observação para revisão, sem bloquear a task: o motivo `ordem_temporal_inconsistente` é salvaguarda técnica. A função segue interna; a exposição (DE-8) está na seção 6.

## 3. Xano — encerramento sob comando

- [x] 3.1 Manter a função e o endpoint de encerramento sob comando manual (design D3) já publicados. A responsável dispensou em 11/11/2026 a matriz adicional de limites de prazo, vigência, revalidação, repetição e comentário em runtime. Testes nativos e locais existentes e 401 HTTP sem chave ou com chave inválida permanecem como evidência parcial. **Chave válida, encerramento elegível, comentário persistido, repetição e rollback não foram comprovados em runtime.**
- [x] 3.2 Validar no MCP, dry-run seletivo e publicação somente com aprovação. Função e endpoint foram publicados seletivamente após validação MCP e prévia revisada; o dry-run posterior ficou limpo. A constante de vigência publicada é `1794181165000`. Ver [registro de validação](../../../docs/sprint3-validacao-publicacao-2026-11-10.md).

> Histórico de 3.1 (10/11/2026): função e endpoint estão publicados; testes locais e nativos cobrem a lógica de seleção, vigência, prazo, revalidação, comentário e evento. Em HTTP real, chave ausente ou inválida retorna `401`. A chave válida não foi confirmada no ambiente Xano e nenhum chamado de teste completou 72 horas para observar o encerramento, o comentário e a repetição em runtime. A prova E0.3 de rollback segue como limitação aceita, sem ser marcada como passou.

## 4. Comando manual

- [x] 4.1 `scripts/encerrar_resolvidos.py` e alvo `make encerrar-resolvidos` implementados para uma chamada única, sem loop e sem registrar credencial. Evidência: `tests/test_encerrar_resolvidos_comando.py`, 6/6 passaram em 2026-11-08 (sucesso, falha de rede, resposta inválida e chamada única). Endpoint real publicado em 2026-11-08; a execução com chave válida aguarda configuração remota.
- [x] 4.2 `.env.example` contém `MIRA_ENCERRAMENTO_AUTOMATION_KEY` vazio e timeout seguro, sem segredo versionado.

## 5. Validação

- [x] 5.1 Suíte completa, `openspec validate sla-resolucao-encerramento --strict` e `git diff --check`, com classificação dos resultados. Em 2026-11-08: pytest **passou** (652 passaram, 26 E2E pulados), OpenSpec strict **passou**, diff check **passou**.
- [x] 5.2 Registrar dispensa do teste integrado positivo por decisão da responsável em 11/11/2026. **Parcial:** E2E HTTP com quatro perfis passou para consumo e autenticação negativa do comando; chave válida e encerramento de chamado elegível **não executados**, conforme [registro de validação](../../../docs/sprint3-validacao-publicacao-2026-11-10.md).

## 6. Exposição do consumo (DE-8, design D5)

- [x] 6.1 Contratos Xano por perfil (Técnico, Gerente pela Loja histórica, Administrador), sem campos de SLA para o solicitante. Evidência: testes locais de contrato e E2E HTTP com quatro perfis, incluindo negação a Diretoria, solicitante sem campo de SLA e Gerente fora da Loja; testes nativos da função de cálculo passaram.
- [x] 6.2 Apresentação no Reflex das situações do design D5 (dentro, próximo, vencido, pausado, encerrado, não calculável). Evidência: `tests/test_frontend_sprint3.py` para seis combinações de faixa/estado, não calculável e carregamento no State; compilação com K-B ligado e desligado e inspeção visual de SLA pausado no chamado 98.
- [x] 6.3 Registrar exclusão dos indicadores do Gerente e da Diretoria deste Apply por decisão da responsável em 11/11/2026. **Não implementados**; fórmulas aprovadas em `indicadores-governanca-formulas`, mas consultas e dashboards dependem de change própria e não são declarados entregues.
- [x] 6.4 Implementar a revisão de layout de 10/11/2026: substituir o card de consumo no detalhe de Gerente/Técnico/Administrador por botão de informação junto a "SLA aplicado", com popover acessível, estados de carregamento/erro e os valores autorizados. `reflex compile --dry` passou em 11/11/2026. **Inspeção visual não executada por instrução explícita da responsável em 11/11/2026; não é registrada como validação aprovada.**

> Evidência de 6.4 em 11/11/2026: o detalhe de Gerente e o detalhe compartilhado de Técnico/Administrador usam `campo_sla_com_consumo` ao lado do rótulo "SLA aplicado"; o card separado foi removido. O controle tem rótulo acessível, foco visível e estados de carregamento, erro e dados retornados. `reflex compile --dry` **passou**; 64 testes focados de frontend/sidebar **passaram**. A inspeção renderizada foi dispensada pela responsável após o host do navegador conectado se mostrar indisponível.
