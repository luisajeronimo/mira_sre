# Design

## Context

Ver `proposal.md` para a motivação e as delta specs para o comportamento
observável. O detalhe funcional do Gerente já consulta chamado, Totem, Categoria,
solicitante e Técnico por escopo de Loja, mas a interface não apresenta todos os
dados retornados. A tabela `interacoes_chamado` contém somente mensagem, relações
e datas opcionais; o GET genérico atual não é DTO público e a mutação genérica é
negada.

`chamados` possui `criado_em`, `created_at` técnico e `atribuido_em`, mas não
possui uma data semântica da última alteração. As únicas mutações funcionais
atuais de chamados são as criações manual e automática e a assunção técnica;
não existe rota funcional de mudança de status nesta base.

## Goals / Non-Goals

**Goals:**

- Persistir e expor com segurança a última alteração observável pelo Gerente.
- Reutilizar `interacoes_chamado` para comentários públicos, sem inferir a
  classificação de registros existentes.
- Criar fronteira funcional pequena para leitura e criação de comentários por
  chamado, com autorização central e escopo de Loja no Xano.
- Completar o detalhe do Gerente com os dados já contratados e os comentários
  públicos recém-contratados.

**Non-Goals:**

- Não criar operação de mudança de status, resolução, rejeição, reatribuição,
  liberação ou tratativa técnica.
- Não classificar, migrar ou expor interações legadas sem visibilidade.
- Não acrescentar paginação, filtros, ordenação ou contadores da lista.
- Não criar comentários privados para o Gerente, edição, exclusão, anexos,
  reações, menções ou histórico técnico completo.

## Decisions

### 1. Timestamps funcionais são aditivos e não reinterpretam metadados técnicos

`chamados` receberá `ultima_atualizacao_em` como timestamp opcional. Chamados
legados permanecerão nulos. Todo produtor novo ou mutação observável já
existente capturará um instante do backend e o aplicará conforme o contrato:

- criação manual: `criado_em` e `ultima_atualizacao_em` recebem o mesmo valor;
- criação automática de heartbeat: os dois campos recebem o mesmo valor na
  transação existente;
- assunção efetiva: `atribuido_em` e `ultima_atualizacao_em` recebem o mesmo
  instante da alteração;
- comentário público: criação e atualização do chamado usam o mesmo instante
  na mesma unidade de escrita.

`created_at` continua técnico e privado. Não haverá backfill de
`ultima_atualizacao_em` e leitura não altera o campo.

Não há hoje fluxo funcional de mudança de status para adaptar. A regra ficará
registrada como invariante: a futura change que introduzir qualquer alteração de
status deverá atualizar `ultima_atualizacao_em` atomicamente com ela. Esta
change não reabre PATCH genérico nem cria endpoint de status.

**Alternativas consideradas:**

- Derivar a última atualização de `created_at`, `atribuido_em` ou interações:
  rejeitada por não cobrir todos os eventos e falsificar legados.
- Calcular dinamicamente em cada leitura: rejeitada porque é incompleta, torna
  a ordenação futura instável e mistura fatos internos com públicos.

### 2. Visibilidade de interação é enum opcional sem default público

`interacoes_chamado` receberá `visibilidade` opcional com valores `publica` e
`interna`. O schema não terá default que transforme registros antigos em
públicos. O escritor específico desta change sempre persistirá `publica`; valor
nulo, `interna` ou qualquer valor não canônico não será retornado ao Gerente.

O modelo físico existente continua sendo reutilizado: `chamados_id` identifica
o chamado, `usuarios_id` recebe exclusivamente `$auth.id` e `criado_em` recebe
o instante do backend. `mensagem` é convertido para um campo público de
conteúdo no DTO, sem retornar o registro bruto ou seus campos internos.

**Alternativas consideradas:**

- Usar o GET genérico existente: rejeitada, pois ele não aplica DTO de
  visibilidade nem contrato por chamado.
- Considerar registros sem visibilidade como públicos: rejeitada por risco de
  expor nota interna ou conteúdo histórico sem classificação.
- Criar tabela exclusiva de comentários: rejeitada; a tabela existente contém
  relações necessárias e basta evoluí-la de modo explícito e seguro.

### 3. Comentários usam endpoints funcionais por chamado

O grupo `MIRA Service Desk` receberá endpoints equivalentes a:

- `GET /gerente/chamados/{chamados_id}/comentarios`;
- `POST /gerente/chamados/{chamados_id}/comentarios`.

