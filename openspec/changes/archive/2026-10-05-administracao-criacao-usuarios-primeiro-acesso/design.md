# Design

## Context

Ver `proposal.md` para a motivação e as delta specs para o contrato. O schema
versionado `usuarios` já é uma tabela de autenticação Xano, possui `email`
único, campo nativo sensível `senha` do tipo `password`, enum limitado a três
perfis e `lojas_id` opcional. Login emite token de oito horas; `/me` obtém a
identidade por função central; a autorização também possui função central e os
CRUDs genéricos de usuários já são bloqueados. O Reflex confirma sessão por
`/me` e tem guards por perfil, mas ainda só reconhece três perfis.

O modelo de domínio já descreve Administrador como humano global. Esta change
regulariza apenas a criação de usuários e o primeiro acesso; ela não herda
automaticamente as demais capacidades administrativas previstas para o futuro.

## Goals / Non-Goals

**Goals:**

- Preservar o Xano como autoridade de senha, persistência e autorização.
- Provisionar somente usuários humanos por contrato administrativo explícito.
- Impedir que uma sessão de senha temporária acesse operações normais por UI ou
  por chamada direta à API.
- Preservar as contas existentes sem backfill nem troca retroativa.
- Reusar o cliente, o State e os guards Reflex já existentes.

**Non-Goals:**

- Criar mecanismo alternativo de autenticação, hash, persistência de token ou
  política de senha além do mínimo aprovado.
- Habilitar os CRUDs genéricos, gestão administrativa completa ou operações de
  Service Desk não necessárias para o fluxo.
- Alterar as credenciais e os contratos independentes de Simulator, Fiscal ou
  Bot de Fiscalização.

## Decisions

### 1. Perfil humano canônico e schema compatível

O enum de `usuarios.role` receberá `administrador`. A identidade e a
autorização central reconhecerão os quatro valores canônicos, mantendo `admin`
como valor não oficial e `bot_fiscalizacao` fora de `usuarios` e da sessão
humana. Essa escolha reutiliza a fonte de identidade existente, sem criar uma
tabela paralela ou mapeamento implícito de legado.

### 2. Estado persistido de troca obrigatória

O schema receberá um booleano cujo nome seguirá a convenção existente e cuja
semântica é `deve_trocar_senha`. Seu default será `false`, preservando todo
registro anterior como não pendente, sem backfill. A criação administrativa
atribuirá explicitamente `true` aos novos registros.

O estado não será inferido da idade da conta, do token ou da senha: essa
inferência não diferencia com segurança contas existentes e novas. Também não
será mantido somente no Reflex, pois a API precisa aplicá-lo contra chamadas
diretas.

### 3. Provisionamento funcional, não CRUD genérico

Será criado `POST /administracao/usuarios`, autenticado e protegido pela função
central com exigência exclusiva de `administrador`. A função validará nome,
e-mail, perfil, Loja e senha antes de gravar; o índice único existente será a
última garantia contra concorrência de e-mail. A resposta será um DTO de
identidade pública, sem credenciais.

`lojas_id` será obrigatório e validado contra Loja existente para Gerente. Para
Técnico, Diretoria e Administrador, deve ser nulo; recebê-lo é erro de contrato
e não será ignorado. Essa decisão evita uma associação persistida sem efeito
de escopo.

### 3.2 Opções mínimas de Loja para a Administração

O formulário não solicita que a pessoa conheça ou digite um ID interno. Um
`GET /administracao/lojas`, autenticado pela tabela `usuarios` e protegido por
`autorizacao/exigir_perfil` com apenas Administrador habilitado, fornecerá as
opções necessárias ao Select de Gerente. O gate central bloqueia também
Administrador com primeiro acesso pendente. A resposta terá somente uma lista
`lojas`, com `id` e `nome` por item. A UI apresenta `nome` e envia `id` em
`lojas_id`; a criação continua responsável por validar novamente a existência
e a compatibilidade da Loja com o perfil.

Essa capability não altera `GET /lojas`, `GET /lojas/{id}` nem concede ao
Administrador acesso geral ao domínio ou à gestão de Lojas. No Reflex, as
opções são carregadas uma vez ao entrar na rota `/administracao`, após a
revalidação da sessão; erros são sanitizados e podem ser tentados novamente.

### 3.1 Bootstrap humano da primeira conta Administrador

`POST /administracao/usuarios` pressupõe um Administrador autenticado e, por
isso, não resolve a criação da primeira conta canônica `administrador`. Antes
do Apply, uma pessoa autorizada deve identificar explicitamente essa primeira
conta e aprovar o procedimento administrativo nativo no Xano. O procedimento
deve usar o mecanismo nativo de senha, registrar a evidência necessária sem
expor senha, hash ou token e não pode converter automaticamente um registro
legado `admin`.

Esse bootstrap não será executado durante Propose nem incorporado como endpoint
autônomo ou fluxo público. Sem a autorização humana específica, o Apply deve
parar antes de criar ou alterar dados de usuário. Criar uma conta pelo endpoint
que ele próprio protege foi rejeitado por violar a autorização; converter
`admin` foi rejeitado porque o valor legado permanece não oficial.

O bootstrap humano foi aprovado para uma nova conta dedicada. Parâmetros
operacionais e sensíveis não são versionados; a execução remota continua
dependente de autorização própria e não integra este Apply local.

### 4. Senha pelo campo nativo do Xano

