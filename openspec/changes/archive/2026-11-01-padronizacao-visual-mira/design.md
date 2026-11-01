# Design

## Context

A casca autenticada existente já centraliza a sidebar, o logotipo oficial, a
identidade da sessão e o logout. A rota `/inicio` despacha a fila global para
Técnico, Diretoria e Administrador, enquanto a matriz de itens continua em
configuração central. O recorte usa a linguagem de `DESIGN.md` e as referências
visuais apenas como apresentação, conforme as specs desta change.

## Referência visual desta change

Além dos PNGs locais, esta change registra o [Figma — MIRA: identidade e telas
de referência](https://www.figma.com/design/W5qbds0Ec5MtqEIfZ4MvRk/Untitled?node-id=0-1&p=f&t=DiOMFvvtzpFX0sUO-0).
Ele foi consultado para hierarquia, proporção, espaçamento e acabamento; não
define dados, ações, métricas ou comportamento fora das specs vigentes.

Para a abertura manual, a referência direta é o
[frame `1:1215` — Abertura de Novo Chamado](https://www.figma.com/design/W5qbds0Ec5MtqEIfZ4MvRk/Untitled?node-id=1-1215&t=iWyZTYhKtYxwS6Pr-0),
complementado por `docs/design/references/abrir-chamado.png`.

Para o login, a referência direta é o
[frame `1:546` — Autenticação e Acesso](https://www.figma.com/design/W5qbds0Ec5MtqEIfZ4MvRk/Untitled?node-id=1-546&t=iWyZTYhKtYxwS6Pr-0),
complementado por `docs/design/references/login.png`. Por decisão explícita, o
título ilustrativo de autenticação é substituído pelo logotipo oficial de
`docs/design/references/logo.svg`, exibido em tamanho destacado.

## Goals / Non-Goals

**Goals:**

- Tornar a casca desktop e a fila global visualmente consistentes com a
  identidade clara, rose/ruby, tipografia, superfícies e escala de espaçamento
  definidos.
- Centralizar estilos reutilizáveis para sidebar, topbar, cabeçalho, filtros,
  cards, botões, tabelas, grids de dados e badges.
- Aplicar ao login público a composição em painel dividido da referência, com
  marca oficial destacada e o formulário existente preservado.
- Preservar integralmente eventos, State, rotas e contratos atuais.

**Non-Goals:**

- Redesenhar formulários administrativos ou fluxos públicos além do login
  explicitamente autorizado neste recorte.
- Criar dashboard, métricas, busca global, item de navegação, drawer mobile,
  endpoint ou componente React externo além do seletor local de intervalo
  explicitamente autorizado nesta change.
- Alterar dados, autorização, filtros, ordenação, escopos rápidos ou ações.

## Decisions

### Tokens locais em CSS do Reflex

Definir cores, fontes, espaçamentos, raios e sombras como constantes de
apresentação no módulo compartilhado e aplicá-las por props Reflex. Isso mantém
o tema nativo `ruby` e permite que páginas existentes adotem o padrão sem
alterar State. Variáveis CSS globais foram descartadas; a única exceção de
biblioteca é `react-day-picker@9.14.0`, autorizada exclusivamente para o
seletor de intervalo local descrito abaixo.

### Casca única com topbar informativa

Evoluir `casca_conteudo` para combinar a sidebar atual com uma topbar desktop
que concentra a única identificação da sessão e o logout existente. A topbar
não recebe novas ações nem modifica a configuração `ITENS_NAVEGACAO`; ela só
reorganiza elementos já renderizados. Duplicar a casca em cada página foi
descartado para preservar consistência.

### Fila global composta com componentes Reflex existentes

Reaproveitar `rx.card`, `rx.button`, `rx.table`, `rx.badge`, `rx.input` e
`rx.select`, compondo wrappers simples para rótulos de filtro, pares de data,
campos de informação e badges. Tabelas, dados e handlers permanecem os mesmos.

### Informações e comentários compactos

Apresentar detalhes em grid de campos com rótulo acima do valor e comentários
em cards com autor e conteúdo à esquerda, data e visibilidade à direita. O
State continua responsável pela ordem e pelos dados.

### Badge semântico único

Criar componente visual compartilhado que aplique maiúsculas e cores semânticas
a status e visibilidades, inclusive `online` e `offline`, sem normalizar ou
persistir o valor recebido.

### Grade de filtros e cabeçalho de tabela compartilhados

Compor filtros em grade desktop de 12 colunas por wrappers compartilhados:
cada grupo mantém seu rótulo, controles com mesma altura e grupo de ações
identificado. As ações permanecem no topo do painel, os períodos usam rótulo
do critério e campos `De`/`Até` na mesma linha, e o painel recebe padding de
24 px. Cabeçalhos de tabelas usam rose sólido, texto branco forte e setas
visíveis. As colunas compartilham largura igual, exceto a de título/chamado,
que recebe o espaço remanescente; as células são centralizadas nos dois eixos,
salvo o título e sua ocorrência, mantidos à esquerda para leitura. Superfícies
sem padding que contêm tabelas recortam o conteúdo na curvatura para não
encobrir a borda. Assim, Gerente e jornada global recebem o mesmo acabamento
sem alterar handlers, valores ou resultados.

### Acabamento de tabelas, detalhes e histórico

Os cabeçalhos ordenáveis ocupam toda a célula interativa, sem aparência de
cápsula, e usam hover rose mais escuro. Badges operacionais mantêm preenchimento
confortável; `NOVO` usa o rose da paleta. No detalhe, identificador e título
compartilham uma faixa com a ação existente do Totem à direita. Campos de
informação usam superfície branca, labels fortes e borda rose sutil. Comentários
e eventos usam cards limpos com a mesma borda; alterações múltiplas ficam em
grade de duas colunas, sem alterar conteúdo ou cronologia.

O hover de cabeçalho modifica exclusivamente sua cor de fundo e preserva todas
as dimensões. As tabelas devem caber no desktop sem barra horizontal; a quebra
de texto protege o conteúdo e não omite colunas. O painel de dados usa uma
única superfície branca com grade limpa; somente a descrição recebe área própria.
O campo de comentário aplica borda e preenchimento diretamente ao controle,
sem contêiner cinza intermediário.

O detalhe de Gerente e da jornada global compartilha a mesma hierarquia: uma
única faixa apresenta `Chamado #ID - título` com tipografia uniforme e a ação
existente do Totem em tamanho destacado; o painel de dados contém somente o
cabeçalho e o grid funcional. Descrição e composição de comentário/tratativa
ficam como seções irmãs fora desse painel. A origem recebe somente transformação
visual para maiúsculas, sem modificar o valor retornado ou persistido.
A descrição permanece como seção irmã, mas usa a mesma superfície branca do
painel de dados para evitar contraste de fundo desnecessário.

Na fila global, o número do chamado permanece como acesso ao detalhe. A coluna
visual `Ações`, que repetia esse mesmo destino, é omitida para Técnico,
Diretoria e Administrador; as colunas restantes redistribuem o espaço liberado.
A célula de título segue a composição já usada pelo Gerente, com o título na
primeira linha e uma prévia compacta da descrição logo abaixo, reutilizando os
dados existentes sem alterar o contrato da fila.

### Seletor de intervalo local

Usar um wrapper local e client-side de `react-day-picker@9.14.0` em modo
`range`, com versão npm fixada. O primeiro dia selecionado preenche `De`, o segundo
preenche `Até`; o wrapper devolve strings ISO locais aos handlers de interface
que atualizam exatamente os campos de filtro já existentes. O calendário usa
as variáveis de cor rose do MIRA, é renderizado em portal no documento para não
ser recortado por superfícies ancestrais e só sincroniza os campos após o
segundo dia, fechando quando o intervalo estiver completo. Somente os dias
inicial e final recebem o círculo rose, enquanto os dias intermediários usam
fundo rose claro e texto neutro. Não haverá endpoint, persistência, regra de
negócio ou biblioteca Python nova.

### Abertura manual em superfície estruturada

Reorganizar somente `_formulario` da jornada do Gerente: cabeçalho com retorno
existente, uma superfície principal `Dados do chamado`, título em largura
total, Totem e Categoria em duas colunas, prioridades existentes em opções
horizontais, descrição ampla e faixa inferior separada para ações. A seleção
visual de prioridade continua chamando o handler e usando os valores já
definidos no State (`Baixa`, `Média`, `Alta` e `Urgente`), sem copiar a opção
`Crítica` nem os exemplos de SLA do Figma. `Limpar`, `Descartar`, `Voltar` e o
envio permanecem distintos e ligados aos eventos atuais. Não haverá formulário
para outros perfis, campo, validação, cálculo ou contrato novo.

### Login público em painel dividido

Reorganizar somente `app/pages/login.py` em uma superfície central desktop com
duas colunas: à esquerda, painel de identidade e contexto visual do produto; à
direita, o formulário existente. O canvas claro, superfícies brancas, bordas,
sombra baixa, tipografia e acento rose seguem os tokens compartilhados. No topo
do formulário, usar `/mira-logo.svg`, cópia byte a byte do arquivo oficial
`docs/design/references/logo.svg`, em tamanho maior e com proporção preservada,
substituindo o texto ilustrativo `Autenticação no sistema`.

Manter somente os controles funcionais existentes: e-mail, senha, mensagem de
erro e envio com estado de carregamento. Seletor de perfil, recuperação de
senha, exibição de senha, lembrança de acesso, 2FA e federação presentes na
referência não são autorizados e não serão simulados. O painel esquerdo pode
reproduzir hierarquia, superfícies e linguagem operacional sem apresentar
métricas fictícias como fatos do sistema. Não haverá alteração de State, evento,
rota, autenticação, contrato Xano ou redirecionamento.

## Risks / Trade-offs

- [Fontes externas indisponíveis no ambiente] → declarar a família desejada
  com fallbacks do sistema, sem bloquear a renderização.
- [Estilos visuais encobrirem estados de interação] → manter rótulos, ícones,
  `disabled`, `aria-current` e foco visível já existentes.
- [Casca compartilhada afetar páginas fora do recorte] → validar a compilação
  das rotas e limitar a topbar a elementos de sessão existentes.

## Migration Plan

1. Aplicar os tokens e a casca compartilhada, sem remover a navegação atual.
2. Aplicar o cabeçalho e os estilos da fila global em `/inicio`.
3. Validar testes focados, compilação Reflex e as specs da change.
4. Em caso de regressão visual, reverter somente os props de apresentação; não
   há dados nem contrato para migrar.