Cada endpoint autentica `usuarios`, reutiliza `autorizacao/exigir_perfil` com
Gerente e localiza primeiro o chamado. A autorização decorre de chamado →
Ativo/Totem → Loja, jamais de Loja enviada pelo cliente. A leitura devolve
somente comentários `publica`, ordenados por `criado_em DESC`, com DTO fechado:
`id`, `conteudo`, `criado_em` e `autor` (`null` ou objeto contendo somente
`nome`). A projeção não expõe ID de usuário, e-mail, perfil, Loja, credencial ou
outro atributo interno; se a relação de autor não puder ser projetada com
segurança, `autor` é `null`.

O POST aceita somente conteúdo, remove espaços nas extremidades e rejeita
vazio. Ele bloqueia `Encerrado` e `Cancelado`, define autor, visibilidade e data
no Xano e executa inserção da interação e patch de
`ultima_atualizacao_em` conjuntamente. Comentários públicos permanecem legíveis
em chamados terminais.

**Alternativas consideradas:**

- Receber `usuarios_id`, visibilidade ou timestamp do Reflex: rejeitada por
  permitir falsificação de autoria ou de confidencialidade.
- Aplicar somente bloqueio visual aos terminais: rejeitada; o backend é a
  autoridade e o contrato deve resistir a chamada direta.

### 4. Detalhe compõe dados de chamado e comentários sem criar tratamento

`GET /gerente/chamados/{chamados_id}` permanece responsável pelo DTO de
chamado e passa a projetar `ultima_atualizacao_em` sem inferência. A página
apresenta esse valor ou `Não informado` quando ele for `null`. A página chama a consulta específica de comentários separadamente,
pois o ciclo de erro e atualização de comentário é independente do detalhe e o
contrato evita transformar o detalhe em agregador de interações. O Reflex
renderiza os dados já retornados de Totem, Categoria, solicitante, Técnico, SLA,
origem, abertura e autoria de sistema; para Técnico nulo usa o estado
apresentável já consolidado.

O rascunho de comentário reside apenas no State do Reflex. Descartá-lo limpa o
valor local e não faz request. Depois de criação aceita, o State usa o DTO do
servidor e recarrega ou atualiza somente a coleção de comentários públicos.

### 5. Compatibilidade com Xano Free e publicação segura

A solução usa campos aditivos, enum, consultas, joins, preconditions e
transações já empregados no workspace. Não requer recurso pago, worker,
agendamento, segredo novo ou API externa. Antes do Apply, os XanoScripts devem
ser validados por parser/MCP e o dry-run deve limitar-se a schema, funções e
endpoints desta capability, além dos ajustes estritamente necessários nos
produtores já aprovados.

## Risks / Trade-offs

- **[Vazamento de conteúdo interno]** → filtro de leitura exige
  `visibilidade = publica`; nulo falha fechado e o DTO não reutiliza a resposta
  genérica.
- **[Atualização parcial entre comentário e timestamp]** → criação do comentário
  público e patch do chamado ocorrem na mesma unidade transacional; falha não
  mantém uma escrita isolada.
- **[Assunção idempotente altera data indevidamente]** → atualizar a data apenas
  quando a atribuição é efetivada, preservando a repetição sem mudança.
- **[Fluxo futuro de status esquecer o timestamp]** → delta registra a invariante
  e a futura capability de status deverá integrá-la antes de publicar mutação.
- **[Legado passa a parecer público ou atualizado]** → campos novos opcionais,
  sem default público e sem backfill.

## Migration Plan

1. Inventariar os produtores e mutações atuais de chamado e confirmar que não
   existe rota funcional de mudança de status.
2. Adicionar os campos opcionais `ultima_atualizacao_em` e `visibilidade`, sem
   alterar registros existentes.
3. Adaptar criação manual, criação automática e assunção para os novos valores
   definidos pelo backend; verificar idempotência da assunção.
4. Criar e validar as funções e endpoints específicos de comentário, incluindo
   escopo de Loja, terminais e transação de escrita.
5. Adaptar DTOs, cliente, State e detalhe Reflex, inclusive a apresentação de
   `ultima_atualizacao_em` nula e do autor público estrito; adicionar testes de
   contrato, segurança e regressão.
6. Executar parser/MCP, suíte local, Reflex, OpenSpec strict e dry-run Xano
   antes de qualquer push autorizado.

Em rollback, desabilitar primeiro os endpoints e a UI novos, mantendo os campos
aditivos e interações já criadas para não apagar fatos. Remoção de campos,
classificação retroativa ou exclusão de dados requer decisão destrutiva separada.
