# Proposal

## Why

A interface autenticada atual já preserva jornadas e permissões aprovadas, mas
a casca, a hierarquia da página inicial global e seus controles ainda não
expressam de modo consistente a linguagem visual definida em `DESIGN.md`.
Este primeiro recorte transforma os padrões visuais já aprovados em interface
concreta e reutilizável, priorizando o desktop.

## What Changes

- Padronizar a casca autenticada desktop com canvas claro, sidebar, topbar de
  contexto, foco visível e o logotipo oficial existente, sem alterar destinos
  ou a matriz por perfil.
- Aplicar tokens visuais e tema Reflex coerentes para cor rose/ruby,
  tipografia, espaçamento, bordas, superfícies, botões e cards.
- Padronizar o cabeçalho compartilhado e aplicar a composição à página
  `/inicio` da jornada global usada por Técnico, Diretoria e Administrador.
- Reorganizar apenas a apresentação dos controles, filtros e tabela existentes
  da fila global, mantendo todos os campos, ações, estado e contratos atuais.
- Estender o padrão às listas, detalhes e comentários existentes, preservando
  dados, ordem, visibilidade e ações, com status visuais em maiúsculas.
- Refinar filtros, cabeçalhos de tabela e ação de saída conforme a referência
  visual registrada, sem modificar os contratos de consulta ou sessão.
- Substituir somente a apresentação dos pares de data por seletor visual de
  intervalo, mantendo os mesmos valores `De`/`Até` nos filtros existentes.
- Reorganizar visualmente a abertura manual do Gerente em seção de dados e
  faixa de ações coerentes com a referência específica do Figma, preservando
  campos, prioridades, validações e envio atuais.
- Reorganizar visualmente a página pública de login em painel dividido e
  destacar o logotipo oficial, preservando exclusivamente os campos, mensagens,
  carregamento, autenticação e redirecionamentos já existentes.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `navegacao-lateral-perfis`: define a apresentação compartilhada desktop da
  casca autenticada, preservando destinos e acessibilidade já aprovados.
- `frontend-sessao-navegacao`: define a composição visual da página inicial
  global e do login público sem alterar a jornada, os dados ou a autorização.
- `chamados-fila-atribuicao-tecnica`: apresentação da fila e detalhe globais.
- `frontend-chamados-gerente`: apresentação da lista, detalhe e comentários locais.
- `monitoramento-disponibilidade-totens`: apresentação de estados operacionais.

## Impact

- Afeta somente componentes e páginas Reflex de apresentação: tema, casca,
  cabeçalho compartilhado, listagens, detalhes, comentários e badges.
- Não altera Xano, APIs, autenticação, filtros, ordenação, permissões ou rotas.
- Adiciona somente a dependência frontend fixada `react-day-picker` para o
  seletor visual de intervalo; não introduz pacote Python nem contrato remoto.
- O restante das páginas protegidas receberá a casca compartilhada, mas seus
  conteúdos próprios não serão redesenhados neste recorte.
- A abertura manual continua exclusiva do Gerente e não altera State, payload,
  catálogos, SLA, permissões ou contratos remotos.
- O login mantém o mesmo formulário, State, contrato Xano, mensagens e destinos;
  nenhuma ação ilustrativa da referência visual é incorporada ao produto.
