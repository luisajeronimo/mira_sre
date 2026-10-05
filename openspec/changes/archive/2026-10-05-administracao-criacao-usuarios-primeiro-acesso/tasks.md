# Tasks

## 1. Gate técnico Xano e senha nativa

- [x] 1.1 Antes do Apply, obter autorização humana explícita que identifique a primeira conta canônica `administrador` e aprove o procedimento administrativo nativo Xano; registrar a decisão de forma segura, sem senha, hash ou token, e sem converter `admin` legado.
- [x] 1.2 Consultar o Xano Developer MCP para confirmar a escrita segura do campo `password`, a forma de atualização coerente com a flag e a disponibilidade no plano Free; registrar a evidência técnica no artefato de implementação.
- [x] 1.3 Inventariar os endpoints humanos autenticados e verificar quais já usam a autorização central, para definir a cobertura completa do gate de primeiro acesso sem alterar contratos de automação.

## 2. Schema e perfil Administrador

- [x] 2.1 Atualizar o schema `usuarios` com o valor canônico `administrador` e o booleano de troca obrigatória com default compatível `false`; validar XanoScript e confirmar que não há backfill nem alteração de registros existentes.
- [x] 2.2 Atualizar as funções de login e identidade para reconhecer somente os quatro perfis humanos canônicos e incluir a flag em `/me`; cobrir login e `/me` de Administrador, `admin` não oficial e usuário existente sem pendência.

## 3. Autorização central e gate de primeiro acesso

- [x] 3.1 Estender a autorização central para `administrador` sem conceder capacidades futuras, mantendo Bot, Fiscal e Simulator fora dos perfis humanos; verificar rejeição de `admin` e de credenciais de automação.
- [x] 3.2 Implementar o gate central que bloqueia sessão pendente antes de APIs funcionais normais e libera somente `/me` e troca da própria senha; verificar por contrato a rejeição de chamada direta e a preservação de Simulator, Fiscal e Bot.
- [x] 3.3 Confirmar que os endpoints humanos autenticados passam pelo gate central ou integrá-los de forma coerente; validar que CRUDs genéricos de `usuarios` continuam bloqueados.

## 4. Criação administrativa de usuários

- [x] 4.1 Implementar `POST /administracao/usuarios`, autenticado e exclusivo de Administrador, com DTO público sem senha, hash ou token; validar a resposta e a negação para Gerente, Técnico, Diretoria e automações.
- [x] 4.2 Implementar validações de nome, e-mail, unicidade, perfil canônico e senha temporária mínima de oito caracteres; cobrir e-mail duplicado, perfil inválido e senha curta sem persistência parcial.
- [x] 4.3 Implementar as regras de Loja: Gerente exige Loja existente; Técnico, Diretoria e Administrador exigem `lojas_id` nulo; cobrir Gerente válido, Gerente sem Loja, Loja inexistente e Loja enviada aos três perfis globais.
- [x] 4.4 Criar usuário novo com senha nativa sensível e flag pendente verdadeira; validar o DTO público e os controles `sensitive` sem inspecionar histórico bruto que possa expor credenciais.
- [x] 4.5 Implementar `GET /administracao/lojas` somente para Administrador concluído, retornando opções `{id, nome}` e mantendo o gate central e as permissões gerais de Lojas; adicionar cobertura XanoScript de autorização por perfil e validar o parser.

## 5. Primeiro acesso e troca obrigatória no backend

- [x] 5.1 Implementar endpoint autenticado específico de troca que recebe somente `nova_senha`, usa a identidade do token e verifica pendência; confirmar que não há alvo externo no contrato e que a jornada rejeita a senha temporária após a troca.
- [x] 5.2 Atualizar senha pelo mecanismo nativo e limpar a flag na mesma transação confirmada pelo MCP para o plano Free; validar a transição bem-sucedida sem injetar falhas que exijam adulterar a conta de teste.
- [x] 5.3 Cobrir o fluxo de contrato: login com senha temporária emite token, `/me` retorna pendência, troca válida encerra pendência, senha temporária deixa de autenticar e nova senha autentica.

