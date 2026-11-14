# Produto — MIRA

<!-- impeccable:product-schema 1 -->

Contexto durável para orientar decisões de UX do MIRA, confirmado na
inicialização do Impeccable. Este registro resume o produto; não substitui os
requisitos funcionais de [OpenSpec](openspec/specs/), o
[modelo de domínio](docs/domain-model.md) ou a
[visão do projeto](docs/project-overview.md). Diretrizes visuais pertencem ao
[DESIGN.md](DESIGN.md).

## Platform

web

## Usuários

As decisões de UX devem equilibrar os quatro perfis humanos, respeitando o
trabalho e o escopo de cada um:

- **Gerente:** acompanha os Totens e chamados da própria Loja, relata problemas
  físicos ou operacionais e acompanha o retorno do atendimento.
- **Técnico:** consulta a fila global, organiza os atendimentos e registra a
  tratativa dos chamados até sua resolução.
- **Diretoria:** acompanha a operação e os indicadores consolidados da rede,
  além de atuar nos chamados conforme suas permissões.
- **Administrador do Sistema:** mantém os cadastros de Usuários, Lojas e Totens
  e atua na operação conforme suas permissões.

Técnico, Diretoria e Administrador compartilham os mesmos acessos
operacionais, incluindo indicadores, consumo de SLA e abertura global.
Gestão e seus contratos administrativos são exclusivos do Administrador.
Somente usuários com perfil Técnico podem ser responsáveis por chamados.
A decisão está registrada na
[spec de autorização](openspec/specs/autorizacao-perfis/spec.md).

## Propósito do produto

O MIRA é uma plataforma acadêmica de Service Desk e observabilidade para Totens
de autoatendimento de uma rede de restaurantes. Integra monitoramento técnico e
atendimento para que a operação acompanhe falhas, disponibilidade e a evolução
dos chamados.

Seu mecanismo central combina telemetria e detecção automática de ausência de
comunicação com relatos manuais das Lojas. Assim, o atendimento também contempla
problemas físicos ou operacionais que a telemetria não identifica.

O sucesso de uso está em permitir que cada perfil encontre a informação e
conclua seu trabalho: relatar e acompanhar problemas, tratar chamados, consultar
indicadores ou manter os cadastros necessários à operação.

## Contexto de uso

- Aplicação Web voltada ao uso em desktop, com jornadas autenticadas por perfil.
- A Loja é a unidade operacional da rede; todo ativo monitorado é um Totem.
- Monitoramento e Service Desk se conectam pelo Totem e pelo histórico da
  ocorrência. O retorno da comunicação não equivale à resolução do atendimento.
- A operação usa filas, filtros, detalhes, comentários e histórico; a Diretoria
  consulta recortes gerenciais de disponibilidade e chamados/SLA.
- A interface e as explicações do projeto usam português brasileiro.

## Capacidades e limites

As capacidades consolidadas abrangem autenticação, administração, monitoramento,
abertura manual e automática de chamados, atribuição, tratativa, histórico, SLA
e indicadores. Contratos, permissões, fórmulas e transições devem ser consultados
nas [specs vigentes](openspec/specs/), sem serem deduzidos de referências visuais.

O frontend existente usa Reflex. Xano/XanoScript concentra persistência,
autenticação, autorização e regras de negócio. Simulator produz telemetria para
Totens cadastrados; Fiscal dispara a verificação periódica de heartbeat. Os
limites arquiteturais e a restrição ao plano Free do Xano estão em
[openspec/config.yaml](openspec/config.yaml).

Dados ausentes ou históricos incompletos não autorizam inventar valores,
resultados ou vínculos. A interface deve distinguir o que os contratos retornam
do que está indisponível. Novas funcionalidades seguem o fluxo OpenSpec.

## Compromissos de marca e linguagem

- Preservar o nome **MIRA** e o
  [logotipo oficial](assets/mira-logo.svg).
- Usar os termos do domínio e textos claros para o trabalho de cada perfil.
- Consultar o [DESIGN.md](DESIGN.md) para identidade e apresentação, preservando
  a prioridade dos requisitos funcionais.

## Evidências disponíveis

- [Visão do projeto](docs/project-overview.md),
  [modelo de domínio](docs/domain-model.md) e [specs](openspec/specs/) descrevem
  o produto e o comportamento aprovado.
- [Aplicação](app/), [backend](xano/) e [testes](tests/) permitem investigar a
  implementação; a existência de código não comprova execução ou publicação.
- O [Simulator](simulator/) fornece telemetria simulada. Dados de demonstração
  e exemplos não devem ser apresentados como resultados reais de clientes.

## Princípios de produto

1. Equilibrar as necessidades dos quatro perfis sem ampliar seus acessos.
2. Manter a ligação entre observabilidade e atendimento compreensível, sem
   confundir estado técnico do Totem com estado do chamado.
3. Sustentar decisões operacionais em fatos persistidos e histórico comprovado.
4. Favorecer a conclusão das tarefas com clareza de contexto, ação e resultado.

## Acessibilidade e inclusão

Preservar navegação por teclado, foco visível, contraste, semântica acessível,
mensagens compreensíveis, suporte a zoom e redução de movimento conforme o
[DESIGN.md](DESIGN.md). Significados não devem depender apenas de cor, posição
ou ícone. Necessidades específicas de públicos com deficiência e um nível
formal de conformidade não foram definidos nesta inicialização.
