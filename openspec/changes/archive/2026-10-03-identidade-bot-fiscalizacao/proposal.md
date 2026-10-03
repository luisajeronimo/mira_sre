## Why

O domínio já reconhece o Bot de Fiscalização como o ator de sistema que cria
incidentes de heartbeat, mas o fluxo atual persiste somente
`origem = "automatico"` e deixa a autoria ausente. Origem funcional e autoria
são conceitos diferentes: a primeira informa como o chamado surgiu, enquanto a
segunda deve registrar quem o criou sem transformar o Bot em usuário humano ou
credencial técnica.

## What Changes

- Adicionar ao chamado uma representação persistida, opcional e exclusiva do
  criador de sistema `bot_fiscalizacao`, sem relação com `usuarios` e sem criar
  uma conta, perfil, sessão, token ou permissão para o Bot.
- Fazer o Xano preencher essa autoria somente ao criar um novo incidente pela
  regra de heartbeat; o fluxo manual permanece com solicitante humano e sem
  criador de sistema.
- Expor a autoria persistida nos contratos de detalhe de chamados para que as
  telas de detalhe de Gerente e Técnico apresentem separadamente `Criado por:
  Bot de Fiscalização` e `Origem: Automático` quando aplicável.
- Preservar registros legados sem autoria, sem backfill e sem inferir o Bot a
  partir de origem, título, categoria, ativo, telemetria ou credenciais.
- Manter inalterados timeout e decisão do heartbeat, deduplicação, Fiscal,
  Simulator, autenticação técnica, `interacoes_chamado` e qualquer auditoria
  genérica.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-abertura-manual`: separar e persistir a autoria de sistema na
  criação automática de heartbeat, mantendo solicitante humano e registros
  legados compatíveis.
- `chamados-fila-atribuicao-tecnica`: disponibilizar a autoria de sistema no
  detalhe técnico de chamado, sem ampliar a fila, a atribuição ou a tratativa.
- `frontend-chamados-gerente`: apresentar a autoria de sistema no detalhe do
  chamado, sem alterar listagem ou jornada de abertura manual.

## Impact

- **Xano:** schema de `chamados`, ponto de inserção de
  `verificar-falhas` e DTOs de detalhe do Service Desk para Gerente e Técnico.
- **Reflex:** modelos/parseamento do cliente e o detalhe existente de chamados
  para os perfis Gerente e Técnico, sem nova coluna ou lista.
- **Testes:** cenários XanoScript e Python para criação automática, criação
  manual, leitura de detalhe e compatibilidade de legados.
- **Documentação estável:** atualização mínima de `docs/domain-model.md` e
  `docs/project-overview.md` para substituir a descrição preexistente do Bot
  como solicitante de sistema pela separação aprovada entre solicitante humano
  ausente e criador de sistema persistido, sem reescrever outros conceitos de
  domínio.
- **Plano e segurança:** a proposta usa somente um campo aditivo no schema e
  contratos existentes, compatível com Xano Free; não adiciona dependências,
  segredos, APIs da OpenAI, credenciais técnicas ou autenticação humana.

## Fora de escopo

- Usuário, login, senha, sessão, token, perfil ou permissões do Bot.
- Auditoria genérica, eventos de sistema, histórico automático ou alterações em
  `interacoes_chamado`.
- Outros Bots, outras automações, comentários, atribuições, status ou
  encerramentos automáticos.
- Timeout, disponibilidade, telemetria, deduplicação e fluxo do Fiscal.
- Autenticação do Fiscal/Simulator, chaves de automação, Environment Variables
  ou secrets.
- Backfill, limpeza ou inferência de autoria para registros históricos.
