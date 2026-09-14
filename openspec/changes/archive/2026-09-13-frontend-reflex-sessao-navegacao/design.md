## Context

Ver `proposal.md` para a motivação e `specs/frontend-sessao-navegacao/spec.md` para o comportamento esperado. O repositório possui as pastas `app/components`, `app/pages`, `app/services` e `app/states`, mas ainda não contém uma aplicação Reflex. O Xano já oferece `POST /login`, que retorna `authToken`, e `GET /me`, que retorna `id`, `nome`, `email`, `role` e `lojas_id`; esses contratos e as regras de autorização não serão modificados.

A solução precisa manter credenciais e token fora do conteúdo renderizado, usar os mecanismos próprios de State, eventos, páginas e rotas do Reflex e deixar toda decisão de autorização no Xano. Como as páginas funcionais ainda não existem, as páginas iniciais por perfil serão destinos neutros da casca autenticada.

## Goals / Non-Goals

**Goals:**

- Estabelecer uma estrutura Reflex pequena e reutilizável para páginas, componentes, serviços e estado.
- Manter o token do Xano associado à sessão do usuário sem sincronizá-lo com o frontend.
- Confirmar e revalidar a identidade exclusivamente por `GET /me`.
- Tornar login, logout, expiração e proteção de rotas comportamentos uniformes.
- Diferenciar rejeição de autenticação, rejeição de autorização e indisponibilidade do Xano.
- Fornecer páginas iniciais e navegação mínimas para os três perfis oficiais.
- Permitir testes determinísticos sem depender de credenciais ou do workspace Xano ativo.

**Non-Goals:**

- Implementar autenticação própria, refresh token, renovação automática, cadastro ou recuperação de senha.
- Alterar XanoScript, tabelas, endpoints, perfis, associação de Loja ou matriz de autorização.
- Criar páginas ou links funcionais de chamados, fila, tratativa, ativos, telemetria, dashboards ou indicadores.
- Persistir ou recuperar o token com `LocalStorage`, `SessionStorage`, cookie próprio, refresh token ou qualquer outro mecanismo não aprovado, inclusive para compartilhar uma sessão entre abas independentes.
- Definir regras de Service Desk ou usar a proteção visual como autorização.

## Decisions

### 1. Organizar o frontend por responsabilidades Reflex já reservadas no repositório

A aplicação terá um módulo de entrada que instancia `rx.App`, páginas públicas e autenticadas em `app/pages`, componentes da casca em `app/components`, o cliente Xano em `app/services` e o estado de autenticação em `app/states`. As páginas serão registradas explicitamente e importadas pelo módulo da aplicação para que o Reflex as descubra durante a compilação.

Essa separação permite que as próximas changes acrescentem jornadas sem misturar renderização, sessão e transporte HTTP. Uma única página monolítica foi rejeitada porque tornaria a fundação difícil de reutilizar; criar uma hierarquia mais extensa foi rejeitado por não ser necessária ao escopo acadêmico atual.

### 2. Usar um cliente HTTP assíncrono e centralizado

Um serviço único encapsulará URL base, timeout, serialização JSON, cabeçalho `Authorization` esperado pelo Xano e conversão das respostas em resultados ou erros tipados. O serviço oferecerá, nesta change, somente as operações de login e identidade atual, mas a infraestrutura poderá ser reutilizada por clientes futuros.

As chamadas serão assíncronas para não bloquear eventos de carregamento do Reflex. A implementação usará um cliente assíncrono mantido como dependência direta do projeto, com substituição simples por falso ou mock nos testes. Chamadas `requests` espalhadas pelos States foram rejeitadas por duplicarem configuração e tratamento de erros.

`XANO_AUTH_BASE_URL` será a configuração obrigatória e exclusiva do cliente de autenticação do frontend e será normalizada sem URL específica embutida no código. Ela apontará para o grupo que contém `POST /login` e `GET /me`, independentemente de `XANO_BASE_URL`, que permanecerá disponível para Simulator, Fiscal e demais integrações com grupos operacionais. O timeout terá configuração própria e valor padrão explícito. `.env.example` documentará somente nomes e valores de exemplo não sensíveis.

### 3. Manter o token em variável backend-only do State da sessão

