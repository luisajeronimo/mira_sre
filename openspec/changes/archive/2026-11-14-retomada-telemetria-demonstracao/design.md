# Design — retomada contínua e demonstração de confiabilidade

## Context

A motivação está em `proposal.md`. O Simulator lê `SIMULATOR_ATIVOS` e `SIMULATOR_ATIVO_SILENCIADO` ao iniciar; não consulta controle remoto. O POST de telemetria somente persiste amostras. `GET /verificar-falhas`, chamado pelo Fiscal, decide as transições e registra `historico_disponibilidade_totens`. O monitoramento atual oferece apenas consultas.

Os indicadores já são calculados no Xano a partir das telemetrias referenciadas e dos vínculos históricos. O gráfico em `app/indicadores/pages.py` usa duas séries diárias, lacunas para dias sem eventos e conversão de minutos para horas. O SVG oficial existe, mas `app/app.py` não declara um favicon global.

As specs atuais proíbem backfill e vínculos retroativos. O usuário corrigiu expressamente o escopo: usar Totens existentes e não criar Totens. O histórico fictício exige exceção delimitada para novos fatos nos IDs 1 e 2; não permite reescrever fatos nem retroagir vínculos. As configurações systemd do Lightsail não estão versionadas no repositório.

## Goals / Non-Goals

**Objetivos técnicos:** separar controle de envio e disponibilidade; manter as decisões no Xano; permitir retomada que sobreviva a ciclos e reinícios; preparar um lote sintético repetível; preservar os contratos de cálculo; reutilizar a marca e a linguagem visual atuais.

**Fora do desenho:** shell, SSH ou `systemctl` acessíveis pela interface; configuração escrita pelo navegador; status Online otimista; segundo Fiscal; pausa pela interface; importação histórica genérica; métricas pré-calculadas no banco; nova entidade de negócio, novo segredo ou serviço pago. O Simulator continua gerando telemetria apenas para Totens cadastrados.

## Decisions

### D1. Um controle de simulação explícito no Totem

Propor `ativos_referencia.telemetria_simulada_ativa` como booleano nullable, separado de `status_atual`:

| Valor | Significado |
| --- | --- |
| `null` | Totem não registrado no controle remoto de simulação. |
| `false` | Totem simulado registrado, com envio silenciado. |
| `true` | Totem simulado registrado, com envio contínuo permitido. |

Não preencher o campo por inferência sobre Online/Offline. Uma preparação operacional explícita inicializa somente os IDs de `SIMULATOR_ATIVOS` revisados para o ambiente: o ID configurado em `SIMULATOR_ATIVO_SILENCIADO` começa em `false`; os demais, em `true`. Reexecução não sobrescreve controles já inicializados. O procedimento apresenta a prévia antes de escrever e interrompe em caso de valor divergente que exigiria alteração de cadastro existente.

Depois da transição, `SIMULATOR_ATIVO_SILENCIADO` é insumo dessa preparação inicial, sem força para voltar a silenciar um controle `true` em cada ciclo ou reinício. `SIMULATOR_ATIVOS` permanece a lista local explícita de participação: o Simulator não passa a enviar para todo o inventário.

**Alternativas:** enviar uma única telemetria não atende à retomada contínua; gravar `status_atual = online` contorna os fatos que sustentam MTTR; escrever `.env` pelo Reflex ou comandar systemd criaria acoplamento operacional e persistência paralela. O campo proposto usa o backend já responsável pelos dados e precisa de aprovação na revisão da change.

### D2. Contratos distintos para pessoa e automação

Contratos propostos, sem mudar as URLs atuais de telemetria e heartbeat:

| Contrato | Autenticação | Efeito |
| --- | --- | --- |
| `GET /simulator/controle-telemetria`, na base operacional | `X-MIRA-Simulator-Key` | Recebe os IDs participantes e devolve somente seus IDs e controles, sem escrita. |
| `POST /monitoramento/ativos/{ativos_referencia_id}/retomar-telemetria`, na base Service Desk | Sessão humana de Técnico, Diretoria ou Administrador, sem troca de senha pendente | Altera somente o controle do Totem selecionado para `true`. |
| Detalhe existente de monitoramento | Autorização operacional existente | Acrescenta `telemetria_simulada_ativa`, nullable, para contextualizar a ação. |

