# Design: Padronização de rotas do frontend

## Context

O Reflex registra páginas em `app/app.py`. Hoje, a lista e o detalhe do
Gerente usam `ChamadosGerenteState`; a fila e o detalhe globais usam
`ChamadosTecnicoState`. Esses States têm escopos, componentes e contratos Xano
deliberadamente distintos. `AuthState` confirma a identidade por `GET /me` e
define os destinos de sessão. A casca atual já contém o botão `Início` e não há
sidebar funcional a redesenhar.

O design visual permanece inalterado: reutilizar a casca, tabelas, formulários,
feedbacks e estados de carregamento existentes. A mudança só substitui os
destinos e a organização das URLs.

## Goals / Non-Goals

**Goals:**

- Fazer a URL representar a funcionalidade, não o perfil.
- Usar `/inicio` para os quatro perfis após confirmação de identidade.
- Reutilizar os componentes e States atuais de chamados conforme o perfil.
- Preservar acesso direto protegido, primeiro acesso, 401, 403 e os aliases
  legados transitórios.

**Non-Goals:**

- Unificar `ChamadosGerenteState` e `ChamadosTecnicoState`.
- Alterar autorização, contratos, endpoints ou dados do Xano.
- Alterar a tratativa operacional, criar dashboards, sidebar, atalhos ou nova
  apresentação visual.

## Decisions

### Rotas canônicas e aliases

| Canônica | Jornada |
|---|---|
| `/` | dispatcher de sessão existente |
| `/login` | login público existente |
| `/primeiro-acesso` | troca obrigatória existente |
| `/inicio` | início compartilhado por perfil |
| `/chamados` | lista contextual por perfil |
| `/chamados/novo` | abertura manual do Gerente |
| `/chamados/[chamado_id]` | detalhe contextual por perfil |
| `/monitoramento` | comportamento atual para sessão autenticada |
| `/administracao/usuarios` | criação administrativa existente |

As rotas antigas continuam registradas apenas como aliases protegidos:
`/gerente`, `/gerente/chamados/novo`, `/gerente/chamados/[chamado_id]`,
`/tecnico`, `/tecnico/chamados/[chamado_id]`, `/diretoria` e
`/administracao`. Depois da revalidação, elas redirecionam à rota canônica
equivalente; aliases de detalhe preservam o identificador. Não renderizam uma
jornada própria. Se o perfil não puder acessar a funcionalidade de destino, o
guard o leva a `/inicio`; sem sessão, vai a `/login`; com troca pendente, a
`/primeiro-acesso`.

Não é definido prazo de remoção desses aliases. A retirada da compatibilidade é
decisão posterior.

### Resolução simples por perfil

`/inicio` e `/chamados` usam um dispatcher fino de rota, não um framework de
roteamento. Ele revalida a identidade antes de escolher a jornada existente:

- Gerente: lista local de chamados e State do Gerente.
- Técnico, Diretoria e Administrador: fila global e State técnico.

`/chamados/[chamado_id]` usa a mesma escolha: detalhe local com comentários
públicos para Gerente; detalhe global com timeline e tratativa para os demais.
`/chamados/novo` aceita somente Gerente. `/inicio` pode reutilizar a mesma
apresentação de `/chamados`, sem duplicar carga ou componentes.

O registro deve garantir que a rota estática `/chamados/novo` seja resolvida
antes da dinâmica `/chamados/[chamado_id]`, conforme a semântica de precedência
do Reflex, com teste de regressão e validação de compilação.

### Segurança, navegação e backend

O dispatcher, os aliases e os links internos usam a identidade revalidada, mas
não autorizam dados. Chamadas de Gerente continuam nos contratos `/gerente/*`;
chamadas globais continuam em `/tecnico/*`; administração continua em
`/administracao/*`. Xano continua avaliando token, troca pendente, perfil e
escopo de Loja.

Login, raiz, acesso a `/login` por sessão confirmada e conclusão de primeiro
acesso passam a direcionar a `/inicio`. O botão `Início`, retornos de detalhes,
formulários e links das tabelas apontam para as rotas canônicas. Em 401, a
sessão continua sendo limpa e o destino é `/login`; em 403, ela é preservada.

## Risks / Trade-offs

- Uma URL comum não pode escolher componente antes de confirmar a identidade;
  por isso a carga deve manter o estado neutro existente até a revalidação.
- Aliases prolongam temporariamente o registro de rotas, mas preservam links e
  favoritos sem manter implementações duplicadas.
- Erro na precedência de `novo` poderia tratá-lo como identificador dinâmico;
  a implementação precisa cobrir essa resolução explicitamente.
- A mudança de rota altera testes de chaves Reflex, destinos e redirects; não
  deve alterar testes de URL dos clientes Xano.
