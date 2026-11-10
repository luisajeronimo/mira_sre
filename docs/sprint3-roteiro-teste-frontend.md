# Sprint 3 — roteiro de teste manual no Reflex

Este roteiro verifica os fluxos visíveis antes do Archive. Registre para cada passo: data, perfil usado, identificador do chamado, resultado observado, captura de tela sem dados sensíveis e classificação **passou**, **falhou**, **não executado**, **bloqueado por ambiente/ferramenta/credencial** ou **limitação aceita**. Não registre tokens, senhas ou headers de autenticação.

## Pré-condições

1. Os 11 contratos Xano da Sprint 3 foram publicados seletivamente em 2026-11-08; o dry-run posterior ficou limpo. A alteração de monitoramento vista na prévia geral ficou fora do push.
2. Use as contas E2E de Gerente, Técnico, Diretoria e Administrador fornecidas pela responsável. O Gerente de teste tem chamados da própria Loja. Os chamados foram criados com autorização e identificados no título com `[MIRA E2E SPRINT 3]`: **97** já está em `Solução Rejeitada` por uma prova HTTP real; **98** permanece `Resolvido` para o encerramento após 72 horas, com comentário público e nota interna; **99** permanece `Resolvido` para a rejeição manual. Use outros chamados existentes para `Encerrado`, `Cancelado`, SLA vencido ou não calculável, se houver; registre como não executado quando faltar o cenário.
3. As URLs do Xano estão no `.env` local. O gate K-B foi liberado após 31/31 E2E e revisão dos contratos; `MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO=true` já está no `.env` e no `.env.example`. O Reflex está disponível nesta sessão em `http://localhost:3001` (backend em `8001`); se encerrar, reinicie com `reflex run --frontend-port 3001 --backend-port 8001` no ambiente virtual. Para testar a proteção do gate desligado (seção 1), defina temporariamente `false`, reinicie, confira o comportamento e restaure `true`.
4. A chave `MIRA_ENCERRAMENTO_AUTOMATION_KEY` foi gerada no `.env` local, mas a publicação da variável de ambiente no workspace Xano ainda precisa ser confirmada. O comando da seção 5 só deve ser executado depois de configurar no Xano exatamente o valor local. Não copie a chave para logs, capturas ou documentos versionados.

## 1. Gate K-B desligado

1. Entre com cada perfil oficial. Confirme que o menu **Chamados solicitados** não aparece.
2. Abra diretamente `/chamados/solicitados` e `/chamados/solicitados/101` (substitua o ID). Ambas devem redirecionar para `/inicio` sem consultar os contratos do solicitante.
3. Abra um detalhe de Gerente. A seção **Histórico de status** não deve aparecer nem consultar o endpoint de histórico enquanto o gate estiver desligado.

## 2. Gerente: detalhe, SLA e rejeição

1. Entre como Gerente e abra o chamado **99**, `Resolvido` da própria Loja, em `/chamados/99`. Confira dados do chamado, comentários públicos e seção **Consumo de SLA**. Compare percentual, prazo e situação com `GET /gerente/chamados/99/consumo-sla`; em consumo não calculável, a tela deve mostrar o motivo sem percentual nem prazo.
2. Confirme que **Rejeitar solução** aparece somente no detalhe `Resolvido`. Abra chamados `Novo`, `Solução Rejeitada`, `Encerrado` e `Cancelado`: a ação não deve aparecer.
3. No chamado `Resolvido`, envie justificativa vazia ou somente espaços. A tela deve informar a obrigatoriedade e não enviar POST.
4. Antes de enviar a rejeição, abra o chamado **99** em duas sessões de Gerente e mantenha a segunda no estado antigo. Na primeira, envie justificativa válida. Durante o envio, confirme o estado de carregamento e o botão bloqueado. Após confirmação do Xano, confira status `Solução Rejeitada`, campo limpo, mensagem de sucesso, justificativa na lista de comentários públicos, histórico atualizado quando K-B estiver ligado e consumo de SLA recalculado. O chamado **97** oferece uma referência já rejeitada. Preserve o **98** em `Resolvido` para a seção 5.
5. Na segunda sessão ainda aberta com a versão antiga do **99**, tente rejeitar com outra justificativa. O Reflex deve informar conflito, preservar a justificativa digitada e recarregar o detalhe sem fingir sucesso. A versão atual já não deve oferecer nova rejeição.
6. Tente abrir diretamente o detalhe e o consumo de chamado de outra Loja e um ID inexistente. O Xano deve negar o acesso ou indicar não encontrado, sem exibir dados protegidos.