Senha temporária e nova senha serão inputs `sensitive`, validados no backend
com mínimo de oito caracteres, e gravados somente no campo nativo `password`.
Não haverá hash próprio, coluna auxiliar, retorno, log ou histórico de senha.

Antes do Apply, o Xano Developer MCP deve confirmar a sintaxe XanoScript
compatível para escrever esse campo e se a alteração no fluxo autenticado usa o
hash nativo como no schema. A implementação não deve manipular representação
interna de senha caso essa confirmação difira da expectativa atual.

O gate técnico pré-Apply confirmou escrita e atualização nativas de `password`,
inputs `sensitive`, transação para senha e flag e compatibilidade com Free. A
validação runtime continua posterior a push autorizado.

### 5. Gate backend central de primeiro acesso

`obter_identidade` passará a fornecer o estado necessário ao `/me`. A função
central de autorização receberá uma distinção explícita entre operações
funcionais normais e as exceções mínimas de primeiro acesso. Para identidade
pendente, operações normais serão rejeitadas antes de suas regras específicas;
somente `/me` e a troca autenticada da própria senha serão permitidos. Logout
continua local no Reflex e não requer nova API.

O gate será integrado à função central existente em vez de repetir checks em
cada endpoint. Endpoints que já chamam essa função precisam ser cobertos na
validação; qualquer endpoint humano que não a chama precisa ser identificado e
integrado no Apply, para que não reste bypass. A interface é defesa de jornada,
não a autorização.

### 6. Troca autenticada coerente

O endpoint específico de primeiro acesso usa a identidade do token como único
alvo e recebe somente `nova_senha`. Ele verifica pendência e tamanho, atualiza
o campo nativo e apenas então remove a pendência, de forma atômica ou com a
unidade de escrita coerente que o Xano Developer MCP confirmar. Se a unidade
atômica não estiver disponível no plano Free, o Apply deve parar para decisão
humana; não pode aceitar estado intermediário que limpe a flag sem nova senha.

Exigir novamente a senha temporária foi rejeitado porque o login que emitiu o
token já a verificou; aceitar identificador de usuário no payload foi rejeitado
porque permitiria alteração de outra conta.

### 7. Sessão e interfaces Reflex mínimas

O DTO de `/me`, cliente e `AuthState` passam a manter a flag apresentável. A
resolução de destino prioriza primeiro acesso quando a flag é verdadeira;
quando falsa, escolhe `/gerente`, `/tecnico`, `/diretoria` ou
`/administracao`. O guard compartilhado aplica essa regra em todo carregamento
protegido e evita acesso indevido por URL direta ou permanência na página de
primeiro acesso após a conclusão.

`/administracao` reutiliza a casca autenticada e contém somente o formulário
de criação. A seleção de Gerente mostra/exige Loja; os demais papéis não
enviam o campo. As confirmações de senha são locais e não substituem a
validação de oito caracteres no Xano. A rota exclusiva de primeiro acesso tem
somente nova senha, confirmação e ação de salvar.

### 8. Compatibilidade operacional e plano Free

O desenho usa tabela, campo `password`, endpoint funcional, autenticação e
funções já presentes no Xano, sem tarefas agendadas, add-ons, mensageria ou
serviço externo. A disponibilidade no plano Free e o comportamento da escrita
de senha e atomicidade devem ser confirmados pelo Xano Developer MCP antes de
qualquer push; nenhuma dependência paga é assumida.

## Risks / Trade-offs

- **[Bypass em endpoint humano sem autorização central]** → inventariar todas
  as APIs autenticadas e garantir integração ao gate antes do push.
- **[Escrita de senha e flag não coerente]** → confirmar a unidade atômica no
  MCP e não implementar solução parcial.
- **[Flag com default incorreto bloqueia contas existentes]** → criar campo com
  default `false`, sem backfill, e testar um registro preexistente.
- **[Senha exposta por DTO ou erro]** → usar DTOs públicos, inputs sensíveis e
  testes que inspecionem responses e logs de cliente.
- **[Guard Reflex confundido com segurança]** → testar chamada direta ao
  backend com sessão pendente e manter o gate no Xano.
- **[Ampliação indevida do Administrador]** → autorizar nesta change somente o
  endpoint administrativo especificado; outras capacidades exigem change.
- **[Ausência de primeira conta administrativa]** → exigir identificação e
  autorização humana explícitas para o bootstrap nativo no Xano antes do Apply,
  sem criar ou converter contas automaticamente.

## Migration Plan

1. Obter autorização humana explícita que identifique a primeira conta
   `administrador`, aprovar o procedimento nativo Xano e definir o registro
   seguro da execução, sem expor senha ou converter `admin`.
2. Confirmar com o Xano Developer MCP a escrita segura no campo `password`, a
   unidade de atualização e a compatibilidade dos recursos com Free.
3. Alterar o schema de perfil e adicionar o booleano com default `false`, sem
   editar registros existentes nem executar backfill.
4. Estender identidade, login e autorização central; criar e validar os dois
   endpoints funcionais sem desbloquear CRUD genérico.
5. Adaptar o cliente, State, guards e as duas telas Reflex.
6. Executar testes locais, validação XanoScript, dry-run Xano, revisão do diff
   e validação runtime/E2E com dados autorizados.

Rollback: remover os endpoints e a UI desta change, reverter o enum e a flag
somente por procedimento aprovado que preserve contas já criadas. Não apagar
usuários nem alterar senhas como ação de rollback automática.