## 6. Cliente, sessão e guards Reflex

- [x] 6.1 Estender modelos e cliente Xano para `/me`, criação administrativa e troca de senha sem armazenar ou expor credenciais; cobrir payloads, respostas sanitizadas e classificação de erros vigente.
- [x] 6.2 Estender `AuthState` e destinos por perfil para Administrador e flag de primeiro acesso; cobrir login, `/me` e destino `/administracao` do Administrador.
- [x] 6.3 Aplicar guard compartilhado que redireciona sessão pendente de todas as rotas funcionais à rota exclusiva e redireciona sessão concluída para o perfil; cobrir bypass por `/gerente`, `/tecnico`, `/diretoria`, `/administracao` e saída do primeiro acesso.

## 7. Interface administrativa mínima

- [x] 7.1 Criar e registrar a rota `/administracao` na casca autenticada com acesso visual de Administrador, sem dashboard nem listagem obrigatória; verificar compilação Reflex e negação de rota para outros perfis.
- [x] 7.2 Implementar o formulário de criação com nome, e-mail, perfil, senha temporária e confirmação local; verificar que sucesso e erro não mostram senha, hash ou token.
- [x] 7.3 Implementar Select de Loja por nome condicional para Gerente, enviar o ID selecionado e limpar seleção ao mudar de perfil; perfis globais não exibem nem enviam Loja, e Gerente sem opção válida é rejeitado localmente.

## 8. Interface de primeiro acesso

- [x] 8.1 Criar e registrar a rota exclusiva de primeiro acesso com nova senha, confirmação e ação autenticada; verificar que não recebe senha por URL nem a mantém em estado apresentável.
- [x] 8.2 Após troca bem-sucedida, revalidar `/me` e redirecionar para Gerente, Técnico, Diretoria ou Administração; cobrir falha sanitizada que mantém o usuário no fluxo obrigatório.

## 9. Testes locais e regressão

- [x] 9.1 Criar harnesses e testes XanoScript para validações backend isoláveis (perfil, Loja, unicidade, gate e DTOs); cobrir autenticação e troca pela suíte local e pelas jornadas E2E aprovadas, sem ler registros sensíveis.
- [x] 9.2 Criar ou ampliar testes de cliente, `AuthState`, rotas e componentes Reflex para Administrador, formulário, primeiro acesso e bypass de rota.
- [x] 9.3 Executar a suíte Python relevante e a regressão completa, incluindo perfis atuais, Service Desk afetado, Fiscal, Simulator e Bot; registrar separadamente testes passados, falhos, não executados ou bloqueados.
- [x] 9.4 Adicionar regressão específica para opções administrativas mínimas de Loja, autorização por perfil/gate, Select, carregamento/erro sanitizado, seleção de ID, ausência residual para perfis globais e formulário sem seleção válida.

### Evidência de correção runtime

- Foi identificado um loop de redirecionamento em `/primeiro-acesso`: a
  revalidação válida de uma sessão pendente emitia redirecionamento para a
  própria rota. A correção local separa o loader da rota exclusiva do guard de
  rotas funcionais, preserva `GET /me` e mantém a sessão pendente na página.
- Foram adicionados testes para login pendente de Administrador, revalidação
  única e repetida sem redirecionamento próprio, redirecionamento de sessão
  concluída por perfil e preservação da falha fechada para identidade inválida.
- A revalidação manual da jornada da Administradora, registrada abaixo,
  confirmou a correção do loop. Nenhum dado remoto foi alterado pelo código
  desta correção local.

### Evidência E2E: primeiro acesso da Administradora (2026-10-04)

- Confirmação humana `PRIMEIRO_ACESSO_ADMIN_CONCLUIDO`: login temporário,
  estabilidade e reload em `/primeiro-acesso`, bloqueio de `/administracao`
  durante pendência, troca, redirecionamento, rejeição da senha temporária,
  aceitação da nova senha e acesso final a `/administracao` foram reportados
  como concluídos pela pessoa humana. Nenhuma senha ou token foi fornecido.