O POST não recebe CPU, memória, timestamps, status, segredo ou IDs de outros recursos. O Xano autoriza antes de ler o alvo: sessão inválida resulta em 401; Gerente, perfil não oficial ou primeiro acesso pendente são negados; alvo inexistente resulta em 404. Totem não gerenciado ou silenciado sem estar Offline é rejeitado como estado incompatível. Para um controle já `true`, uma repetição retorna confirmação sem nova alteração, inclusive se a recuperação ocorreu entre as requisições.

A resposta de sucesso confirma **envio autorizado**, nunca recuperação concluída. Não cria telemetria, evento Online ou interação de chamado. A autorização dos três perfis acompanha a matriz operacional vigente e será ratificada na revisão; a criação de cadastros continua exclusiva da Administração.

Não expor um endpoint HTTP para importar histórico, nem atribuir permissões humanas à chave técnica. O procedimento de preparação usa a CLI autenticada do operador e funções Xano do namespace `demonstracao/`, não as APIs normais de usuário.

### D3. Consulta agrupada uma vez por ciclo

Antes dos POSTs do ciclo, o Simulator faz uma consulta de controle para a lista configurada. Somente IDs presentes com controle `true` enviam telemetria. `false` permanece silenciado; `null`, ID omitido ou não cadastrado não autorizam envio e produzem diagnóstico sem segredo. Não há requisição adicional por Totem nem chamada ao Fiscal pelo Simulator.

Se a consulta agrupada falhar ou seu formato não puder ser validado, o ciclo não envia amostras e tenta novamente no próximo ciclo normal. Não usa valor antigo ou `.env` como autorização alternativa. Essa escolha evita desfazer uma decisão persistida, mas uma indisponibilidade prolongada da consulta pode causar ausência de heartbeat; deve ser explicitamente aprovada e testada.

A confirmação passa a valer na próxima consulta de ciclo bem-sucedida. Se ela chegar depois da consulta já feita, vale no ciclo seguinte. O novo ciclo envia uma amostra atual e continua enviando nos posteriores. O estado do Totem permanece o retornado pelo Xano até uma verificação normal do Fiscal registrar a recuperação. Isso não garante prazo em caso de falha HTTP ou serviço parado.

Mantêm-se ciclos de 300 s e espaçamento de 3 s. O exemplo atual de 15 Totens tem até 15 POSTs e dois GETs por ciclo: controle e Fiscal. O histórico fictício usa dois desses participantes, sem ampliar a lista. O espaçamento mantém até sete POSTs por janela de 20 s; incluindo ambos os GETs, o tráfego dessas automações pode chegar a nove requisições na janela. Isso não reserva capacidade contra tráfego da aplicação ou de outros clientes.

**Alternativas:** polling por Totem aumenta requisições; consulta mais frequente ou segundo Fiscal ampliaria o escopo e a pressão no Free. A leitura agrupada é suficiente para a retomada contínua pedida.

### D4. Confirmação no detalhe, com resultado verificável

Na página de monitoramento, mostrar **Retomar telemetria** quando o Totem selecionado estiver `offline` e seu controle for `false`. Para `true` ainda Offline, informar que o envio já está autorizado, sem afirmar que o processo está saudável. `null` ou metadado ausente não oferecem a ação. A ausência do metadado permite compatibilidade de leitura durante a atualização, sem inventar controle.

O diálogo identifica nome e Loja do Totem e explica: **“A telemetria simulada voltará a ser enviada nos próximos ciclos. A retomada não resolve nem encerra chamados.”** As ações são **Cancelar** e **Retomar telemetria**.

Abrir, cancelar ou fechar o diálogo não envia POST. Confirmar envia uma única solicitação, bloqueia reenvio durante o processamento e mantém o ID do alvo confirmado mesmo que haja interação com a seleção. Ao trocar de Totem, fechar e descartar a confirmação anterior. Resposta tardia não aplica dados ao novo Totem selecionado. O sucesso recarrega lista e detalhe e informa **“Envio de telemetria autorizado. Aguarde os próximos ciclos.”** Erro mantém os estados confirmados, permite nova tentativa quando apropriado e segue o tratamento central de sessão.