O estado de autenticação terá uma variável backend-only, por exemplo `_auth_token`, que não é sincronizada nem renderizada pelo frontend. Os dados públicos retornados por `/me` serão representados por campos tipados do State e somente eles poderão alimentar componentes.

O token não será colocado em `LocalStorage`, `SessionStorage`, cookie próprio, URL, propriedade de componente ou mensagem, e não haverá refresh token nem mecanismo alternativo de recuperação. A sessão não possui persistência duradoura: ela depende exclusivamente do ciclo de vida do State backend associado ao cliente Reflex, e uma nova sessão do navegador começa sem token. Essa escolha segue o princípio de manter material sensível no backend do Reflex.

Como o Reflex 0.9.7 usa armazenamento em disco por padrão, a aplicação configurará explicitamente o gerenciador de State em memória. Assim, o State autenticado e o token backend-only não serão gravados em `.states` nem restaurados após reinício do processo.

As oito horas definidas na capacidade consolidada de autenticação representam somente a validade máxima do token perante o Xano. Elas não constituem duração prometida para a sessão do Reflex e não garantem que o State backend sobreviverá por oito horas. Se o processo reiniciar, o State expirar ou for perdido e `_auth_token` não puder mais ser obtido, a aplicação não tentará recuperá-lo por outro armazenamento: limpará a identidade apresentável e exigirá nova autenticação, mesmo que o token anteriormente emitido ainda pudesse ser aceito pelo Xano.

Armazenar o token em `LocalStorage` foi rejeitado por persistir além da sessão e expô-lo ao JavaScript. `SessionStorage` também foi rejeitado porque enviaria o token ao cliente e introduziria recuperação não aprovada. Armazená-lo em um State comum foi rejeitado porque sincronizaria o valor com o navegador. Introduzir cookie próprio, refresh token, segunda autenticação ou qualquer persistência equivalente foi rejeitado porque ampliaria o mecanismo já consolidado no Xano.

### 4. Confirmar o login com `/me` antes de publicar a sessão

O evento de login receberá os valores do formulário, chamará `POST /login`, guardará provisoriamente o token backend-only e, em seguida, chamará `GET /me`. Somente uma identidade válida com `gerente`, `tecnico` ou `diretoria` concluirá o login e acionará o redirecionamento.

Senha e token não serão mantidos em campos apresentáveis nem incluídos em logs. Se o login ou `/me` falhar, o estado provisório será limpo. Isso evita considerar autenticado um token cuja identidade ainda não foi validada.

Confiar apenas no retorno de `POST /login` foi rejeitado porque esse contrato não contém a identidade necessária à navegação. Inferir o perfil no Reflex ou codificá-lo no formulário foi rejeitado porque `/me` é a fonte consolidada.

### 5. Revalidar páginas protegidas em eventos de carregamento

Cada página autenticada usará um guard compartilhado em `on_load`. O guard verificará a presença do token, consultará `/me` e confirmará que o perfil retornado corresponde à rota. Enquanto essa verificação estiver em andamento, a página renderizará apenas um estado neutro de carregamento; o conteúdo autenticado dependerá de um estado confirmado.

As rotas serão:

| Rota | Acesso e comportamento |
|---|---|
| `/` | Resolve a sessão e encaminha para `/login` ou para o início do perfil. |
| `/login` | Pública; sessão já confirmada é encaminhada para o início do perfil. |
| `/gerente` | Exige sessão confirmada com perfil `gerente`. |
| `/tecnico` | Exige sessão confirmada com perfil `tecnico`. |
| `/diretoria` | Exige sessão confirmada com perfil `diretoria`. |

Um perfil que acessar a rota de outro será redirecionado para sua própria página inicial. Esse comportamento organiza a navegação, mas não concede ou nega acesso a dados: futuras chamadas continuam sujeitas ao Xano.

Aplicar apenas `rx.cond` sem guard foi rejeitado porque esconder componentes não protege eventos nem evita renderização intermediária. Duplicar lógica diferente em cada página foi rejeitado pelo risco de divergência.

### 6. Centralizar o ciclo de vida e a classificação de erros da sessão

O State terá operações reutilizáveis para iniciar e finalizar carregamento, publicar identidade, limpar sessão, resolver destino por perfil e processar erros do cliente. A classificação mínima será:

