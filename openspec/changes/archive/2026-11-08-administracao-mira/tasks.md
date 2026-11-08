# Tasks

## 1. Preparação técnica proporcional

- [x] 1.1 Conferir no Xano Developer MCP a sintaxe dos XanoScripts afetados e os recursos Free usados por tabelas, consultas, validações e transações; registrar a evidência e distinguir sintaxe de comportamento runtime.
- [x] 1.2 Preparar dados de teste isolados para Administrador, demais perfis, duas Lojas, Gerente e Totem sem telemetria; verificar que o plano de testes não altera registros reais nem exige carga ou stress.

## 2. CRUD administrativo de Lojas

- [x] 2.1 Implementar criação de Loja com nome, endereço, região e situação inicial `Ativa` em contrato específico; validar XanoScript e testar sucesso, campo obrigatório ausente e perfil indevido.
- [x] 2.2 Implementar listagem e detalhe administrativos de Lojas, preservando o catálogo mínimo usado pela criação de usuário; validar respostas de Loja `Ativa`/`Inativa` e autorização negativa.
- [x] 2.3 Implementar edição, inativação e reativação de Loja; testar que novos vínculos ficam bloqueados em `Inativa`, os existentes continuam operando e nenhum Totem muda artificialmente para `Offline`.
- [x] 2.4 Implementar exclusão física de Loja com checagem dos vínculos atuais de Gerentes, Totens e preferências, sem cascata; testar exclusão livre e erro funcional por dependência. Completar a checagem do histórico temporal na tarefa 3.1.

## 3. Estrutura temporal Totem–Loja

- [x] 3.1 Acrescentar schema aditivo de identificação do Totem e `historico_vinculos_totem_loja`, sem backfill, e completar a exclusão de Loja para bloquear referências temporais; validar XanoScript e testes de histórico impeditivo e registros legados intactos.
- [x] 3.2 Implementar registro inicial e transferência temporal com origem, destino e `efetivado_em` definidos pelo Xano, junto da atualização do vínculo atual em `db.transaction`; testar operação sequencial válida, destino inválido e ausência de escrita parcial observável em falha funcional.
- [x] 3.3 Implementar resolução de Loja por `chamados.criado_em`, `telemetria_equipamentos.evento_timestamp` e `historico_disponibilidade_totens.detectado_em`; testar antes, na fronteira e depois da transferência, além de legado sem vínculo comprovável.

## 4. CRUD administrativo de Totens

- [x] 4.1 Implementar criação de Totem com identificação, nome, Loja `Ativa` e evento temporal inicial; testar dados inválidos, perfil indevido e ausência de estado `Online`/`Offline` antes da primeira telemetria.
- [x] 4.2 Implementar listagem e detalhe administrativos de Totens; testar Totem em Loja `Inativa`, estado desconhecido e respostas sem dados fora do contrato.
- [x] 4.3 Implementar edição e transferência de Totem para Loja `Ativa` com ID preservado; testar destino `Inativa` rejeitado e fatos anteriores intactos com Loja histórica correta.
- [ ] 4.4 Implementar exclusão física de Totem com checagem de chamados, telemetria, disponibilidade, preferências e histórico temporal; permitir remoção explícita do único vínculo inicial de Totem nunca usado e testar bloqueio por cada dependência relevante, sem cascata automática.

## 5. Administração de Usuários e Gerentes

- [x] 5.1 Reutilizar `POST /administracao/usuarios`, exigindo Loja `Ativa` para novo Gerente; testar e-mail único, perfis canônicos, senha temporária, primeiro acesso e resposta sem credenciais.
- [x] 5.2 Implementar listagem e detalhe administrativos de usuários; testar projeção sem senha, hash ou token e negação a outros perfis.
- [x] 5.3 Implementar edição de nome, e-mail, perfil e Loja, com transferência de Gerente para Loja `Ativa` e bloqueio de Técnico responsável por chamado; testar IDs históricos preservados, e-mail duplicado e Gerente já vinculado a Loja `Inativa` sem novo vínculo.
- [ ] 5.4 Implementar proteção do último Administrador em mudança de perfil e exclusão, inclusive autoedição, usando validação Xano na unidade de escrita; testar último bloqueado, mudança permitida quando outro Administrador permanece e ausência de alteração parcial nos casos funcionais.
- [x] 5.5 Implementar exclusão física de usuário com checagem de chamados, interações e preferências, vedando própria conta e cascata; testar dependências, perfil indevido e exclusão de registro livre.