Reutilizar diálogo acessível, tokens e foco visível do projeto, com navegação por teclado, retorno de foco à ação e feedback textual. Não redesenhar o painel ou adicionar monitoramento da saúde do Fiscal. A autoridade visual continua em `DESIGN.md`.

### D5. Histórico fictício exclusivamente nos Totens existentes

A instrução humana posterior **“usa os totems ja existentes pra mockar, vc esta proibido de criar totems novos”** substitui o desenho anterior de novos cadastros. Nenhum Totem, Loja, vínculo, usuário, chamado ou interação será criado pelo lote. A consulta ao Xano confirmou os mesmos 16 Totens e nenhum cadastro criado por esta change.

O lote fechado `DEMO-CONFIABILIDADE-V2-2026-11-14` usa exclusivamente os Totens **1 (TOT-PAU-001)** e **2 (TOT-PAU-002)**, já existentes na Loja 1. A data-base é 14/11/2026, com 30 dias completos de 15/10 a 13/11 em Brasília. O inventário somente leitura conferiu as 60 janelas sem sobreposição com amostras/transições existentes. O Xano deve repetir essa conferência antes das escritas, rejeitando divergência de cadastro, colisão ou janela ocupada.

Cada Totem recebe uma amostra inicial e 30 pares com duas telemetrias de referência e duas transições: **122 telemetrias e 120 transições, total de 242 registros**, sem amostras atuais de finalização. Eventos começam às 05h/06h em Brasília, variam deterministicamente e preservam MTTD de 16–20 min e MTTR de 30–180 min. Offline e Online respeitam fiscalização fictícia de cinco minutos. As durações são derivadas dos fatos, nunca médias persistidas.

A carga altera somente esses fatos sintéticos. Nomes, identificações, Loja, estado atual, controle de simulação e fatos anteriores permanecem íntegros. Não cria vínculos retroativos: o recorte global ou por Totem permite observar os 30 dias; o recorte por Loja continua limitado ao vínculo histórico comprovado, sem inferir a Loja atual. A nota acadêmica identifica os dois IDs que recebem o histórico fictício, sem renomear cadastros.

### D6. População pontual concluída, sem importador permanente

A preparação foi uma operação única da demonstração, já concluída: **242 fatos**
no lote `DEMO-CONFIABILIDADE-V2-2026-11-14`. A prévia e o manifesto fixaram
workspace, versão, IDs, data-base, payloads e contagens, sem credenciais.
A interrupção foi retomada a partir dos fatos conferidos no Xano; a repetição de
conferência retornou zero novos registros. Esses resultados ficam em
o registro de validação no checklist.

Amostras foram comparadas por Totem/timestamp e transições por
Totem/status/detecção, incluindo conteúdo integral e referência. Duplicidade
ou divergência interromperam a operação sem sobrescrever dados. Não houve
limpeza, rollback global, criação de cadastro ou inicialização de estado no lote.

Por decisão humana posterior, o utilitário Python temporário é removido após a
população. Não haverá CLI, comando Make, endpoint público, rotina automática ou
procedimento de aplicação que volte a carregar o gráfico. As funções Xano usadas
na operação e seus testes de integridade registram a implementação realizada;
não são chamadas pelo Reflex, pelo Simulator, pelo Fiscal ou pelo deploy. Não
executar novamente a carga para validar a interface.

### D7. Cálculo normal, identificação do contexto e favicon global

Os Totens de demonstração participam dos filtros e agregados normais da rede. Os filtros dos Totens 1 e 2 permitem selecionar os alvos existentes. Exibir no painel de confiabilidade uma nota clara de **ambiente acadêmico com dados simulados**, para que um agregado global não pareça resultado de clientes reais. Não selecionar Totem ou Loja automaticamente nem excluir o lote dos agregados sem alterar o filtro visível.

Os 30 dias completos dão uma série diária densa pelo filtro personalizado; no atalho padrão de 30 dias, podem aparecer 29 dias completos com dados e o dia atual parcial. Manter o comportamento de Hoje, as unidades em horas na apresentação, cores distintas, legendas textuais, tooltip com data/valor, eixos legíveis e lacunas em dados ausentes. Os cálculos e as médias do período continuam nas funções existentes do Xano, sem alterar o contrato para acomodar a estética.