## 3. Técnico e Administrador: consumo de SLA

1. Entre como Técnico e abra o detalhe global de um chamado em contagem. Confira percentual consumido, prazo restante e faixa/situação. Repita para `Resolvido` (pausado), `Encerrado` ou `Cancelado` (encerrado), vencido e não calculável. Compare com `GET /tecnico/chamados/{id}/consumo-sla`.
2. Faça um Save autorizado que altere o status e recarregue o detalhe. Confira que o consumo apresentado corresponde ao estado persistido; nenhum valor é estimado quando a linha do tempo é inconsistente.
3. Repita a consulta com Administrador. O perfil do solicitante não deve ter endpoint nem seção de consumo de SLA.

## 4. Solicitante após liberação K-B

1. Com o gate ligado e os endpoints publicados e revisados, entre com cada perfil oficial. O menu **Chamados solicitados** deve aparecer e ficar ativo na lista e no detalhe. Sem sessão, ambas as rotas devem redirecionar para `/login`; com troca de senha pendente, para `/primeiro-acesso`.
2. Na lista, confira somente chamados vinculados ao usuário, ordenados por última atualização e ID decrescentes. Usuário sem chamados deve ver estado vazio. Não deve haver filtros, preferências ou paginação.
3. Abra um chamado da lista. Confira título, descrição, status, Totem, Loja, Categoria, solicitante e responsável, sem botão de detalhe do Totem, drawer, telemetria ou SLA. A página não deve oferecer comentário, rejeição, Save, atribuição ou outra escrita.
4. Confirme que comentários exibidos são apenas públicos. Um comentário interno e eventos operacionais do mesmo chamado não devem aparecer na seção de comentários.
5. Confira o histórico de status: somente transições válidas, em ordem decrescente, com status anterior, resultante, data e autor. Sem transições registradas, deve aparecer estado vazio. Falha no histórico deve mostrar erro isolado e manter o detalhe visível.
6. Acesse diretamente o detalhe de chamado de outro solicitante e um ID inexistente. Ambos devem resultar em **Chamado não encontrado**, sem dados anteriores na tela.

## 5. Encerramento sob comando

1. O chamado **98** entrou em `Resolvido` em **08/11/2026 por volta de 20h52** (`America/Sao_Paulo`); confira a hora exata no histórico. O prazo de 72 horas se completa em **11/11/2026 por volta de 20h52**. Antes desse instante, confirme que o chamado continua `Resolvido` sem execução de comando. Não rejeite nem altere o **98** antes do teste de encerramento.
2. Depois do prazo e da configuração remota da chave, execute uma única vez `make encerrar-resolvidos` no ambiente autorizado. O comando mostra contagens e não imprime a chave. Reabra no Reflex `/chamados/98`: deve estar `Encerrado`, com comentário público e transição de histórico atribuídos a **Sistema**. Chamado ainda abaixo de 72 horas e chamado resolvido antes da vigência devem permanecer `Resolvido`.
3. Execute o comando novamente e confirme ausência de novo comentário ou transição no chamado já encerrado. Registre separadamente qualquer parte que não puder ser testada por falta de dados, prazo ou autorização.

## Fechamento da evidência

Execute a suíte Python, a compilação Reflex com o gate ligado e desligado, `openspec validate --strict` para as changes ativas e `git diff --check`. A prova E0.3 em runtime permanece **bloqueada por restrição do plano Free**, com limitação aceita na decisão de 2026-11-08. Não classifique E2E não executado como aprovado e não faça Archive neste roteiro.
