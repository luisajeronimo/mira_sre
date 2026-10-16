# Tasks

## 1. Contratos e dados da tratativa

- [x] 1.1 Definir no Xano o schema aditivo e o DTO canônico de `alteracao_chamado`, com pares anterior/resultante e compatibilidade de leitura de comentários e eventos legados; verificar CONTRACT, XANO e UNIT sem backfill.
- [ ] 1.2 Implementar o catálogo autenticado de Categorias ativas para edição e o contrato do detalhe que conserva Categoria atual inativa; verificar CONTRACT, XANO e REST_AUTH contra Categoria ativa e inativa.

## 2. Save transacional no Xano

- [ ] 2.1 Implementar o contrato único de Save para Responsável, Status, Prioridade e Categoria, com lista canônica de valores, validação de Técnico responsável, comparação simples de `ultima_atualizacao_em` e detalhe canônico pós-commit; verificar UNIT, CONTRACT e XANO.
- [ ] 2.2 Persistir em uma mesma transação as diferenças funcionais, `atribuido_em`, SLA decorrente de Categoria, comentário obrigatório, exatamente um `alteracao_chamado` por Save efetivo e `ultima_atualizacao_em`; verificar XANO e PERSISTENCE com Save combinado válido.
- [ ] 2.3 Cobrir rollback de validação, falha de persistência, Save sem diferença funcional e proteção otimista simples: carregar detalhe, alterar o mesmo chamado por outra operação, salvar com `ultima_atualizacao_em` antigo e recarregar; verificar PERSISTENCE que não há campo, comentário, evento nem timestamp parcial. UNIT isolado não conclui esta tarefa. **BLOQUEADA por decisão humana:** o ambiente Xano Free não oferece isolamento seguro para injeção real de falha após escrita; não criar hook, endpoint ou função temporária no workspace live. Permanecem como evidência parcial os mocks de falha de patch/comentário/auditoria, XanoScript válido, Save sem diferença, atribuição/liberação persistentes e conflito otimista real sem efeito parcial.
- [x] 2.4 Validar no Xano status terminal, Encerrado manual, Cancelado com mudanças combinadas e rejeição de Aguardando Terceiro; verificar CONTRACT, XANO e PERSISTENCE.

## 3. Comentários e autorização

- [x] 3.1 Implementar comentário operacional independente Público/Interno para Técnico, Diretoria e Administrador, inclusive em terminal, com atualização de `ultima_atualizacao_em`; verificar UNIT, XANO e PERSISTENCE.
- [x] 3.2 Ajustar o comentário Público do Gerente para terminal dentro da Loja e jornada já autorizadas, sem conceder comentário Interno, fila global ou edição funcional; verificar CONTRACT, XANO e REST_AUTH para escopo próprio e negado. **Evidência aceita por decisão humana:** REST_AUTH foi comprovado somente na jornada real autenticada do Gerente (comentário Público não terminal e terminal, escopo por Loja e entrada vazia). A negação de `visibilidade=interna` foi comprovada por CONTRACT e XANO live antes da transação, sem REST_AUTH específico, pois a jornada normal não produz esse payload e não foi autorizado criar mecanismo artificial para exercitá-lo.
- [ ] 3.3 Aplicar no Xano a matriz de autorização da tratativa para Técnico, Diretoria e Administrador e manter CRUD genérico negado; verificar XANO e REST_AUTH com 401, 403 e cada perfil.

## 4. Reflex: edição pendente e comentário

- [ ] 4.1 Adaptar service e DTOs Python ao catálogo, Save e detalhe pós-commit, preservando o cliente autenticado da fila e a diferenciação 401, 403, 404, 422 e 5xx; verificar UNIT e CONTRACT sem usar valores vazios para mascarar incompatibilidade.
- [ ] 4.2 Implementar no State e detalhe Reflex valores persistidos e pendentes para os quatro campos, dropdown `Responsável`, `Descartar mudanças`, `Salvar` e comentário de Status obrigatório; verificar UNIT e REFLEX que dropdown não persiste antes do Save, Status pendente exige comentário com Público fixo nos destinos definidos e erro não confirma rascunho.
- [ ] 4.3 Substituir os controles imediatos de responsável pela edição pendente sem modificar a fila, Todos, Atribuídos a mim, filtros ou pesquisa; verificar REFLEX com Técnico, Diretoria e Administrador, ausência dos controles separados e inexistência de caminho funcional alternativo ao Save.
- [ ] 4.4 Implementar comentário independente, validação visual de texto/visibilidade e apresentação discriminada de comentário, eventos legados e `alteracao_chamado` na timeline decrescente; verificar UNIT, CONTRACT e REFLEX.

## 5. Integração autenticada e persistência real

- [ ] 5.1 Sincronizar somente recursos Xano aprovados após validação de XanoScript e dry-run, e executar o endpoint REST autenticado real do Save para atribuição, reatribuição, liberação, Categoria inativa, Status com comentário e terminal; verificar XANO, PERSISTENCE e REST_AUTH. `xano function run` não conclui esta tarefa.
- [ ] 5.2 Exercitar pelo Reflex em execução real o detalhe, rascunho, Descartar, Save combinado, falha sem confirmação visual, comentário Público/Interno e timeline mista; verificar REFLEX com dados reais e contrato autenticado.

## 6. Validação integrada e humana

- [ ] 6.1 Executar a suíte Python completa, compile Reflex --dry, validação OpenSpec estrita, validação XanoScript, testes de contrato e `git diff --check`; registrar separadamente UNIT, CONTRACT, XANO, PERSISTENCE, REST_AUTH e REFLEX passados, falhos ou bloqueados.
- [ ] 6.2 Conduzir validação humana com Técnico, Diretoria, Administrador e Gerente nos cenários definidos pelas specs; verificar HUMAN para permissões, Save atômico, comentário em terminal, Categoria/SLA, evento único e preservação da fila. Não marcar a change concluída antes dessa evidência.
