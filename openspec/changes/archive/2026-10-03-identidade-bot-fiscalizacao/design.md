## Context

Ver `proposal.md` para a motivação e as delta specs para o comportamento
observável. Hoje `chamados.origem` já é um enum opcional (`manual` ou
`automatico`) e `solicitante_id` é uma relação opcional com a tabela
autenticável `usuarios`. O endpoint `verificar-falhas` decide o incidente no
Xano e insere o chamado automático sem solicitante. Os detalhes de Gerente e
Técnico carregam solicitante por *left join* e já toleram sua ausência.

O modelo de domínio exige que o Bot de Fiscalização seja ator de sistema, não
um usuário humano. As chaves de automação autenticam processos técnicos e não
são dados de domínio. A solução deve, portanto, acrescentar autoria sem mudar a
autoridade do Xano, o contrato de segurança do Fiscal ou a regra de heartbeat.

Há uma deriva documental a reconciliar durante Apply: `docs/domain-model.md` e
`docs/project-overview.md` ainda chamam o Bot de solicitante de sistema. A
decisão humana desta change estabelece que `solicitante_id` representa somente
um usuário humano ou permanece ausente; a autoria do Bot deve ser expressa por
`criador_sistema`. A reconciliação será textual, limitada aos trechos que
descrevem essa relação e posterior à implementação aprovada, sem usar a
documentação preexistente como autorização para uma FK, usuário fictício ou
backfill.

## Goals / Non-Goals

**Goals:**

- Persistir uma autoria explícita e limitada à criação automática de heartbeat.
- Preservar `origem` como classificação funcional e `solicitante_id` como
  referência humana independente.
- Permitir aos detalhes de Gerente e Técnico apresentar a autoria sem criar
  coluna nas listas.
- Manter legados sem autoria e sem inferência retrospectiva.

**Non-Goals:**

- Generalizar atores, trilha de auditoria, eventos ou `interacoes_chamado`.
- Modelar outros Bots, ações posteriores no ciclo de vida ou outras automações.
- Alterar Fiscal, Simulator, chaves, guards, autenticação humana, autorização,
  timeout, telemetria, disponibilidade ou deduplicação.
- Criar, migrar ou associar contas em `usuarios` e executar backfill.

## Decisions

### Campo aditivo e canônico no chamado

A modelagem física será um campo opcional `criador_sistema` em `chamados`, com
enum de valor único `bot_fiscalizacao`. Ele não terá relação com outra tabela e
não será aceito de consumidores como entrada sob autoridade. Essa escolha é a
menor persistência que torna a autoria consultável, diferencia-a de `origem` e
não altera a semântica de `solicitante_id`.

O campo é opcional para compatibilidade: ausência representa autoria
desconhecida ou não aplicável, inclusive em todos os registros legados. No
escopo desta change, o único produtor é a inserção de incidente pelo heartbeat;
o único valor criado é `bot_fiscalizacao`.

Alternativas consideradas:

- **Derivar o Bot de `origem = automatico`: rejeitada.** Não persiste autoria,
  confunde classificação do fluxo com ator e falsificaria históricos automáticos
  sem autor registrado.
- **Inserir Bot em `usuarios`: rejeitada.** Essa tabela é autenticável e reúne
  perfil, e-mail, senha e permissões humanas; uma FK conveniente criaria uma
  identidade humana indevida.
- **Tabela de atores ou enum de atores genérico: rejeitada.** Acrescenta
  abstração para automações, eventos e relações ainda não aprovados.
- **Registrar em `interacoes_chamado`: rejeitada.** Não representa o criador do
  próprio chamado e ampliaria a change para auditoria/histórico.

### Escrita exclusivamente no ponto decisório do Xano

No trecho de `verificar-falhas` que já insere um incidente novo após decidir a
ausência de heartbeat e não encontrar equivalente, o Xano escreverá
`criador_sistema: "bot_fiscalizacao"` junto com os campos já existentes. O
Fiscal continuará somente disparando `GET /verificar-falhas`; sua chave de
automação continuará sendo validada apenas como credencial técnica e nunca será
persistida como autoria.

Nenhuma condição, consulta, status ou critério da deduplicação será modificado.
Em especial, se houver incidente equivalente, não haverá escrita em chamado
existente para completar `criador_sistema`.

### Contratos de detalhe e apresentação mínima

