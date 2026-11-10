# Sprint 3 — publicação e validação antes do Archive

Registro em 10/11/2026. A decisão humana autorizou push seletivo ao Xano, uso das quatro contas E2E, criação de dados de teste e conclusão do Apply até antes do Archive. Este registro separa observação de runtime, validação local e pendências.

## Publicação Xano

- Publicados seletivamente os contratos de rejeição pelo Gerente, consumo de SLA por Gerente/Técnico, encerramento sob comando e projeção de comentário de Sistema. A atualização do detalhe do solicitante retirou `sla_horas_aplicado`. O arquivo de monitoramento que apareceu no dry-run geral ficou fora do pacote.
- XanoScript afetado validado no Xano Developer MCP. Antes de cada push, a prévia seletiva foi inspecionada; após cada push, o novo dry-run retornou `No changes to push` para os arquivos aprovados. Correções posteriores na rejeição e na projeção de comentários seguiram o mesmo ciclo.
- A versão da função de encerramento publicada fixa a vigência em `1794181165000` (`08/11/2026 23:39:25 UTC`). Chamados resolvidos antes dela não entram no encerramento por prazo. Não houve publicação de `workflow_test` nem de recurso pago.

## Testes observados

| Verificação | Resultado | Alcance |
| --- | --- | --- |
| Testes nativos XanoScript | **Passou** | Consumo de SLA, histórico, contratos de solicitante, projeção de comentários e sete testes da rejeição publicada (7/7 em 10/11). Nenhuma conclusão de persistência/rollback é inferida dos mocks. |
| E2E HTTP com quatro perfis | **Passou**, 31/31 | Isolamento de interações, contratos de solicitante, histórico, consumo de SLA, negação de rejeição a outros perfis e negação de chave ausente/inválida. |
| Rejeição real do chamado 97 | **Passou** | `422` para justificativa vazia, `409` para versão obsoleta, `200` na rejeição autorizada; status, comentário público, histórico e nova rejeição `409` verificados depois. |
| Reflex em navegador | **Passou** no fluxo observado | Gerente: detalhe, consumo pausado de SLA, ação de rejeição e histórico. Solicitante: lista, detalhe somente leitura, comentários públicos e histórico; nota interna omitida. Um erro transitório de carregamento do histórico foi recuperado ao recarregar. |
| Chave válida do comando no Xano | **Bloqueado por configuração remota** | Chave gerada e guardada somente no `.env` ignorado. A prévia CLI com `--env` não detectou atualização da variável do workspace; a configuração remota ainda precisa ser confirmada. Chave ausente e inválida retornaram `401` em runtime. |
| Encerramento real de um chamado elegível | **Não executado** | O chamado 98 ainda não completou 72 horas em 10/11/2026. Conservar `Resolvido` e executar depois do prazo, com a chave remota configurada. |
| Prova E0.3 de persistência e rollback | **Bloqueado por plano; limitação aceita** | A API do Xano Free rejeitou `workflow_test` com exigência de upgrade pago. A responsável aceitou prosseguir sem essa prova em runtime em 08/11/2026. |

Validação local final em 10/11/2026: `pytest -q` **658 passaram, 31 pulados** (E2E sem credenciais no ambiente local); os mesmos E2E foram executados separadamente com credenciais e **31/31 passaram**. `reflex compile --dry` **passou** com K-B ligado e desligado. `openspec validate --strict` **passou** nas quatro changes ativas da Sprint 3. `git diff --check` **passou**. A suíte inicialmente revelou quatro expectativas da matriz de navegação que ainda assumiam o gate desligado por padrão; os testes foram corrigidos para fixar explicitamente o gate desligado, e a suíte foi repetida sem falhas.

Os chamados de teste persistidos são **97** (`Solução Rejeitada`, prova real), **98** (`Resolvido`, reservado para encerramento após 72 horas) e **99** (`Resolvido`, reservado para rejeição manual). Todos têm título com `[MIRA E2E SPRINT 3]`. O 98 tem comentário público de resolução e nota interna para verificar o isolamento. O roteiro de verificação humana está em [sprint3-roteiro-teste-frontend.md](./sprint3-roteiro-teste-frontend.md).

## Revisão documental e limites

- `docs/project-overview.md` descreve acompanhamento e rejeição pelo Gerente de forma compatível com as changes ativas. `docs/domain-model.md` continha uma frase antiga que colocava a rejeição pelo Gerente na visão futura; ela foi alinhada à regra aprovada, mantendo o aceite pelo solicitante como futuro.
- O encerramento no limite exato de 72 horas, a idempotência em runtime e o comentário real de Sistema ainda dependem da passagem do prazo e da chave configurada no Xano. Testes nativos e locais cobrem a lógica, mas não substituem essa observação HTTP.
- Os indicadores de Gerente e Diretoria continuam na change `indicadores-governanca-formulas`; não foram incluídos neste pacote de interface.
- **Archive não executado.** A revisão final das changes e a consolidação das specs devem ocorrer depois do teste manual e da classificação das pendências.