- Verificação remota read-only: conta 12 corresponde a Luisa Lima,
  `luisa.lima@fastfood.com`, `administrador`, Loja nula e
  `deve_trocar_senha=false`. Os dez usuários do baseline mantêm seus campos
  públicos comparados; total segue 11, sem IDs faltantes ou novos. Nenhum
  campo de senha foi consultado.
- Evidência local previamente aprovada nesta rodada: suíte Python completa,
  138 testes aprovados; compilação Reflex dry, OpenSpec strict e
  `git diff --check` passaram; Xano dry-run retornou `No changes to push`.
- Naquele momento a criação dos perfis e as evidências E2E restantes ainda
  estavam pendentes; os relatos humanos e testes adicionais registrados abaixo
  atualizam esse estado. Não foi exigida troca de senha dos outros perfis.
- A jornada manual também fornece evidência para a task 5.3: login com senha
  temporária, sessão pendente, troca, rejeição da senha temporária e aceitação
  da nova senha foram confirmados. Nenhuma senha ou token foi registrado.

### Evidência da lacuna de seleção de Loja

- Durante o E2E de criação administrativa, foi constatado que o campo de Loja
  era um input numérico manual sem catálogo e não permitia selecionar uma Loja
  pelo nome. Nenhum usuário foi criado e nenhum dado remoto foi alterado nesta
  investigação.
- A correção local adiciona `GET /administracao/lojas` com resposta mínima,
  mantém inalterados os endpoints gerais de Loja, carrega as opções após o
  guard da Administração e apresenta Select nome/ID com limpeza ao trocar para
  perfil global. A cobertura local específica está na task 9.4.
- Publicação remota autorizada (2026-10-04), workspace `152692`: o dry-run
  prévio mostrou somente a função `administracao/listar_opcoes_lojas` e o
  endpoint `administracao/lojas GET`. A chamada normal parou antes de aplicar
  alterações porque a CLI não podia confirmar interativamente; após conferir
  novamente o mesmo preview, `xano workspace push --force` foi concluído. A
  CLI informou 81 documentos enviados no pacote e sincronização local de 2
  GUIDs; o preview identificava somente os dois recursos acima como alterados.
  Não foram usados `--records`, `--delete`, `--env` ou `--sync`.
- Verificação remota read-only pela Meta API confirmou que a função consulta
  Lojas, projeta somente `id` e `nome` e não contém operações de mutação; o GET
  autenticado como `usuarios` chama essa função. O autorizador central remoto
  exige Administrador e bloqueia primeiro acesso pendente antes da checagem de
  perfil. O `GET /lojas` geral permanece autorizado somente para Gerente e
  Diretoria, sem Administrador.
- Dry-run pós-push retornou `No changes to push`. O push foi estrutural, sem
  sincronização de records; a função e o endpoint não foram executados durante
  esta rodada. Portanto, nenhum registro — inclusive a conta ID 12 — foi
  alterado pelo push. A conta não foi reconsultada nesta rodada; a última
  evidência read-only anterior registrava primeiro acesso concluído.
- Validação local desta correção: `.venv/bin/python -m pytest -q` aprovou 158
  testes; Reflex compile, OpenSpec strict e `git diff --check` passaram. O MCP
  validou os três XanoScripts tocados. A confirmação manual posterior do
  Select e da criação do Gerente E2E está registrada abaixo; as etapas de
  runtime restantes continuam pendentes.

### Evidência manual: Gerente E2E (2026-10-04)

- A pessoa humana confirmou que criou pela UI `Gerente E2E MIRA`,
  `e2e.gerente.20261004@fastfood.com`, perfil Gerente, selecionando Loja
  Paulista (ID 1). Também confirmou que o Select aparece para Gerente, some ao
  mudar para Técnico e exige nova seleção ao voltar para Gerente. Nenhuma
  senha ou token foi fornecido.