## 6. Service Desk e histórico operacional

- [x] 6.1 Implementar entrada administrativa de abertura manual global reutilizando as validações do Gerente; testar Administrador em Loja diferente, solicitante da sessão, Categoria/prioridade válidas e negação a perfil indevido.
- [x] 6.2 Ajustar lista, detalhe, comentários e filtros do Gerente para a Loja histórica demonstrável do chamado; testar acesso da origem, negação à Loja de destino e falha fechada para legado indeterminado.
- [x] 6.3 Ajustar fila e detalhe globais para Loja histórica e preservar tratativa existente; testar filtros por Loja antes/depois da transferência e chamado legado sem Loja comprovada.
- [ ] 6.4 Ajustar leitura histórica do monitoramento sem mudar Fiscal ou Simulator; testar telemetria/eventos em cada Loja, Loja `Inativa` operante e Totem novo sem telemetria.

## 7. Interface Reflex integrada

- [x] 7.1 Estender cliente Xano e estados administrativos, isolando dados por sessão; testar parsing, expiração, acesso indevido e troca de usuário.
- [x] 7.2 Ampliar a área existente com seções de Usuários, Lojas e Totens, listas, detalhes, criação e edição segundo `DESIGN.md`; verificar compilação Reflex e testes de guard e navegação.
- [x] 7.3 Adicionar seleção de Loja `Ativa`, confirmação de exclusão e erros funcionais; testar cancelamento, dependência impeditiva, último Administrador bloqueado e ausência de credenciais na interface.
- [x] 7.4 Disponibilizar abertura manual global do Administrador no Reflex; verificar compilação e fluxo com Totem de outra Loja sem duplicar regras de negócio no frontend.
- [x] 7.5 Centralizar a sidebar em `/administracao/gestao`, deixar `/administracao/usuarios` somente como alias protegido e eliminar a página e o formulário duplicados; testar matriz de rotas e permissões.
- [x] 7.6 Compor dashboard de três cards segundo `DESIGN.md` e referência Figma, com indicadores reais e adaptação a larguras distintas; verificar no navegador.
- [x] 7.7 Mover as três criações para modais com validação, cancelamento, erro, sucesso e atualização das listas, sem senha persistida em State; testar com mocks e no navegador sem gravar na `v1`.
- [x] 7.8 Modernizar as três listagens na mesma rota, mantendo busca, estados de vazio/erro e ações protegidas de edição, transferência e exclusão; testar com mocks e no navegador sem mutação live.
- [x] 7.9 Oferecer a abertura global no Início com formulário visual compartilhado com o Gerente; testar os dois perfis e a ausência do formulário na gestão, sem criar chamado de teste na `v1`.

## 8. Integração e evidência

- [x] 8.1 Executar testes funcionais focados, suíte Python pertinente, compilação Reflex, validação XanoScript, `git diff --check` e `openspec validate administracao-mira --strict`; registrar cada resultado como passou, falhou, não executado ou bloqueado.
- [x] 8.2 Registrar limites não demonstrados de concorrência e rollback de falha provocada, sem declarar cenário não executado como aprovado; verificar que os requisitos de negócio e testes funcionais normais permanecem rastreáveis às specs.
- [x] 8.3 Antes de qualquer publicação autorizada, executar `xano workspace push --dry-run` e revisar o diff completo; após push real autorizado, repetir dry-run e verificar ausência de alteração fora do escopo.
