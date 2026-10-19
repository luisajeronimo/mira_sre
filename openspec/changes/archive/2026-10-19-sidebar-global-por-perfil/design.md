# Design

## Context

Veja `proposal.md` para a motivação. A casca atual em `app/components/layout.py`
é reutilizada pelas páginas autenticadas, mas combina topbar e conteúdo sem uma
fonte central de itens. A sessão somente é utilizável após `/me`; loading e
primeiro acesso já são composições sem casca.

O monitoramento atual usa `GET /ativos_referencia`, cujo contrato genérico
preserva consulta do Gerente à própria Loja. Essa rota não pode ser reutilizada
para a nova regra de monitoramento global sem alterar consumidores existentes.

## Goals / Non-Goals

**Goals:**

- Concentrar composição, itens e seleção ativa da navegação desktop em
  componentes compartilhados.
- Exibir a navegação somente depois da identidade confirmada, em uma única
  sidebar desktop.
- Aplicar a mesma matriz aprovada no guard Reflex e no contrato Xano dedicado
  de monitoramento.
- Servir o logo oficial como asset sem alterar suas formas, cores ou proporção.

**Non-Goals:**

- Não criar destinos de navegação, dashboards, dados operacionais ou permissões
  além da matriz aprovada.
- Não alterar `GET /ativos_referencia`, sua semântica ou seus consumidores.
- Não usar visibilidade ou rota como substituto da autorização Xano.
- Não introduzir persistência de token ou sessão no navegador.

## Decisions

### Configuração única da navegação e casca única

Uma definição estática central reúne rótulo, rota, ícone e perfis permitidos.
Uma var derivada do perfil confirmado seleciona seus itens, e a casca única
renderiza tanto a sidebar quanto o conteúdo das páginas autenticadas.

Isso elimina listas paralelas e permite que uma inclusão futura altere uma
única configuração. Cada página mantém seu guard e sua consulta funcional; a
casca não decide acesso a dados.

Alternativas consideradas:

- Repetir `rx.cond` e links em cada página: rejeitada por duplicar a matriz.
- Converter a configuração em dados vindos do Xano: rejeitada porque a matriz é
  comportamento de interface aprovado e não exige novo contrato ou persistência.

### Rota canônica da listagem e compatibilidade

A seleção ativa usa a rota explícita dos itens configurados. `/inicio` é a
listagem canônica de chamados para todos os perfis; não há item Chamados na
sidebar. A rota `/chamados` permanece registrada somente como redirecionamento
protegido para `/inicio`, sem iniciar a jornada de listagem duplicada nem
limpar o State de filtros da sessão. `/chamados/novo` e
`/chamados/[chamado_id]` continuam rotas funcionais sem item de navegação.

Alternativa considerada: manter duas páginas de lista com o mesmo dispatcher.
Rejeitada porque duplica a jornada canônica e cria risco de divergência de
filtros ou carregamento.

### Navegação exclusivamente desktop

O MIRA é exclusivamente Web desktop. A casca renderiza uma única sidebar fixa
ao lado do conteúdo; não possui drawer, gatilho de menu, breakpoints de
navegação nem estado efêmero de abertura.

Alternativa considerada: drawer para telas estreitas. Rejeitada pela decisão
humana de não oferecer interface mobile nesta change.

### Logo oficial como asset público controlado

`docs/design/references/logo.svg` permanece a referência de design. A change
copia seu conteúdo para `assets/mira-logo.svg`, usado pela casca em dimensão
desktop que preserva a razão de aspecto. Um teste verifica que o asset de
aplicação corresponde à referência, prevenindo deriva silenciosa.

Alternativa considerada: apontar a interface diretamente para `docs/`.
Rejeitada porque esse diretório não é um asset público do Reflex. Redesenho por
texto ou ícone genérico é incompatível com `DESIGN.md`.

### Contrato dedicado de monitoramento

O grupo MIRA Service Desk recebe `GET /monitoramento/ativos`, apoiado por função
dedicada que chama `autorizacao/exigir_perfil` para Técnico, Diretoria e
Administrador. O cliente Reflex usa somente esse contrato na página de
monitoramento; o guard local usa a mesma matriz para redirecionar Gerente antes
da consulta. O contrato retorna o DTO de monitoramento já usado pela página.

Alternativas consideradas:

- Restringir `GET /ativos_referencia`: rejeitada porque quebraria seu escopo
  atual de Gerente e possíveis consumidores.
- Ocultar somente o item: rejeitada porque URL e chamada direta continuariam
  alcançando o endpoint genérico.

## Risks / Trade-offs

- [Casca nova altera várias páginas autenticadas] → preservar seus guards e
  estados atuais, cobrir rota canônica, redirecionamento compatível e aliases,
  e compilar Reflex.
- [Matriz de UI diverge da autorização] → testar explicitamente guard Reflex e
  HTTP 403 do novo contrato para Gerente; o Xano permanece a autoridade.
- [Logo de referência e asset servido divergem] → testar igualdade do conteúdo
  ou hash entre os dois arquivos.
- [Novo endpoint Xano pode afetar recursos fora do escopo] → validar somente os
  arquivos Xano adicionados, revisar dry-run completo e publicar seletivamente
  após autorização humana.

## Migration Plan

1. Adicionar o asset, a configuração de navegação desktop e a casca
   compartilhada.
2. Migrar as páginas autenticadas para a casca, preservando login, primeiro
   acesso, aliases e estados de revalidação sem sidebar.
3. Criar e validar localmente o contrato dedicado de monitoramento; atualizar o
   cliente e o guard Reflex para usá-lo.
4. Executar testes Python, compilação Reflex, validação XanoScript, OpenSpec
   strict e dry-run Xano. Publicação Xano requer autorização humana separada.

Rollback: reverter a implantação desta change restaura a casca anterior e o
cliente pode voltar ao contrato genérico, que não será modificado por esta
change. O novo contrato não cria nem altera dados operacionais.
