# MIRA

## 1. Apresentação

O **MIRA** é uma plataforma acadêmica de **Service Desk e observabilidade** para totens de autoatendimento de uma rede de fast-food. Reúne monitoramento técnico, registro de falhas, atendimento e indicadores em um único sistema.

O problema tratado é a dificuldade de acompanhar a disponibilidade dos equipamentos e organizar a resposta aos incidentes. O monitoramento detecta falta de comunicação, enquanto a abertura manual permite registrar problemas físicos ou operacionais que a telemetria não identifica.

O público-alvo é formado por **Gerentes de loja, Técnicos de atendimento, Diretoria e Administradores do Sistema**.

## 2. Acesso ao aplicativo

**Versão publicada:** [https://mira-16-59-1-160.sslip.io](https://mira-16-59-1-160.sslip.io)

O acesso exige uma conta cadastrada pelo Administrador do Sistema. Utilize o e-mail e a senha recebidos do responsável pelo ambiente; credenciais não são publicadas neste repositório. Não há cadastro público pela tela de login.

Novas contas usam senha temporária e devem definir uma nova senha no primeiro acesso. As opções de navegação são apresentadas conforme o perfil. A interface foi concebida para uso em computador.

## 3. Perfis de usuários

| Perfil | Responsabilidades e permissões |
| --- | --- |
| **Gerente** | Abre e acompanha chamados da própria loja, consulta seus detalhes e SLA, publica comentários e pode rejeitar uma solução. Não acessa a fila global, o monitoramento global, os indicadores executivos nem os cadastros administrativos. |
| **Técnico** | Atua na fila global, abre chamados, atribui ou reatribui responsáveis, altera status, prioridade e categoria, registra comentários públicos ou internos e consulta monitoramento e indicadores. Pode ser responsável pelo atendimento. |
| **Diretoria** | Possui os mesmos acessos operacionais do Técnico, incluindo abertura e tratativa de chamados, monitoramento e indicadores globais. Pode gerir atribuições, mas somente Técnicos podem ser responsáveis pelos chamados. |
| **Administrador do Sistema** | Possui os acessos operacionais globais e a área exclusiva de Administração para manter usuários, lojas e totens. Também não pode ser responsável técnico por um chamado enquanto seu perfil for Administrador. |

As permissões são validadas pelo Xano. O escopo do Gerente considera a loja do chamado no momento da ocorrência, preservando o histórico mesmo quando o totem é transferido depois.

## 4. Funcionalidades

- **Acesso:** autenticação, troca obrigatória da senha temporária e navegação por perfil.
- **Chamados:** abertura manual por totem e categoria, prioridade, fila com busca e filtros combináveis, atribuição e tratativa.
- **Comunicação:** comentários públicos, comentários internos para os perfis operacionais e histórico das alterações.
- **SLA:** prazo por categoria e consulta do consumo e da situação do chamado.
- **Monitoramento:** estado dos totens, última telemetria, histórico recente e incidentes automáticos por ausência de heartbeat.
- **Indicadores:** disponibilidade, MTTD, MTTR, volume por status, conformidade e risco de SLA, Top 5 Lojas, Pareto por categoria e recorrência.
- **Administração:** criação, consulta, edição e exclusão permitida de usuários, lojas e totens, incluindo transferência de totem.
- **Automações:** geração de telemetria simulada, verificação de heartbeat e verificação de encerramento dos chamados elegíveis.

## 5. Manual de utilização

A sequência habitual é **entrar → registrar ou localizar um chamado → atribuir e atender → registrar a solução → acompanhar o resultado**. Monitoramento e indicadores ajudam a investigar falhas e acompanhar a operação; a Administração mantém os cadastros necessários a essas jornadas.

### 5.1. Entrar e concluir o primeiro acesso — todos os perfis

1. Abra a versão publicada e preencha **E-mail institucional** e **Senha de acesso**.
2. Clique em **Entrar**. Se houver erro, confira as credenciais e a mensagem apresentada.
3. Se a conta exigir troca da senha temporária, preencha **Nova senha** e **Confirme a nova senha**, com pelo menos oito caracteres, e clique em **Salvar nova senha**.
4. Aguarde a abertura de **Início**: o Gerente encontra os chamados da loja; os demais perfis encontram a fila global.
5. Ao terminar, clique em **Sair**. Se a sessão expirar, faça login novamente.

**Resultado esperado:** sessão autenticada e acesso somente às funcionalidades autorizadas para o perfil. A troca obrigatória precisa ser concluída antes de usar as funcionalidades normais.

### 5.2. Abrir um chamado — Gerente

1. Em **Início**, clique em **Criar chamado**.
2. Selecione o **Totem** da loja e uma **Categoria** disponível para abertura manual.
3. Defina a **Prioridade** e preencha **Título** e **Descrição**, explicando sintomas, contexto e o equipamento afetado. Os cinco campos são obrigatórios.
4. Revise as informações e clique em **Confirmar e abrir chamado**.
5. Após a confirmação, consulte o detalhe e anote o número do chamado para acompanhá-lo.

**Resultado esperado:** chamado criado em `Novo`, com a prioridade escolhida, o solicitante autenticado, a loja do totem e o SLA da categoria. Para problemas em vários totens, registre um chamado para cada equipamento.

Técnico, Diretoria e Administrador também usam **Criar chamado**, com catálogo global de totens. A loja é determinada pelo totem selecionado.

### 5.3. Acompanhar, comentar e rejeitar uma solução — Gerente

1. Em **Início**, localize o chamado pelo número ou combine os filtros disponíveis e clique em **Aplicar**. Use **Limpar filtros** para remover a seleção.
2. Abra o chamado pelo número e consulte status, prioridade, descrição e dados do totem. A informação ao lado de **SLA aplicado** permite consultar o consumo quando calculável.
3. Na seção **Comentários**, escreva uma atualização e clique em **Postar comentário**. Os comentários do Gerente são públicos.
4. Se o chamado estiver `Resolvido` e o problema persistir, preencha a justificativa na seção **Rejeitar solução** e clique em **Rejeitar solução**.

**Resultado esperado:** o comentário fica registrado no chamado. A rejeição válida muda o status para `Solução Rejeitada`, registra a justificativa pública e retoma a contagem do SLA a partir do saldo anterior à resolução.

O Gerente pode comentar em chamados da loja mesmo quando estão encerrados ou cancelados. Um comentário, por si só, não altera o status nem reabre o chamado.

### 5.4. Atribuir, atender e resolver — Técnico, Diretoria e Administrador

1. Em **Início**, localize o chamado pela busca ou pelos filtros. Os atalhos **Todos**, **Atribuídos a mim** e **Não atribuídos** ajudam a organizar a fila.
2. Abra o detalhe e, em **Responsável**, selecione um Técnico. Para assumir o atendimento como Técnico, selecione o próprio nome; para liberar a atribuição, selecione **Não atribuído**.
3. Clique em **Salvar** para confirmar a atribuição. Escolher um responsável não muda o status automaticamente.
4. Ao iniciar o trabalho, selecione `Em Atendimento` em **Status**, registre um **Comentário**, escolha a **Visibilidade** permitida e clique em **Salvar**.
5. Durante a tratativa, atualize prioridade, categoria ou responsável quando necessário. As mudanças ficam pendentes até **Salvar**; **Descartar mudanças** restaura os dados confirmados.
6. Após aplicar a solução, selecione `Resolvido`, descreva a solução em um comentário **Público** e clique em **Salvar**.
7. Confira os dados retornados e a **Linha do tempo** para confirmar o registro das alterações.

**Resultado esperado:** o chamado passa a refletir as mudanças confirmadas, com registro das alterações e dos comentários. Comentários **Internos** ficam restritos aos perfis operacionais.

Toda mudança de status exige comentário. Os destinos `Resolvido`, `Aguardando Solicitante` e `Cancelado` exigem comentário público. Chamados `Encerrado` ou `Cancelado` bloqueiam novas alterações funcionais, mantendo os comentários autorizados. Se outra pessoa atualizar o chamado antes do seu salvamento, confira os dados recarregados antes de tentar novamente.

### 5.5. Investigar um totem — Técnico, Diretoria e Administrador

1. Na navegação lateral, abra **Monitoramento**.
2. Consulte o resumo dos estados e selecione o totem desejado.
3. Verifique **Última telemetria**, CPU, memória, temperatura, rede e os horários apresentados.
4. Consulte os históricos de telemetria, eventos de disponibilidade e incidentes automáticos de heartbeat.
5. Quando houver um incidente relacionado, abra seu link para consultar ou continuar a tratativa do chamado.

**Resultado esperado:** identificação do último estado persistido e dos fatos disponíveis para investigação. A página não força a atualização do equipamento nem muda seu estado; o Xano decide as transições a partir da telemetria e das verificações de heartbeat.

### 5.6. Consultar indicadores — Diretoria, Técnico e Administrador

1. Abra **Indicadores** na navegação lateral.
2. Escolha a aba **Disponibilidade**, **Chamados e SLA** ou **Causas e recorrência**.
3. Selecione **Hoje**, **Últimos 30 dias** ou **Personalizado**. Para datas personalizadas, informe o intervalo e clique em **Aplicar período**.
4. Quando necessário, selecione loja histórica, totem ou categoria nos filtros da aba e clique em **Aplicar filtros**.
5. Consulte os cartões, gráficos e tabelas. Observe também avisos de ausência de dados ou de resultado não calculável.

**Resultado esperado:** indicadores referentes ao recorte escolhido. MTTD representa o tempo médio de detecção; MTTR representa o tempo médio de recuperação do totem. Em **Chamados e SLA**, o termômetro de risco mostra o retrato atual dos chamados em contagem, inclusive os abertos antes do período selecionado.

### 5.7. Manter os cadastros — Administrador do Sistema

1. Abra **Administração**. A tela **Gestão do sistema** reúne **Usuários & Acessos**, **Lojas & Unidades** e **Ativos & Totens**.
2. Para preparar uma nova loja, clique em **Criar Loja**, preencha nome, endereço e região e clique em **Salvar Loja**. A nova loja é criada como `Ativa`.
3. Clique em **Criar Totem**, informe identificação e nome, selecione uma loja ativa e clique em **Salvar Totem**. O estado operacional permanece não informado até a primeira telemetria válida.
4. Clique em **Criar Usuário**, informe nome, e-mail, perfil, senha temporária e confirmação. Para um Gerente, selecione também uma loja ativa. Clique em **Salvar Usuário** e entregue as credenciais ao usuário por canal seguro.
5. Para consultar ou manter um cadastro existente, clique em **Ver listagem** no módulo correspondente, use a busca e escolha **Editar**. Altere os campos necessários e salve. A transferência de totem ocorre pela seleção de outra loja ativa no formulário de edição.
6. Para excluir um cadastro sem dependências, use **Excluir**, confira o registro indicado e clique em **Confirmar exclusão**. A operação é definitiva; vínculos e histórico podem impedir a exclusão.

**Resultado esperado:** confirmação da operação e atualização dos registros apresentados. A transferência de um totem preserva os fatos anteriores na loja da ocorrência. O sistema protege a própria conta, o último Administrador e os registros com vínculos impeditivos.

### 5.8. Entender o andamento e o encerramento

| Status | Significado na jornada |
| --- | --- |
| `Novo` | Chamado registrado, ainda sem início explícito do atendimento. |
| `Em Atendimento` | Trabalho iniciado por alteração explícita de um perfil operacional. |
| `Aguardando Solicitante` | Aguarda informação ou ação do solicitante; um comentário posterior não muda o status automaticamente. |
| `Aguardando Mudança` | Aguarda uma mudança; a saída depende de nova alteração operacional. |
| `Resolvido` | Solução aplicada; o consumo de SLA fica pausado. |
| `Solução Rejeitada` | A solução precisa de nova tratativa; o consumo de SLA é retomado. |
| `Encerrado` | Chamado finalizado, sem reabertura ou edição funcional. |
| `Cancelado` | Chamado cancelado, sem reabertura ou edição funcional. |

Os estados de espera continuam consumindo SLA. A verificação agendada de encerramento ocorre diariamente às **03h, horário de Brasília**, e o Xano encerra apenas chamados elegíveis com pelo menos **72 horas corridas em `Resolvido`**, sem rejeição posterior e dentro da vigência da regra. Completar 72 horas não provoca mudança imediata: é necessária uma execução da verificação. Se o problema reaparecer após `Encerrado` ou `Cancelado`, abra outro chamado.

## 6. Exemplos de utilização

Os cenários abaixo são ilustrativos; os nomes não representam cadastros garantidos no ambiente. Use totens e categorias disponíveis para a conta de demonstração.

### Problema físico percebido pela loja

O totem continua `Online`, mas a impressora não emite comprovantes. O Gerente seleciona o equipamento e uma categoria manual correspondente, informa prioridade `Alta`, usa o título **“Impressora não emite comprovante”** e descreve os sintomas. Após a abertura, o Técnico se atribui como responsável, inicia o atendimento e registra a solução em comentário público ao marcar `Resolvido`.

**Resultado esperado:** o problema é atendido mesmo sem uma falha de heartbeat. Se a impressão continuar falhando enquanto o chamado estiver `Resolvido`, o Gerente pode rejeitar a solução com justificativa.

### Perda de comunicação simulada

O responsável pelo ambiente configura um totem já monitorado para deixar de enviar telemetria. Após mais de 15 minutos sem comunicação e uma verificação do Fiscal, o Xano pode registrar a transição de `Online` para `Offline` e criar um incidente `Novo/Urgente`, desde que não exista chamado equivalente não terminal.

**Resultado esperado:** os perfis operacionais conseguem investigar o evento em **Monitoramento** e tratar o incidente pela fila. Retomar a telemetria pode devolver o totem a `Online`, mas não resolve nem encerra o chamado.

### Análise de incidentes recorrentes

A Diretoria abre **Indicadores → Causas e recorrência**, seleciona **Últimos 30 dias**, escolhe uma loja histórica e aplica os filtros. Consulta o ranking de lojas, a concentração por categoria e os incidentes recorrentes. A análise considera Incidentes não cancelados e a repetição para o mesmo totem e categoria em uma janela de 30 dias corridos.

**Resultado esperado:** identificação das lojas e categorias que concentram incidentes no recorte, com indicação explícita quando não houver dados suficientes.

## 7. Limitações conhecidas

### Funcionais e operacionais

- **Telemetria simulada:** a versão entregue usa scripts Python para gerar dados; não representa uma integração instalada em totens físicos.
- **Monitoramento periódico:** os ciclos padrão são de cinco minutos. A detecção de ausência de heartbeat depende de mais de 15 minutos sem telemetria e de uma verificação do Fiscal, portanto não é instantânea.
- **Histórico incompleto:** fatos legados sem vínculo histórico confiável podem não ser acessíveis ao Gerente; SLA e indicadores podem ficar não calculáveis. O sistema não substitui dados ausentes por estimativas.
- **Dependências externas:** consultas e gravações dependem da conectividade com o backend Reflex e o Xano. Uma falha de consulta é apresentada como erro, sem confirmar uma operação que não foi concluída.

### Plano Free do Xano

O projeto utiliza o **plano Free** e deve permanecer compatível com seus recursos. Os limites de referência abaixo constam na [página oficial de planos do Xano](https://www.xano.com/pricing/); a disponibilidade deve ser conferida antes da adoção de novos recursos.

| Restrição | Impacto no projeto |
| --- | --- |
| Até 10 requisições de API a cada 20 segundos | O Simulator espaça os envios para reduzir picos; esse espaçamento não reserva capacidade para outras chamadas da aplicação. |
| Até 100.000 registros no banco | O crescimento da telemetria e dos históricos precisa ser acompanhado. |
| Um workspace | O projeto não pressupõe um segundo workspace para homologação isolada. |
| Background tasks, branching e ambientes sandbox da CLI em planos pagos | As automações atuais executam no Lightsail e chamam APIs do Xano, mantendo as decisões de negócio no backend. |

Recursos pagos e alterações de requisito para contornar limitações exigem decisão humana pelo fluxo OpenSpec.

## Informações técnicas e desenvolvimento

### Arquitetura e infraestrutura atual

O ambiente publicado utiliza **AWS Lightsail, Debian 13, Python 3.13 e Reflex 0.9.7**. A versão do Reflex está fixada em [requirements.txt](requirements.txt).

| Componente | Responsabilidade |
| --- | --- |
| AWS Lightsail | Hospeda a aplicação Reflex e as automações Python. |
| Caddy | Serve o frontend estático, encaminha as conexões ao backend Reflex e disponibiliza HTTPS com domínio gratuito `sslip.io` e certificado Let's Encrypt. |
| Backend Reflex | Mantém o estado da interface e consome os contratos do Xano. A configuração atual usa estado em memória, conforme [rxconfig.py](rxconfig.py). |
| Xano / XanoScript | Persiste os dados e executa autenticação, autorização, APIs e regras de negócio. |
| Simulator | Gera telemetria para totens já cadastrados e a envia ao Xano. |
| Fiscal | Solicita periodicamente ao Xano a verificação de heartbeat. |
| systemd | Gerencia os serviços contínuos e o agendamento do encerramento. |
| GitHub Actions | Executa testes, compila o frontend e publica releases no Lightsail por WireGuard e SSH. |

As decisões de negócio permanecem no Xano. O Simulator não cadastra totens nem cria chamados; o Fiscal não decide a indisponibilidade. O comando de encerramento apenas solicita uma verificação ao Xano.

#### Backend Xano

O backend do MIRA utiliza o **plano Free do Xano**, conforme a restrição acadêmica definida em [openspec/config.yaml](openspec/config.yaml) e as limitações descritas na seção 7. O Xano concentra o banco de dados, a autenticação dos usuários, a autorização por perfil e loja, o recebimento da telemetria, as regras de heartbeat, a tratativa dos chamados e os cálculos dos indicadores.

Os contratos HTTP incluem os grupos `MIRA Auth`, `MIRA Service Desk`, administração e APIs operacionais de telemetria. O Reflex consome esses contratos; Simulator, Fiscal e encerramento usam credenciais técnicas distintas, específicas para cada automação.

O código do backend está versionado em XanoScript:

- [xano/table/](xano/table/): schemas das tabelas.
- [xano/function/](xano/function/): funções reutilizáveis de negócio, autorização e indicadores.
- [xano/api/](xano/api/): endpoints e grupos de APIs.

O Xano Developer MCP apoia a consulta e a validação de XanoScript; a Xano CLI sincroniza o workspace. Antes de uma publicação no Xano, valide os arquivos afetados, execute `xano workspace push --dry-run` e revise o diff, seguindo [AGENTS.md](AGENTS.md). Essa publicação é separada do deploy da aplicação no Lightsail.

#### Organização no servidor

| Caminho | Uso |
| --- | --- |
| `/srv/mira/releases/` | Releases publicadas pelo pipeline. |
| `/srv/mira/current` | Link para a release ativa. |
| `/srv/mira/current/public/` | Frontend estático exportado pelo Reflex. |
| `/srv/mira/current/REVISION` | Commit incluído na release. |
| `/etc/mira/` | Arquivos de variáveis de ambiente, separados das releases e com permissões restritas. |


O [workflow de publicação](.github/workflows/verificacao.yml) está versionado. A configuração do Caddy, as unidades systemd e o receptor de deploy por SSH são mantidos no servidor; seus conteúdos não estão neste repositório.


#### Simulator e Fiscal

| Variável | Configuração |
| --- | --- |
| `SIMULATOR_ATIVOS` | IDs dos totens existentes que devem participar da simulação. |
| `SIMULATOR_INTERVAL_SECONDS` | Intervalo entre inícios de ciclos; padrão `300` segundos. |
| `SIMULATOR_INTERVAL_BETWEEN_ASSETS` | Espaçamento entre envios sequenciais; padrão `3` segundos. |
| `FISCAL_INTERVAL_SECONDS` | Intervalo entre verificações; padrão `300` segundos. |
| `FISCAL_REQUEST_TIMEOUT_SECONDS` | Timeout da chamada do Fiscal; padrão `30` segundos. |
| `SIMULATOR_ATIVO_CPU_ALTA` | ID do totem com cenário de CPU alta; vazio desativa. |
| `SIMULATOR_ATIVO_MEMORIA_ALTA` | ID do totem com cenário de memória alta; vazio desativa. |
| `SIMULATOR_ATIVO_TEMPERATURA_ALTA` | ID do totem com cenário de temperatura alta; vazio desativa. |
| `SIMULATOR_ATIVO_REDE_OFFLINE` | ID do totem cujo payload informa rede offline; vazio desativa. |
| `SIMULATOR_ATIVO_SILENCIADO` | ID do totem que deixa de enviar telemetria. Vazio desativa o silêncio. |

O `.env.example` deixa os cenários especiais vazios. O silêncio do totem é uma configuração do ambiente publicado. Alterar essas variáveis exige reiniciar o processo do Simulator; no servidor, reinicie `mira-mock.service`.

O Simulator inicia ciclos a cada cinco minutos e envia os totens sequencialmente, com três segundos entre requisições. O totem silenciado é omitido. O Fiscal começa depois que o Simulator conclui o primeiro ciclo de `make mock`; essa conclusão não garante que todos os envios HTTP tenham sido bem-sucedidos.

O Xano decide quando um totem previamente `Online` fica `Offline` por mais de 15 minutos sem telemetria. A criação de incidente `Novo/Urgente` respeita a prevenção de duplicidade para o mesmo totem e categoria. O retorno da telemetria pode restabelecer `Online`, mas não resolve nem encerra o chamado.

### Serviços e agendamento

| Unidade | Função |
| --- | --- |
| `mira-reflex.service` | Mantém o backend Reflex em execução contínua. |
| `mira-mock.service` | Executa `make mock`, coordenando Simulator e Fiscal. |
| `mira-encerramento.service` | Executa `make encerrar-resolvidos` uma vez e termina. |
| `mira-encerramento.timer` | Dispara o encerramento diariamente às **03h em `America/Sao_Paulo`**, sem recuperar execuções perdidas enquanto a VM estiver desligada. |

O timer agenda a execução do comando; o Xano continua responsável por selecionar e revalidar chamados elegíveis. O encerramento exige pelo menos 72 horas corridas em `Resolvido`, sem rejeição posterior, respeitando o início de vigência e a transição registrada.

O prazo de 72 horas torna o chamado elegível; a mudança ocorre quando uma verificação é executada. Com a agenda diária, um chamado pode aguardar o próximo horário das 03h.

### CI/CD com GitHub Actions

O fluxo está em [.github/workflows/verificacao.yml](.github/workflows/verificacao.yml):

1. Pull requests para `main` executam `make setup` e `make check`, que reúne testes Python e compilação de verificação do Reflex.
2. Pushes em `main` executam as mesmas verificações e, se passarem, exportam o frontend com `reflex export --frontend-only --no-zip`.
3. O pipeline gera `mira.tar.gz` com o código do commit, frontend em `public/`, arquivos de backend gerados quando presentes, dependências congeladas em `requirements-deploy.txt` e o identificador `REVISION`. O artefato `mira-release` fica disponível por sete dias.
4. O job de deploy usa o ambiente GitHub `production`, confirma que o commit ainda é o mais recente de `main`, abre o túnel WireGuard e envia o pacote por SSH privado com chave dedicada e verificação estrita da identidade do servidor.
5. O receptor no Lightsail publica em `/srv/mira/releases/`, atualiza `/srv/mira/current`, reinicia o backend e verifica a disponibilidade. O mecanismo de rollback no servidor restaura a versão anterior se a publicação falhar.

Também há execução por `workflow_dispatch`; a publicação exige a referência `main`. O pipeline publica a aplicação no Lightsail. A sincronização de contratos Xano é uma operação separada e não faz parte desse workflow.


### Desenvolvimento e validação local

Requisitos: Python 3.13, GNU Make e, para `make mock`, ambiente Linux com Bash, `setsid` e grupos de processos POSIX. As dependências Python estão em [requirements.txt](requirements.txt).

```bash
make setup
```

O comando cria `.venv`, instala as dependências e copia `.env.example` para `.env` se o arquivo ainda não existir. Preencha as URLs e as credenciais necessárias antes de executar a aplicação ou as automações.

| Comando | Uso |
| --- | --- |
| `.venv/bin/reflex run` | Executa a aplicação em desenvolvimento. |
| `make simulator` | Executa somente o Simulator. |
| `make fiscal` | Executa somente o Fiscal. |
| `make mock` | Executa Simulator e Fiscal coordenados até a interrupção. |
| `make encerrar-resolvidos` | Solicita uma verificação única ao Xano; pode encerrar chamados elegíveis. |
| `make py_test` | Executa a suíte Python com pytest. |
| `make reflex_check` | Executa `reflex compile --dry`. |
| `make check` | Executa os testes Python e a verificação Reflex usados pelo CI. |

### Desenvolvimento assistido por IA

O repositório inclui ferramentas opcionais de apoio à implementação, revisão e qualidade visual. A aplicação, os testes e o fluxo OpenSpec podem ser utilizados sem agentes.

#### Impeccable

O **Impeccable** é uma skill de design de interfaces usada para revisar e melhorar hierarquia visual, layout, tipografia, acessibilidade, responsividade e acabamento. Suas instruções estão versionadas em [.agents/skills/impeccable/](.agents/skills/impeccable/SKILL.md) e [.github/skills/impeccable/](.github/skills/impeccable/SKILL.md).

As alterações visuais seguem [DESIGN.md](DESIGN.md), os componentes existentes e os requisitos funcionais aprovados no OpenSpec.

#### Agentes do MIRA

No Codex, os papéis estão registrados em [.codex/config.toml](.codex/config.toml), com definições em [.codex/agents/](.codex/agents/). As regras gerais de trabalho estão em [AGENTS.md](AGENTS.md).

| Papel | Responsabilidade |
| --- | --- |
| Supervisor | Agente principal que delimita o trabalho autorizado, delega tarefas e coordena as rodadas de implementação e revisão. |
| MIRA Implementer | Implementa somente o escopo autorizado e devolve alterações, testes e evidências ao Supervisor. |
| MIRA Reviewer | Revisa specs, diff, testes e riscos de forma independente e somente leitura; conclui com `aprovado`, `correção necessária` ou `decisão humana necessária`. |

Para solicitar esse fluxo, informe a tarefa ou change e peça ao agente principal que delegue a implementação ao MIRA Implementer e a revisão ao MIRA Reviewer. Em Explore, a delegação se limita à investigação sem alterações. Novas decisões de negócio e operações como Archive ou merge em `main` seguem os pontos de revisão humana definidos em `AGENTS.md`.

### Documentação e OpenSpec

O projeto utiliza **Spec-Driven Development**, com o fluxo `explore → propose → revisão humana → apply → archive`. Mudanças relevantes de produto, APIs, modelo de dados ou arquitetura seguem esse processo.

- [Visão do projeto](docs/project-overview.md): objetivos, escopo e arquitetura do produto.
- [Modelo de domínio](docs/domain-model.md): conceitos, relacionamentos e invariantes.
- [Specs consolidadas](openspec/specs/): comportamento aprovado.
- [Changes](openspec/changes/): propostas e alterações em desenvolvimento; `archive/` preserva o histórico.
- [Configuração OpenSpec](openspec/config.yaml): restrições globais, incluindo uso do plano Free do Xano.
- [Makefile](Makefile): comandos de desenvolvimento e instalação opcional de Xano CLI e OpenSpec.
