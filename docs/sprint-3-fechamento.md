# Fechamento técnico da Sprint 3 (26/10 a 08/11/2026)

Registro de 2026-11-08, branch `explore-monitoramento-xano` (PR #26). Evidências detalhadas ficam nas changes OpenSpec citadas; aqui ficam o inventário, a revisão de commits e o que depende de decisão.

## 1. Commits revisados

A equipe mencionou 30 commits. O histórico real tem:

- **PR #26:** 25 commits sobre `main` (24 commits e 1 merge).
- **Período da Sprint 3, alcançáveis pela branch:** 38 commits (35 sem merges), dos quais 13 já estavam em `main` antes do PR.

Os 38 foram revisados. Critério de incorporação: os arquivos introduzidos continuam em HEAD ou foram removidos de forma intencional e rastreável (arquivamento de change ou remoção registrada). A suíte local, o OpenSpec estrito e o CI passam no HEAD.

Classes: **C** correto e necessário; **CD** correto, documentação complementada depois; **DT** dependente de decisão técnica ou de ambiente; **R** redundante sem dano.

| Commit | Data | Autoria | Origem | Finalidade | Classe | Observação |
|---|---|---|---|---|---|---|
| `96a144b` | 29/10 | Luisa Lima | main | Complementos de consulta e detalhe de chamados | C | Arquivos da change removidos ao arquivar (`8df737a`) |
| `8df737a` | 29/10 | Luisa Lima | main | Arquiva a change acima | C | — |
| `ce44e5c` | 01/11 | Luisa Lima | main | Padronização visual | C | Change arquivada em `eab46c5` |
| `eab46c5` | 01/11 | Luisa Lima | main | Arquiva a padronização visual | C | — |
| `af99dc9` | 01/11 | Luisa Jeronimo | main | Merge do PR #24 | C | — |
| `19a2deb` | 02/11 | Luisa Lima | main | Automações mock em paralelo (`make mock`) | C | Limitação no Windows documentada no README |
| `84f8c03` | 02/11 | Luisa Lima | main | Aquecimento antes do Fiscal | C | — |
| `97125a8` | 02/11 | Luisa Lima | main | Visibilidade de comentários e filtros múltiplos | C | Remove `reflex.lock/package-lock.json` de propósito; change arquivada em `fde3603` |
| `fde3603` | 02/11 | Luisa Lima | main | Arquiva a change acima | C | — |
| `06cc763` | 02/11 | Luisa Jeronimo | main | Merge do PR #25 (base do PR #26) | C | — |
| `38e487d` | 06/11 | Luisa Lima | main | Melhorias pontuais; change arquivada | C | — |
| `d75db38` | 08/11 | Luisa Lima | main | Gestão administrativa (lojas, usuários, Totens, abertura administrativa) | C | Versionou de forma independente os mesmos objetos da Loja histórica que o PR; conciliado em `b19d4b4` |
| `c12e417` | 08/11 | Isabelly Garcia | PR | Suporte a Windows (`tzdata`, documentação) | C | Completado por `a74d1cb` |
| `3eaebd8` | 08/11 | Isabelly Garcia | PR | AGENTS.md exige o MCP nas validações que dependem dele | C | — |
| `62bc41a` | 08/11 | Isabelly Garcia | PR | Change `regularizar-loja-historica-totem` | C | Deltas ajustados à base de `main` em `b19d4b4` |
| `1f27556` | 08/11 | Isabelly Garcia | PR | Change do acompanhamento do solicitante | CD | Cópias inativas em `referencias/` removidas em `1243ea8` |
| `6a82bb5` | 08/11 | Isabelly Garcia | PR | Change da rejeição de solução | DT | Implementação depende da E0.3 (DT-1) |
| `749b5cc` | 08/11 | Isabelly Garcia | PR | Changes de SLA, encerramento e indicadores | DT | Decisões DE, DI, DS-2 e DR (seção 3) |
| `b453e1b` | 08/11 | Isabelly Garcia | PR | Visão do produto e domínio | CD | Deriva corrigida em `1243ea8` e no merge |
| `92de6f9` | 08/11 | Isabelly Garcia | PR | README da Sprint 3 | CD | Corrigido em `1243ea8` e depois |
| `77badc0` | 08/11 | Isabelly Garcia | PR | CI em Linux | C | Passou a executar quando os conflitos foram resolvidos |
| `63f864d` | 08/11 | Isabelly Garcia | PR | Versiona a leitura da Loja histórica publicada | C | — |
| `9276048` | 08/11 | Isabelly Garcia | PR | Versiona os contratos do solicitante e do histórico | C | Validados por HTTP autenticado em 08/11 |
| `107f75a` | 08/11 | Isabelly Garcia | PR | Teste de coerência do pacote da prova E0.3 | DT | A prova não foi executada (sem ambiente isolado) |
| `6afb174` | 08/11 | Isabelly Garcia | PR | Reconcilia contratos publicados (Loja ativa) | C | — |
| `a74d1cb` | 08/11 | Isabelly Garcia | PR | `make py_test` e `reflex_check` no Windows | C | — |
| `ef7d883` | 08/11 | Isabelly Garcia | PR | `AUTENTICACAO.md` marcado como histórico | C | — |
| `374ecf6` | 08/11 | Isabelly Garcia | PR | Prepara a validação das escritas e registra a ausência de job | C | — |
| `64f2790` | 08/11 | Luisa Lima | main | Alinha os GETs genéricos de interações ao Xano | R | Equivalente ao Pacote A do PR (diferença só de layout); conciliado no merge |
| `c9ede3c` | 08/11 | Isabelly Garcia | PR | Versiona as escritas da Loja histórica | DT | Atomicidade depende da E0.3 (DL-3). Criou `ativos_historicos_GET.xs`, duplicando `ativos-historicos_GET.xs` de `d75db38` (mesmo objeto); duplicação removida em `9808756`, com teste de regressão |
| `d16ae19` | 08/11 | Isabelly Garcia | PR | Publica o consumo de SLA | C | Testes complementados em `9e1fea6` |
| `f861306` | 08/11 | Isabelly Garcia | PR | Versiona o detalhe de monitoramento | C | O UPDATE persistente do dry-run é artefato do CLI |
| `b19d4b4` | 08/11 | Isabelly Garcia | PR | Merge de `main`, com os 28 conflitos resolvidos | C | Justificativa por arquivo em `corrigir-gerente-gets-genericos-loja-historica/integracao-main.md` |
| `fc2c696` | 08/11 | Isabelly Garcia | PR | Versiona as quatro funções publicadas | CD | Exceção do alias `tecnico_usuario` documentada |
| `a385c1e` | 08/11 | Isabelly Garcia | PR | Correção C-1 (GETs genéricos pela Loja histórica) | C | Publicada; testes nativos 7/7 e E2E 6/6 |
| `9e1fea6` | 08/11 | Isabelly Garcia | PR | Testes de troca de Categoria e instante padrão no SLA | C | Publicado; testes nativos 20/20 |
| `1243ea8` | 08/11 | Isabelly Garcia | PR | Alinha README e OpenSpec; DE-8 registrada | C | — |
| `499f298` | 08/11 | Isabelly Garcia | PR | Evidências da publicação da C-1 e do SLA | C | — |

Commits posteriores à revisão: `dc0cdb7` (E2E da C-1 e DTO do Técnico), `3a1004c` (interface do solicitante integrada e desligada), `e665615` (este documento) e `9808756` (remoção do documento Xano duplicado). Nenhum commit foi classificado como problemático ou incompleto sem tratamento. Os itens **DT** dependem dos bloqueios da seção 3, e nenhum foi reescrito.

## 2. Entregas da Sprint 3

| Entrega | Situação | Evidência |
|---|---|---|
| Loja histórica do Totem (leitura) | Publicada e versionada | Testes nativos; E2E de isolamento |
| Correção C-1 nos GETs genéricos de `chamados` | Publicada | Testes nativos 7/7 e 4/4; E2E autenticado 6/6 |
| Contratos do solicitante e do histórico de status | Publicados | Testes nativos; E2E Pacote B 11/11 |
| Interface do solicitante e seção de histórico (Reflex) | Integrada ao repositório, desligada | Testes de State e páginas; ligar depende da K-B (5.8) |
| Consumo de SLA em tempo corrido (função interna) | Publicado | Testes nativos 20/20 |
| Gestão administrativa (de `main`) | Integrada | Suíte local; CI |
| Escritas da Loja histórica (abertura manual, heartbeat, transferência, `totens`) | Publicadas, versionadas | Testes nativos com mock 14/14; sem HTTP de escrita nem prova de atomicidade |
| Exposição do SLA por perfil (DE-8) | Decidida, não implementada | Design D5 e tasks 6.x de `sla-resolucao-encerramento` |
| Rejeição de solução e encerramento automático de 72 h | Especificados, não implementados | Dependem da E0.3 e de DE-3a/b, DE-4 a DE-7 e DE-9 |
| Indicadores (disponibilidade, MTTD, MTTR, cumprimento, recorrência) | Especificados, não implementados | Dependem de DI-1 a DI-5, DS-2 e DR-1 a DR-3 |

## 3. Bloqueios e decisões necessárias

Nenhuma destas decisões foi tomada nesta revisão. A coluna "alternativa mais segura" repete a recomendação já registrada nas changes ou aponta a opção que não altera dados nem contratos publicados.

| Item | Decisão ou bloqueio | Alternativa mais segura | Menor ação para destravar |
|---|---|---|---|
| E0.3 | Ambiente isolado para provar o rollback | Não executar no workspace compartilhado | Autorizar um ambiente isolado (plano pago ou workspace separado) |
| DL-1 | Legados sem vínculo fora da jornada do Gerente | Aceitar o estado atual (sem backfill) | Aceite formal |
| DL-2 | Texto da Loja nula | Manter "Não informado" | Confirmar o texto |
| DL-3 | Escritas dependentes sem a E0.3 | Manter as publicadas e não criar novas até a prova | Aceite do risco ou executar a E0.3 |
| DL-4 | Quem vê o histórico de vínculos | Manter Gerente (rota publicada) e Administrador | Confirmar e especificar |
| DL-5 | Chamados removidos e interações órfãs | Não alterar dados | Autorização própria de tratamento de dados |
| 2.2–2.3 e K-B | Dados de teste com comentários na Loja do Gerente | Não criar dados no workspace compartilhado | Autorizar a criação de dados de teste ou indicar um chamado existente |
| DE-3a/b | Texto e autor do comentário de sistema | Texto proposto; `autor = null` | Aprovar |
| DE-4/DE-5 | Mecanismo e frequência do job | Script Python no padrão do Fiscal, a cada 15 min | Aprovar |
| DE-6 | `Aguardando Terceiro` | Manter não calculável | Decidir |
| DE-7 | Encerramento manual pelo Save | Manter | Confirmar |
| DE-9 | Início de vigência | Constante versionada definida no Apply | Decidir |
| DI-1 a DI-5 | Marcos e agregação dos indicadores | Recomendações registradas em `indicadores-governanca-formulas` | Aprovar |
| DS-2 | Base do cumprimento de SLA | Excluir `Cancelado` | Aprovar |
| DR-1 a DR-3 | Recorrência | Totem; somente `Incidente` sem `Cancelado`; janela a decidir | Escolher a janela e confirmar o resto |
| DE-8 | Formato dos contratos de exposição | Consultas próprias e aditivas por perfil, sem alterar DTOs validados de forma estrita pelo Reflex | Apply da seção 6 de `sla-resolucao-encerramento` |
| M-3 | Desempenho das listas do Gerente | Pré-filtro por Totens candidatos, com equivalência provada | Validação MCP e publicação autorizada |
| MCP | Validação pelo Xano Developer MCP | Não simular | Sessão com o MCP disponível |