Os DTOs de detalhe de Gerente e Técnico passarão a expor
`criador_sistema: "bot_fiscalizacao" | null` separadamente de `origem` e
`solicitante`. A consulta pode ler o campo diretamente de `chamados`; não há
join de usuário para essa autoria. O cliente Reflex aceitará o campo opcional
no seu modelo de detalhe e converterá somente o valor canônico conhecido para o
rótulo estável `Bot de Fiscalização`.

As duas páginas de detalhe existentes renderizarão `Criado por: Bot de
Fiscalização` apenas com esse valor persistido, mantendo `Origem: Automático`
em linha própria. Para `null`, elas não inventarão uma autoria nem introduzirão
um texto substituto como se fosse dado histórico. As listagens, seus DTOs e
colunas não recebem o novo campo porque a necessidade de apresentação aprovada
é somente o detalhe.

O retorno de abertura manual pode continuar compatível com o cliente por
`criador_sistema` opcional nulo; durante Apply, os contratos compartilhados e
seus parsers serão verificados para que nenhuma resposta seja tratada como
autoria humana. Esse ajuste de compatibilidade não cria comportamento novo na
jornada manual.

### Compatibilidade, segurança e Xano Free

A mudança é aditiva: não remove, renomeia nem torna obrigatório um campo já
existente. Nenhum backfill será executado, e a ausência em legados será
retornada como `null`. O campo usa o mesmo recurso de enum opcional já presente
no schema local de `chamados`, além de consulta/DTOs existentes; não requer
recurso pago, worker, agendamento, secret ou API externa. Durante Apply, a
sintaxe do XanoScript e a disponibilidade efetiva no workspace alvo serão
validadas com o Xano Developer MCP antes de qualquer push, conforme
`openspec/config.yaml`.

### Reconciliação documental mínima

Depois de demonstrar o comportamento implementado, os trechos estáveis que
descrevem chamados automáticos serão atualizados para registrar: solicitante
humano ausente no heartbeat, Bot de Fiscalização como criador de sistema não
autenticável e separação entre origem e autoria. A atualização se limita a
`docs/domain-model.md` e `docs/project-overview.md`; não reestrutura a
documentação, não altera regras de heartbeat nem amplia o modelo para auditoria
genérica.

## Risks / Trade-offs

- **Risco: usar `origem` como se fosse autoria.** → Os contratos e a UI usam
  `criador_sistema` como única evidência para mostrar o Bot; `origem` permanece
  uma informação independente.
- **Risco: converter o Bot em usuário por conveniência de relacionamento.** →
  Não haverá FK para `usuarios`, criação de credencial ou modificação de perfis.
- **Risco: falsificar o passado.** → Campo opcional, sem backfill e sem escrita
  sobre incidente equivalente ou legado.
- **Risco: ampliar escopo para auditoria futura.** → Enum de valor único no
  próprio chamado e nenhum ajuste em interações, status ou atribuições.
- **Risco: o parser Reflex supor objeto de usuário.** → O novo campo é escalar
  opcional, separado de `solicitante`, e terá testes de parse de nulo e valor
  canônico.
- **Trade-off: a autoria fica limitada à criação de heartbeat.** → É deliberado;
  uma necessidade de atores em outros eventos exigirá change independente.
- **Risco: documentação estável preservar a semântica anterior de
  solicitante.** → Atualizar somente os trechos identificados e revisar o diff
  para confirmar que a documentação passa a refletir `solicitante_id` humano ou
  nulo e `criador_sistema` do Bot, sem mudanças de domínio adjacentes.

## Migration Plan

1. Confirmar no Xano Developer MCP o schema/endpoint alvo e validar o campo
   aditivo `criador_sistema` sem tocar registros existentes.
2. Aplicar o schema e adaptar somente a inserção de novo incidente de
   `verificar-falhas`.
3. Adaptar os DTOs de detalhe, cliente tipado e as duas páginas de detalhe.
4. Executar testes de criação manual, criação automática, detalhe e legado;
   validar XanoScript, diff e OpenSpec strict antes de qualquer push.
5. Antes de push remoto, executar `xano workspace push --dry-run`, revisar o
   diff completo e preservar recursos remotos fora do escopo.

Rollback deve desativar primeiro a exposição do campo nos contratos/UI e
restaurar apenas a escrita do endpoint se necessário. O campo aditivo e os
valores já criados permanecem para não apagar evidência; qualquer remoção física
ou alteração de registros exigirá decisão destrutiva separada.
