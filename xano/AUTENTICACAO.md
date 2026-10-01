# Autenticação e autorização no Xano

Este documento registra o contrato local e o plano operacional aprovado pela change
`autenticacao-perfis-autorizacao`. Ele não contém credenciais e não executa nenhuma
alteração remota.

## Modelo de identidade

- A tabela autenticável é `usuarios`.
- Os únicos perfis oficiais persistidos são `gerente`, `tecnico` e `diretoria`.
- `usuarios.lojas_id` é uma referência direta e opcional a `lojas`.
- O campo `lojas_id` é fonte de escopo somente para `gerente`.
- Um Gerente sem Loja válida falha de forma fechada nas consultas dependentes de
  unidade.
- Técnico e Diretoria não obtêm escopo nem permissões a partir de `lojas_id`.

## Plano de normalização de dados

Aplicar, como uma única etapa revisável, somente o mapeamento aprovado:

| Valor existente | Valor canônico |
|---|---|
| `tecnico_n1` | `tecnico` |
| `tecnico_n2` | `tecnico` |
| `tecnico_n3` | `tecnico` |
| `diretor` | `diretoria` |
| `gerente` | `gerente` |

Qualquer valor diferente dos listados deve interromper a migração para nova decisão
humana. Os valores legados não serão preservados como perfis ou níveis técnicos.

Aplicar somente os vínculos de configuração/teste aprovados:

| Usuário | `usuario_id` | `loja_id` | Loja |
|---|---:|---:|---|
| Thiago Pereira | 8 | 1 | Loja Paulista |
| Isabelly Garcia | 10 | 2 | Loja Vila Mariana |

Antes da aplicação, deve ser verificado no ambiente alvo que os identificadores ainda
correspondem aos nomes revisados e que nenhuma outra conta Gerente será alterada.

## Credenciais

As credenciais iniciais devem ser preparadas diretamente pelos mecanismos nativos do
Xano. Senhas, hashes reutilizáveis, tokens e valores específicos do ambiente não devem
ser gravados no repositório nem retornados pelos endpoints. Esta change não cria
cadastro público, recuperação de senha ou administração de usuários.

## Contrato destinado ao Reflex

O grupo `MIRA Auth` oferece:

- `POST /login`, com `email` e `senha`, retornando somente `authToken` quando as
  credenciais e o perfil oficial forem válidos; o token expira em 8 horas;
- `GET /me`, autenticado por token da tabela `usuarios`, retornando somente `id`,
  `nome`, `email`, `role` e `lojas_id`.

O mesmo erro público de credenciais é usado para e-mail inexistente, senha incorreta
e perfil não oficial. O Reflex apenas envia as credenciais, guarda/usa o token e
apresenta a interface correspondente; validação de senha, perfil e escopo permanece
no Xano. Esta change não fornece refresh token nem renovação automática.

## Limites da sincronização pendente

Após aprovação do diff completo e habilitação explícita de push, a sincronização deve
ser limitada a:

1. alteração da tabela `usuarios` para autenticação nativa, perfis canônicos, senha
   sensível, referência de Loja e unicidade de e-mail;
2. criação do grupo e dos endpoints de autenticação;
3. criação das funções reutilizáveis de autorização;
4. proteção das rotas de usuário inventariadas;
5. normalização dos perfis e aplicação dos dois vínculos acima;
6. preparação das credenciais pelo mecanismo do Xano, fora do versionamento.

O POST de telemetria do Simulator e o endpoint de verificação de heartbeat do Fiscal
devem permanecer inalterados. Nenhum push deve ser executado enquanto
`allow_push` estiver desabilitado ou antes da aprovação humana do diff.

## Inventário de rotas e política de acesso

| Grupo/recurso | Operação | Classificação e política desta change |
|---|---|---|
| `MIRA Auth` | `POST /login` | Pública; autentica credenciais e emite token de 8 horas. |
| `MIRA Auth` | `GET /me` | Usuário autenticado; retorna apenas a identidade pública. |
| `lojas` | GET lista/detalhe | Gerente: somente a Loja vinculada; Diretoria: consulta global; Técnico: negado. |
| `ativos_referencia` | GET lista/detalhe | Gerente: somente Ativos da Loja vinculada; Técnico e Diretoria: consulta global. |
| `chamados` | GET lista/detalhe | Gerente: somente Chamados de Ativos da Loja vinculada; Técnico e Diretoria: consulta global. |
| `telemetria_equipamentos` | GET lista/detalhe | Gerente: somente Telemetria de Ativos da Loja vinculada; Técnico e Diretoria: consulta global. |
| `categorias_servico` | GET lista/detalhe | Consulta autenticada para os três perfis oficiais. |
| `interacoes_chamado` | GET lista/detalhe | Gerente: somente interações de Chamados de sua Loja; Técnico: consulta necessária à tratativa; Diretoria: negado. |
| `usuarios` | GET lista/detalhe | Negado; a única consulta de identidade permitida é `GET /me`. |
| CRUDs genéricos | POST, PATCH e DELETE | Autenticação obrigatória e negação para os três perfis oficiais. |
| `telemetria_equipamentos` | POST | Rota do Simulator; exige exclusivamente `X-MIRA-Simulator-Key`, comparado no Xano a `MIRA_SIMULATOR_AUTOMATION_KEY` antes de persistir. |
| `verificar-falhas` | GET | Rota disparada pelo Fiscal; exige exclusivamente `X-MIRA-Fiscal-Key`, comparado no Xano a `MIRA_FISCAL_AUTOMATION_KEY` antes de consultar heartbeat. |

As regras são aplicadas por rota, sem proteção indiscriminada do grupo que contém as
duas automações. Identificadores enviados pelo cliente localizam recursos, mas nunca
substituem o vínculo `usuarios.lojas_id` usado para autorizar um Gerente.

## Matriz de validação local

| Cenário | Evidência local antes da sincronização |
|---|---|
| Credenciais válidas | Teste inline do login verifica a emissão de `authToken`; o token é criado com `expiration = 28800`. |
| E-mail inexistente ou senha incorreta | Testes inline percorrem ambos os casos e a implementação converge para a mesma mensagem pública. |
| Perfil não oficial | Testes inline rejeitam `admin`, os três níveis técnicos legados, `diretor` e valor desconhecido. |
| Token ausente ou inválido | Todas as rotas de usuário, exceto login, declaram `auth = "usuarios"`; a rejeição ocorre antes do stack. |
| Resposta sem credencial | Testes de resposta do login e da identidade verificam que `senha` não é exposta. |
| Isolamento entre Lojas | Testes inline cobrem os vínculos 8→1 e 10→2, o acesso cruzado e Gerente sem Loja. |
| Técnico | As consultas de Chamado, Ativo e Telemetria permitem somente o perfil canônico `tecnico`; mutações genéricas são negadas. |
| Diretoria | As consultas globais inventariadas permitem `diretoria`; mutações genéricas são negadas. |
| Operação não prevista | A função de negação por padrão é chamada antes de qualquer operação de escrita nos CRUDs genéricos. |
| Simulator e Fiscal | Os dois arquivos de endpoint permanecem idênticos ao estado anterior à change. |

Os testes inline e a validação estática são a verificação disponível antes da
sincronização. A matriz crítica deve ser executada novamente no runtime do Xano após
a sincronização aprovada, conforme a tarefa 6.4.
