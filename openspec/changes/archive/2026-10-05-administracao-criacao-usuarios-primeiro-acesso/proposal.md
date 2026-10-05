# Proposal

## Why

O MIRA ainda não possui um perfil Administrador funcional, nem um fluxo seguro
para provisionar usuários humanos. Novas contas também precisam deixar de usar
uma senha temporária como acesso permanente, sem interromper as contas já
existentes.

## What Changes

- Introduz o perfil humano canônico `administrador` nos contratos de
  autenticação, identidade, autorização e navegação, sem reutilizar o valor
  legado `admin` e sem confundir o perfil com `bot_fiscalizacao`.
- Adiciona a capability administrativa mínima para que somente um Administrador
  autenticado crie um usuário por `POST /administracao/usuarios`, mantendo os
  CRUDs genéricos de `usuarios` bloqueados.
- Define os dados de criação: nome, e-mail único, perfil canônico, `lojas_id`
  somente para Gerente e senha temporária sensível com no mínimo oito
  caracteres. A resposta devolve somente a identidade pública criada.
- Adiciona o estado persistido de troca obrigatória de senha: novos usuários
  administrativos nascem pendentes; registros existentes permanecem não
  pendentes, sem backfill.
- Estende login, `/me`, autorização central e sessão Reflex para conduzir o
  usuário pendente exclusivamente à troca de senha e bloquear operações
  funcionais normais também no backend.
- Adiciona uma operação autenticada de troca obrigatória que recebe somente a
  nova senha, persiste-a pelo mecanismo nativo `password` do Xano e conclui o
  primeiro acesso apenas após sucesso coerente da alteração.
- Planeja as interfaces mínimas `/administracao` para criar usuários e a rota
  exclusiva de primeiro acesso, sem CRUD administrativo completo, listagem
  obrigatória, reset ou recuperação de senha.
- Estabelece como gate humano pré-Apply o bootstrap da primeira conta canônica
  `administrador`: a API administrativa não pode criar essa conta inicial e o
  procedimento nativo Xano depende de identificação e autorização humana
  explícitas, sem conversão automática de `admin` legado.

## Capabilities

### New Capabilities

- `administracao-usuarios`: criação administrativa mínima e segura de usuários
  humanos, incluindo a matriz de perfil, Loja e senha temporária.

### Modified Capabilities

- `autenticacao-usuarios`: reconhece `administrador`, expõe o estado de troca
  obrigatória em `/me` e restringe a sessão pendente ao fluxo mínimo permitido.
- `autorizacao-perfis`: inclui o Administrador na autorização central, concede
  somente a criação administrativa prevista e aplica o gate backend de primeiro
  acesso.
- `frontend-sessao-navegacao`: inclui a sessão e rota de Administrador, os
  guards de primeiro acesso e as telas mínimas de criação e troca de senha.

## Impact

- Xano: schema `usuarios`, enum de perfil, funções centrais de identidade e
  autorização, endpoints funcionais específicos de criação e troca de senha.
- Reflex: cliente Xano, `AuthState`, guards, roteamento, casca autenticada e
  duas interfaces mínimas.
- Testes: contratos XanoScript, cliente e State Reflex, proteção de rotas,
  autorização e validação runtime/E2E.
- O Apply precisa validar no Xano Developer MCP a escrita segura no campo
  `password` e a atualização coerente da senha com a flag, usando somente
  recursos compatíveis com o plano Free.
- O Apply depende de autorização humana explícita para identificar a primeira
  conta Administrador e aprovar o procedimento administrativo nativo Xano de
  bootstrap, com registro seguro sem expor senha.

## Fora do escopo

- Edição, exclusão, desativação, reset administrativo ou recuperação de senha.
- Mensageria de credenciais, MFA, CAPTCHA, expiração ou histórico de senhas.
- CRUD de Lojas ou Totens, dashboard administrativo, permissões granulares,
  grupos, equipes e ampliação automática do Service Desk.

## Decisões humanas pendentes

Não há nova decisão de produto ou arquitetura pendente: as regras de perfil,
Loja, senha temporária, primeiro acesso e compatibilidade foram aprovadas para
esta change. Permanecem os gates pré-Apply: confirmação técnica de sintaxe Xano
e atomicidade, e autorização humana explícita para a primeira conta
`administrador`; nenhum deles autoriza criar dados durante a Propose.
