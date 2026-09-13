## Why

O MIRA possui usuários e APIs no Xano, mas o snapshot local não representa autenticação nem autorização compatíveis com as responsabilidades de Gerente, Técnico e Diretoria. Esta change estabelece a fundação de acesso antes da implementação das jornadas do Reflex e impede que controle de acesso seja delegado à interface.

## What Changes

- Habilitar a autenticação de usuários pelos mecanismos próprios do Xano, sem expor ou manipular credenciais como dados de negócio no Reflex.
- Disponibilizar contratos de login e identificação do usuário autenticado para consumo futuro pelo Reflex, com token de autenticação válido por 8 horas.
- Restringir o conjunto de perfis oficiais a Gerente, Técnico e Diretoria, sem reconhecer `admin`, `tecnico_n1`, `tecnico_n2` ou `tecnico_n3` como perfis do domínio.
- Aplicar autorização no Xano conforme o perfil autenticado e as responsabilidades já definidas no domínio.
- Restringir o Gerente aos dados da unidade à qual estiver associado.
- Propor no design a representação da associação entre Gerente e Loja, mantendo essa decisão visível para revisão humana antes do Apply.
- Impedir que os três perfis oficiais recebam, por meio dos CRUDs genéricos existentes, operações administrativas ou destrutivas que não constam de suas responsabilidades documentadas.
- Manter fora do escopo alterações nas regras de heartbeat, SLA, chamados, telemetria e dashboards.
- Manter fora do escopo a autenticação do Simulator e do Fiscal, pois esta change não identifica requisito existente que exija alterar o acesso dessas automações.
- **BREAKING**: acessos anônimos a APIs destinadas aos usuários do MIRA deixarão de ser aceitos.
- **BREAKING**: os valores existentes `tecnico_n1`, `tecnico_n2` e `tecnico_n3` serão normalizados para `tecnico`, e `diretor` será normalizado para `diretoria`; qualquer outro valor não oficial não concederá acesso nem será convertido sem decisão humana explícita.

## Capabilities

### New Capabilities

- `autenticacao-usuarios`: autenticação no Xano, emissão de token com expiração de 8 horas, validação da sessão e consulta da identidade autenticada pelo Reflex.
- `autorizacao-perfis`: autorização no Xano para Gerente, Técnico e Diretoria, incluindo o escopo de unidade do Gerente e a negação de perfis não oficiais.

### Modified Capabilities

Nenhuma. Ainda não existem especificações consolidadas em `openspec/specs/`.

## Impact

- Modelo de usuários do Xano, incluindo sua habilitação para autenticação, vocabulário de perfis e associação proposta entre Gerente e Loja.
- Novos endpoints de autenticação e identificação do usuário autenticado.
- APIs Xano destinadas ao consumo por usuários, que passarão a exigir identidade autenticada e autorização executada no backend.
- Contrato futuro do Reflex com o Xano para login, manutenção da sessão, identificação do perfil e apresentação da navegação apropriada.
- Dados existentes serão normalizados somente pelo mapeamento aprovado nesta change; valores fora desse mapeamento exigirão nova decisão humana.
- Simulator e Fiscal permanecem inalterados.
