# Tasks

## 1. Decisões e gates

- [x] 1.1 DS-1 aprovada: SLA em tempo corrido.
- [x] 1.2 DE-1 aprovada: 72 horas corridas após a entrada em `Resolvido`.
- [x] 1.3 DE-2 aprovada: sem encerramento em massa de chamados já resolvidos; regra técnica de vigência no design D3.
- [x] 1.4 DE-3 aprovada: comentário público de sistema no encerramento automático.
- [ ] 1.5 Decidir DE-3a (texto) e DE-3b (autor do comentário de sistema no DTO público).
- [ ] 1.6 Decidir DE-4 e DE-5 (mecanismo e frequência do job). Evidência para a decisão (2026-11-08, `xano workspace pull` somente leitura de 16:28): o workspace `152692` contém somente documentos `api`, `function`, `table` e `workspace`, sem nenhuma tarefa agendada; hoje não existe mecanismo que dispare o encerramento. A disponibilidade de tarefas agendadas no plano Free não foi verificada.
- [ ] 1.7 Decidir DE-6, DE-7, DE-8 e DE-9.
- [ ] 1.8 Obter autorização de ambiente isolado e executar a prova E0.3 (DT-1) antes de 3.1. Investigação de 2026-11-05 ([validacao-xano-2026-11.md](../acompanhamento-solicitante-historico-status/validacao-xano-2026-11.md)): `xano sandbox` exige plano pago; `xano ephemeral` cria tenant dentro do workspace compartilhado `152692`, o único da conta. Nenhum ambiente criado; segue bloqueada por ambiente. Pacote de prova preparado em 2026-11-07: [prova-e03/](../rejeicao-solucao-gerente/prova-e03/README.md) (tabela, funções e teste de workflow com a matriz `db.add`, `db.patch`, `function.run`, duas escritas e tipos de erro; concorrência não coberta). Validação estática MCP: 4/4; teste local de coerência: `tests/test_prova_e03_pacote.py`. **Não executado:** runtime, persistência e rollback continuam sem prova.
- [ ] 1.9 Esclarecer as dependências externas "4", "5" e "D3" do planejamento.
- [ ] 1.10 Obter aprovação formal do Apply.

## 2. Xano — consumo de SLA

- [ ] 2.1 Função somente leitura de linha do tempo e consumo (design D1–D2). Evidência: testes XanoScript dos exemplos e cenários do design (sem pausa, rejeição, múltiplas pausas, espera, `Encerrado` direto, `Cancelado`, troca de Categoria, linha do tempo inconsistente, limites de 70%, 90% e 100%); teste estático sem escrita.

> Progresso de 2.1 (2026-11-05 a 07, Apply local autorizado): `xano/function/service_desk/calcular_consumo_sla_chamado.xs` implementa D1–D2 somente para leitura, com entrada `chamados_id` e `instante_referencia` opcional (padrão: instante atual) e saída `{chamados_id, calculavel, motivo, consumo_ms, sla_horas_aplicado, fracao_consumida, faixa, estado_contagem, calculado_em}`; faixas do domínio §12. É **interna**: nenhum endpoint a chama, porque a exposição depende de DE-8. Possui 17 blocos `test` XanoScript (exemplo do design, sem pausa, múltiplas pausas, espera, `Encerrado`, `Cancelado`, linha do tempo inconsistente, status fora da lista, limites de 70%, 90% e 100%, sem SLA, sem `criado_em`, transição anterior à abertura, inexistente). Validação MCP: válida após substituir `num_min` e `num_max`, inexistentes no XanoScript, por condicionais. `tests/test_consumo_sla_xanoscript.py` (21 testes) recalcula os esperados com um modelo de referência das regras e verifica que a função é somente leitura e sem chamadores; a checagem de mutação detectou 3 de 3 valores alterados. **Aberta:** os blocos `test` exigidos como evidência não foram executados no runtime Xano. Troca de Categoria é coberta somente por usar o `sla_horas_aplicado` vigente, sem teste dedicado. O motivo `ordem_temporal_inconsistente` (transição anterior a `criado_em`) é uma salvaguarda técnica para não somar intervalo negativo e precisa de confirmação na revisão.

## 3. Xano — encerramento automático

- [ ] 3.1 Somente após 1.8: função e endpoint de automação (design D3). Evidência: elegível, prazo não vencido (71 h 59 min), limite exato de 72 h, fora da vigência na primeira execução, nova resolução após a vigência, comentário público de sistema criado, entrada desconhecida, rejeição concorrente simulada pela revalidação, execução repetida, credencial ausente ou inválida, perfil humano negado.
- [ ] 3.2 Validar no MCP, dry-run seletivo e publicação somente com aprovação.

## 4. Job

- [ ] 4.1 Implementar o job conforme DE-4 e DE-5, sem registrar credenciais. Evidência: testes Python com cliente simulado (sucesso, falha de rede, resposta inválida).
- [ ] 4.2 Documentar a variável de credencial em `.env.example` com placeholder, após aprovação.

## 5. Validação

- [ ] 5.1 Suíte completa, `openspec validate sla-resolucao-encerramento --strict` e `git diff --check`, com classificação dos resultados.
- [ ] 5.2 Teste integrado em ambiente autorizado; sem autorização, registrar como não executado.