- Confirmação humana `PRIMEIRO_ACESSO_GERENTE_CONCLUIDO`: login com senha
  temporária, primeiro acesso obrigatório, bloqueio/redirecionamento de rota
  normal antes da troca, troca concluída, rejeição da senha temporária,
  aceitação da nova senha e acesso normal como Gerente. A jornada manual
  registra a pendência original (`deve_trocar_senha=true`) pelo primeiro
  acesso obrigatório; isso não é leitura direta do registro remoto.
- Confirmação humana subsequente: também foram criados pela UI o Técnico E2E
  (`e2e.tecnico.20261004@fastfood.com`), a Diretoria E2E
  (`e2e.diretoria.20261004@fastfood.com`) e o Administrador E2E
  (`e2e.administrador.20261004@fastfood.com`), todos sem Loja. Não se exige
  primeiro acesso redundante desses três usuários.
- Não foi possível consultar `GET /me` da sessão: não há browser conectado a
  este processo. Foi solicitada à pessoa humana a confirmação dos campos
  sanitizados `role`, `lojas_id` e `deve_trocar_senha`, além da negação de
  `/administracao` e acesso normal do Gerente. Nenhuma senha, token, tabela
  bruta `usuarios` ou campo `password`/hash foi consultado. A unicidade do
  Gerente ainda aguarda a tentativa controlada de duplicidade descrita no
  roteiro humano.

### Testes Xano de validação e autorização (2026-10-05)

- A execução remota dos testes centrais identificou que mocks antigos de
  sessão concluída não continham `deve_trocar_senha=false`; os testes positivos
  falhavam ao ler a nova flag. Foram corrigidos somente os fixtures dos mocks,
  sem alterar a política de autorização. Os cenários positivos e negativos de
  escopo de Loja e perfil passaram após a correção.
- `autorizacao/exigir_perfil` recebeu testes específicos para Administrador
  concluído, Administrador pendente e negação a Gerente, Técnico e Diretoria.
  `login` e `autorizacao/obter_identidade` receberam cobertura de Administrador
  pendente; o login rejeita `admin` legado. Os unit tests Xano publicados para
  esses casos passaram.
- Para validar os dados de criação sem criar registros de teste, as regras
  foram extraídas para `administracao/validar_criacao_usuario`, função somente
  de leitura, chamada depois do gate de Administrador e antes do único `db.add`
  no endpoint. Seus 11 unit tests Xano passaram: quatro perfis válidos, `admin`
  inválido, Gerente sem Loja/inexistente, Loja para perfis globais e e-mail
  duplicado.
- Push estrutural autorizado após previews exatos: primeiro duas funções de
  autorização; em seguida os testes de login/identidade; por fim somente a
  função de validação acima e `POST /administracao/usuarios`. A CLI reportou
  `Pushed 81 documents` nas duas primeiras publicações e `Pushed 82 documents`
  na última; são totais do pacote. Os previews mostraram apenas os recursos
  listados, sem envio de records. O dry-run pós-push retornou
  `No changes to push`.
- Os unit tests executaram somente cenários mockados; nenhum usuário foi
  criado/alterado por eles. Nenhum histórico bruto, senha, hash, token ou
  `swagger.token` foi consultado ou registrado.

### Rejeições do formulário administrativo (2026-10-05)

- A revisão pré-Archive identificou que o cliente só classificava HTTP 422
  como entrada inválida, enquanto rejeições Xano HTTP 400 no endpoint de
  criação poderiam escapar do tratamento visível do formulário. O cliente
  agora classifica HTTP 400 como entrada inválida somente para
  `POST /administracao/usuarios`; os demais endpoints mantêm o tratamento
  estrito de erro de contrato. `AdministracaoState` exibe mensagem sanitizada
  para rejeição funcional e para resposta de contrato inesperada.
- Regressões locais confirmam a classificação específica do HTTP 400, a
  preservação do erro estrito nos demais endpoints e mensagens sem detalhes
  internos. Os testes focados após a correção passaram (45 testes).
- O `mira-reviewer` aprovou essa correção local em revisão independente.
  Permanecem pendentes apenas as evidências runtime humanas registradas na
  task 10.2; não foram inferidas nem substituídas por unit tests.