- credenciais rejeitadas no login: mensagem genérica e permanência em `/login`;
- sessão não autenticada ou expirada: limpeza integral, mensagem de expiração quando aplicável e redirecionamento para `/login`;
- identidade inválida: falha fechada e retorno ao login;
- operação autenticada não autorizada: sessão preservada e apresentação da negação;
- timeout, conexão ou falha temporária do servidor: sessão preservada quando já existia e apresentação de indisponibilidade com possibilidade de nova tentativa.

O logout será local porque o contrato consolidado não oferece revogação de token: limpará token, identidade, mensagens sensíveis e estado de carregamento, depois redirecionará para `/login`. O token expirará no Xano no máximo após as oito horas já definidas, mas a sessão Reflex poderá terminar antes por logout, perda, expiração ou reinício do State. Adicionar persistência, blacklist ou endpoint de revogação está fora do escopo.

### 7. Criar uma casca visual mínima sem antecipar funcionalidades

A tela de login conterá identificação do MIRA, campos de e-mail e senha, estado de carregamento e área de erro. A casca autenticada exibirá identidade pública, rótulo do perfil, um único destino de início compatível com o perfil e a ação de logout. As três páginas iniciais terão conteúdo neutro, suficiente para confirmar sessão e roteamento.

Não serão exibidos links inativos para Service Desk ou dashboards. Isso mantém o escopo verificável e evita apresentar capacidades ainda inexistentes como disponíveis.

### 8. Testar fronteiras sem depender do ambiente remoto

Os testes substituirão o cliente Xano e cobrirão transições do State, classificação de erros e destinos por perfil. A compilação do Reflex verificará o registro das páginas e o uso válido de Vars e eventos. Uma validação manual opcional contra o Xano alvo será executada somente com URL e credenciais fornecidas fora do repositório.

Testes que gravem credenciais reais ou dependam sempre do datasource `live` foram rejeitados por não serem reproduzíveis nem seguros.

## Risks / Trade-offs

- **[Estado backend perdido]** Reinício do backend Reflex ou expiração do State encerra a sessão antes das oito horas do token → tratar ausência do token como sessão encerrada e exigir novo login, sem persistência insegura no cliente.
- **[Redirecionamento em ciclo]** Guards independentes podem alternar entre login e página de perfil → centralizar resolução de destino e testar todas as combinações de rota, token e perfil.
- **[Conteúdo exibido antes da validação]** `on_load` ocorre após o início da renderização → condicionar toda a casca autenticada ao estado confirmado e mostrar apenas carregamento neutro durante `/me`.
- **[Indisponibilidade confundida com expiração]** Limpar o token em qualquer erro força logins desnecessários → o cliente deve distinguir autenticação, autorização e erros transitórios.
- **[Logout não revoga token no Xano]** A limpeza local não invalida um token já copiado → manter o token backend-only e registrar que revogação exigiria futura alteração do contrato Xano.
- **[Dependência adicional]** Um cliente HTTP assíncrono aumenta a superfície de dependências → fixar faixa compatível, declarar a dependência diretamente e cobrir o adaptador com testes.
- **[Proteção visual interpretada como segurança]** Rotas por perfil podem sugerir autorização no frontend → manter as chamadas futuras autenticadas e documentar que o Xano continua sendo a autoridade.

## Migration Plan

1. Confirmar o contrato local de `POST /login` e `GET /me` sem alterar o Xano.
2. Adicionar a configuração Reflex, as dependências diretas e a estrutura mínima da aplicação, separando `XANO_AUTH_BASE_URL` da base operacional `XANO_BASE_URL`.
3. Implementar e testar isoladamente o cliente Xano e sua classificação de erros.
4. Implementar o State de autenticação, login, validação por `/me`, expiração e logout.
5. Criar componentes da casca, rotas e guards compartilhados.
6. Executar testes automatizados e compilar a aplicação Reflex.
7. Validar manualmente os três perfis contra o ambiente configurado, sem registrar credenciais ou tokens.

Não há migração de dados nem sincronização Xano. Em caso de rollback, remover a nova aplicação Reflex e suas dependências/configurações, preservando integralmente o backend e as automações existentes.