Para o favicon, declarar o SVG oficial no cabeçalho global do app Reflex (`head_components`, disponível na versão instalada), incluindo login e primeiro acesso. Verificar o HTML exportado e eventuais declarações padrão concorrentes para que o ícone selecionado seja o oficial. Reutilizar o mesmo SVG; não redesenhar a marca, introduzir imagem gerada ou depender de arquivo externo. A publicação já empacota os assets exportados.

## Risks / Trade-offs

- **Consulta de controle indisponível interrompe envios do ciclo** → explicitar o resultado, preservar o intervalo e testar a recuperação no ciclo seguinte; não mascarar a falha com estado antigo.
- **Retomada não é imediata** → confirmar somente a autorização de envio e mostrar o estado persistido até o Fiscal registrar a recuperação; não prometer prazo quando há falha de serviço ou rede.
- **Inicialização incompleta silencia outros Totens** → preparar e conferir todos os IDs participantes antes de trocar a versão do Simulator; não reinterpretar `null` como autorização.
- **Dados sintéticos alteram agregados da rede e ocupam armazenamento** → usar cadastros identificados, mostrar o contexto simulado, limitar a 242 registros no lote fechado e verificar capacidade antes da carga, sem limpeza histórica.
- **Backdating sintético pode ser confundido com fato real** → restringir a IDs existentes fixados no plano e preservar o instante técnico de criação; exigir aprovação dos deltas que introduzem a exceção.
- **A carga pode falhar parcialmente** → etapas determinísticas, diagnóstico e retomada verificável; não depender da prova E0.3 ainda não comprovada em runtime nem aceitar nova limitação funcional silenciosamente.
- **Concorrência ou edição manual dos cadastros de demonstração** → execução operacional única e interrupção diante de duplicidade ou divergência; nenhuma correção destrutiva automática.
- **Cota Free e tempo de execução** → consulta agrupada, espaçamento preservado e carga em lotes pequenos. Não depender de background tasks, branches ou sandbox pagos. Conferir o plano vigente antes da publicação, tomando a [página oficial](https://www.xano.com/pricing/) e o Xano Developer MCP como referências.
- **Ambiente real e navegador não disponíveis para validação** → registrar verificações como bloqueadas, não como aprovadas. A aprovação estática dos artefatos não comprova runtime, deploy ou aparência renderizada.

## Validação e fechamento após a correção humana

1. Preservar os 242 fatos já carregados nos Totens existentes 1 e 2 e as evidências da conferência. Não repetir a população nem alterar cadastros, vínculos, estado, controles ou chamados para fabricar um teste.
2. Remover o utilitário temporário da carga e o arquivo de repasse entre agentes; restaurar o README anterior. Preservar os testes locais de integridade do histórico que não dependem do utilitário removido.
3. Conferir testes locais, compilação, diff e OpenSpec strict. A validação runtime da aplicação ocorre somente em desenvolvimento local com `reflex run`; não acessar o servidor para testar ou publicar.
4. Disponibilizar a aplicação local e avisar o usuário para testar o diálogo, a retomada, o gráfico e o favicon. Verificações autenticadas pendentes continuam abertas até evidência real.
5. Parar antes de Archive e commit. Aguardar o teste e a decisão humana. Se autorizado posteriormente, primeiro consolidar/arquivar a change; somente depois criar commit e tratar qualquer publicação separadamente.

O commit e o push antecipados foram desfeitos a pedido do usuário, preservando a
implementação em arquivos locais. Essa correção de Git não apaga os fatos já
persistidos no Xano nem altera recursos remotos fora do commit. Não fazer
rollback, exclusão de dados ou operação adicional no servidor por inferência.

## Revisão necessária

D1–D7 tiveram implementação autorizada, com correção humana posterior que proíbe novos Totens e determina a carga pontual, a remoção do utilitário e a validação somente local. A revisão restante é o teste humano da aplicação dev. Archive e novo commit aguardam essa revisão, nessa ordem; a instrução de continuar o Apply não substitui esse gate.