### Evidência segura de ausência de segredos

- O endpoint de criação recebe senha temporária como input sensível e monta
  resposta somente com identidade pública e flag; o endpoint de troca também
  marca `nova_senha` como sensível e retorna apenas `{success: true}`. Login
  retorna somente o token previsto no contrato, sem senha/hash; `/me` projeta
  identidade e flag sem credenciais; opções administrativas de Loja retornam
  apenas `{id, nome}`.
- Os DTOs Reflex de identidade, usuário criado e opção de Loja não possuem
  campo de senha/hash. `_auth_token` fica somente no State backend; a senha de
  formulário é recebida como dado de evento e não é declarada como variável de
  State. Testes locais cobrem a ausência de campos de senha no State e as
  respostas sanitizadas.
- As evidências controladas desta change não contêm credenciais. Histórico
  bruto de request/log não foi consultado para evitar exposição potencial; os
  campos sensíveis estão marcados no Xano.

## 10. Validação XanoScript e runtime/E2E

- [x] 10.1 Validar os XanoScripts alterados com Xano Developer MCP e executar `xano workspace push --dry-run`; revisar o diff completo antes de qualquer push autorizado.
- [x] 10.2 Em ambiente autorizado, executar E2E: Administrador cria os quatro perfis permitidos, Gerente usa Loja válida e perfis globais não usam Loja; Administradora e pelo menos um usuário criado pelo endpoint completam o primeiro acesso e alcançam seus destinos; o gate bloqueia sessões pendentes e Gerente não recebe privilégio administrativo. Não exigir trocas redundantes para os outros três perfis.
- [x] 10.3 Confirmar por superfícies seguras que a criação não retorna senha temporária, hash ou token; `/me` não retorna senha/hash; login não retorna senha/hash e retorna somente o token de sessão previsto; troca não retorna nova senha/hash/token adicional; opções de Loja retornam apenas `id/nome`; DTOs Reflex não armazenam senha; inputs sensíveis e evidências controladas não registram segredo. Não consultar histórico bruto que possa expor credenciais.

## 11. Documentação e validação final

- [x] 11.1 Atualizar documentação estável somente se a implementação consolidar comportamento que ela já não descreve; verificar que não duplica specs nem introduz requisitos fora do escopo.
- [x] 11.2 Executar `openspec validate administracao-criacao-usuarios-primeiro-acesso --strict`, `git diff --check`, compilação Reflex e verificações de regressão aplicáveis; reconciliar as tasks com evidências reais.
- [x] 11.3 Revisar o diff para confirmar que não houve CRUD administrativo completo, reset ou recuperação de senha, mensageria, MFA, alterações de automação ou capacidades administrativas não aprovadas.

### Validação final local (2026-10-05)

- `pytest -q`: 168 passaram.
- `reflex compile --dry`: compilação bem-sucedida; apenas avisos de plugin/depreciação já existentes.
- `openspec validate administracao-criacao-usuarios-primeiro-acesso --strict`: válido.
- `git diff --check`: passou.
- `xano workspace push --dry-run`: `No changes to push`.
- A task 10.2 permaneceu aberta até as confirmações runtime humanas listadas
  abaixo; isoladamente, essas validações locais não autorizavam Archive.

### Encerramento da evidência E2E do Gerente (2026-10-05)

- Confirmação humana: `GERENTE_ME_OK; GERENTE_ADMIN_NEGADO;
  GERENTE_ROTA_NORMAL_OK; GERENTE_E2E_DUPLICADO_REJEITADO`.
- A evidência manual confirma o `/me` sanitizado esperado do Gerente E2E,
  a negação de `/administracao`, o acesso à rota funcional normal e a
  rejeição controlada da criação com o e-mail existente, sem sucesso de
  criação. Nenhuma senha, token, tabela bruta ou campo sensível foi fornecido
  ou consultado.
- Com as jornadas humanas previamente registradas — Administradora concluída,
  quatro perfis provisionados, Gerente associado à Loja válida e primeiro
  acesso do Gerente concluído — a task 10.2 possui evidência suficiente.
