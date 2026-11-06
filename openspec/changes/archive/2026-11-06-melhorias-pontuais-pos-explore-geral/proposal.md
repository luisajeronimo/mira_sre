# Proposal

## Why

O Explore geral confirmou um caminho de leitura de interações que expõe registros brutos ao Gerente, estado local do Gerente que sobrevive à troca de sessão e pequenas divergências entre código, testes e contratos já aprovados. Esta change reúne os dez achados para revisão coordenada, com resolução independente e mínima por item; conflitos de regra e suspeitas sem evidência permanecem pendentes.

## What Changes

- **BREAKING para Gerente que chame CRUD genérico diretamente:** retirar apenas o Gerente dos dois GETs genéricos de `interacoes_chamado`, preservando o Técnico e a negação atual de Diretoria/Administrador observada nos XanoScripts locais. A matriz foi confirmada pelo usuário em 06/11/2026. A jornada do Gerente continua no contrato funcional de comentários públicos. Nenhum consumidor desses GETs foi encontrado em `app/`, `simulator/` ou `fiscal/`, mas isso não exclui integração externa; verificar integrações declaradas antes da edição.
- Isolar dados, rascunhos, catálogos e preferências do `ChamadosGerenteState` por identidade e sessão; limpar o contexto do Gerente na saída e antes de usar dados após nova autenticação, sem refatorar a autenticação geral.
- Reconciliar as fontes antigas com as decisões das specs mais recentes para `ultima_atualizacao_em` de comentário interno, comentários em chamados terminais, comentário do Gerente em terminal e uso operacional de `Solução Rejeitada`. O usuário definiu esse critério em 06/11/2026; o comportamento implementado nesses quatro pontos já o segue, portanto esta trilha altera somente documentação e deltas de spec.
- Corrigir apenas a expectativa desatualizada do teste de filtros múltiplos, mantendo arrays codificados como JSON no GET. Verificar a decodificação e rejeição de valor que não seja array nos testes focados.
- Ajustar o agendamento local do Simulator para que os inícios de ciclos tenham intervalo de cinco minutos pelo relógio monotônico, sem sobrepor ciclos nem mudar o envio sequencial dos Totens.
- Exigir `XANO_BASE_URL` explícita no Fiscal, com erro claro antes de request, removendo somente o fallback remoto embutido.
- Acrescentar rótulos persistentes aos campos administrativos identificados. A tentativa de mostrar o título da rota na topbar foi rejeitada pelo usuário após conferência visual; removê-lo para todos os perfis, mantendo contexto na navegação e no conteúdo, sem alterar identidade ou saída.
- Executar a matriz HTTP negativa mínima com sessões autorizadas. A execução revelou três entradas inválidas com 400 apesar do 422 consolidado; a correção pontual nos dois GETs funcionais foi autorizada e comprovada com 422 nos três casos, mantendo 200 nas listas válidas. A autorização de perfil e Loja também foi comprovada. Não criar infraestrutura de login de teste.
- Corrigir a divergência HTTP 200/401 confirmada nos guards técnicos já especificados de Fiscal e Simulator, sem alterar chave, payload, regra operacional ou resposta válida. Esta extensão pontual do item 8 foi autorizada pelo usuário após a validação dos demais achados.
- Investigar latência e número de consultas dos pontos suspeitos de monitoramento e fila técnica antes de autorizar otimização. Nenhuma consulta muda nesta change sem nova evidência e revisão.
- Registrar dashboards, administração de Lojas/Totens e demais capacidades futuras como backlog, separados dos defeitos atuais, sem implementar ou especificar comportamento novo.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `autorizacao-perfis`: os dois GETs genéricos de interações passam a rejeitar Gerente, mantendo Técnico; Diretoria/Administrador continuam negados, conforme matriz confirmada pelo usuário.
- `frontend-chamados-gerente`: estado local protegido e preferências não atravessam logout, troca de usuário ou nova sessão.
- `chamados-acompanhamento-gerente`: comentário interno operacional atualiza a data funcional, conforme a spec posterior de tratativa, sem tornar seu conteúdo visível ao Gerente.
- `autenticacao-automacoes`: Fiscal exige URL operacional explicitamente configurada antes da chamada.
- `administracao-usuarios`: formulário administrativo apresenta rótulos persistentes nos campos existentes.
- `navegacao-lateral-perfis`: a topbar compartilhada deixa de repetir o título da rota, conforme decisão visual explícita do usuário; sidebar, conteúdo, identidade e saída permanecem.

As regras já consolidadas de periodicidade do Simulator e transporte JSON dos filtros não precisam de delta: a implementação ou o teste deve convergir para elas. A decisão humana de retirar o título da topbar exige o delta de `navegacao-lateral-perfis`. A decisão de 06/11/2026 sobre os quatro conflitos de negócio é registrada nos deltas das duas specs anteriores que ainda divergiam e no modelo de domínio; não autoriza nova funcionalidade ou alteração de código desses fluxos.

## Impact

- Apply localizado nos dois GETs XanoScript genéricos, nos dois GETs funcionais `gerente/chamados` e `tecnico/chamados`, nos guards de `verificar-falhas` e `telemetria_equipamentos`, `ChamadosGerenteState` e integração pontual da saída, teste dos filtros, `simulator/simulator.py`, `fiscal/fiscal.py`, formulário administrativo e topbar. Não há alteração de schema, entidade, segredo, regra de heartbeat ou formato da listagem bem-sucedida.
- Validação de autorização e respostas HTTP publicadas depende de sessões já autorizadas para os perfis e escopos necessários. Nenhum acesso remoto ou publicação faz parte desta proposta.
- A escolha humana pelos trechos mais recentes das specs está registrada em `design.md` com a origem de cada regra. Não há mudança funcional adicional de negócio a publicar nesta trilha; aceite/rejeição pelo solicitante e fechamento automático seguem como backlog.
