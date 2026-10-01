## Why

O Fiscal chama `GET /verificar-falhas` e o Simulator chama `POST /telemetria_equipamentos` anonimamente. Quem descobrir essas URLs pode disparar verificação operacional ou enviar telemetria sem uma credencial de finalidade. Isso expõe os dois pontos de entrada que alimentam processos já autoritativos no Xano.

## What Changes

- Exigir uma credencial técnica dedicada em header para cada automação, validada no Xano antes de qualquer leitura operacional, lógica de heartbeat ou persistência.
- Fiscal: `X-MIRA-Fiscal-Key`, provido pelo Python e comparado ao segredo lógico Xano `MIRA_FISCAL_AUTOMATION_KEY`.
- Simulator: `X-MIRA-Simulator-Key`, provido pelo Python e comparado ao segredo lógico Xano `MIRA_SIMULATOR_AUTOMATION_KEY`.
- Rejeitar com HTTP 401 credencial ausente, inválida ou segredo Xano não configurado, sempre com o corpo público exato `{"error":"Não autenticado."}` e sem outros campos, dados operacionais, segredo ou detalhe de configuração.
- Remover o modo `--telemetria` do Fiscal sem substituto.
- Definir periodicidades operacionais padrão de cinco minutos para o Fiscal e para o ciclo do Simulator; o ciclo e o espaçamento podem ser sobrescritos por configuração de ambiente, sem alterar a regra de domínio do heartbeat no Xano.

Esta change preserva URL, método e payload das chamadas bem-sucedidas. O efeito observável pretendido é que chamadas sem a credencial técnica correta deixem de ser aceitas.

## Scope

- Guardas Xano separados para `GET /verificar-falhas` e `POST /telemetria_equipamentos`.
- Configuração segura por variável de ambiente nos scripts Python, sem valores reais em arquivos versionados.
- Remoção do diagnóstico `--telemetria` do Fiscal.
- Ciclo operacional do Simulator iniciado a cada cinco minutos: dentro de cada ciclo, os 15 Totens são enviados sequencialmente com espaçamento padrão de três segundos entre POSTs; o ciclo leva alguns segundos por esse espaçamento, sem criar fila ou infraestrutura nova.
- Testes de credencial, contrato, regressão de heartbeat e proteção contra vazamento de segredo.

## Out of Scope

- Usuário técnico, Bot, tabela de credenciais, OAuth, IAM ou alteração da autenticação humana por `usuarios`, login e sessão de oito horas.
- Mudança da regra Xano de disponibilidade, heartbeat, deduplicação, incidentes automáticos, SLA ou payload funcional de telemetria.
- Alterar endpoints humanos, permitir que credenciais técnicas autorizem APIs humanas ou alterar URLs e métodos das automações.
- Fila, agendador externo, infraestrutura de rate limit ou rotação automatizada de segredos.

## Impact

- **Fiscal:** passa a enviar `X-MIRA-Fiscal-Key`; sem a variável Python correspondente, a execução deve falhar de modo explícito e seguro antes de enviar uma chamada anônima. O padrão operacional será de cinco minutos.
- **Simulator:** passa a enviar `X-MIRA-Simulator-Key`; o ciclo operacional padrão inicia a cada cinco minutos e envia os 15 Totens sequencialmente, com três segundos entre POSTs. Os cinco minutos são entre inícios de ciclos, não entre Totens.
- **Xano:** cada endpoint compara exclusivamente sua própria credencial antes de processar a requisição. Segredo Xano ausente falha fechado, sem comparação permissiva com valor vazio ou nulo. A rejeição HTTP 401 com `{"error":"Não autenticado."}` e sem outros campos ocorre antes de leitura, persistência, cálculo de heartbeat, alteração de disponibilidade ou incidente. O segredo do Fiscal não autoriza telemetria, o do Simulator não autoriza heartbeat e todas as credenciais técnicas NÃO DEVEM autorizar endpoints humanos.
- **Compatibilidade:** clientes com segredo válido mantêm URL, método e payload atuais; clientes sem segredo passam a receber rejeição.

## Limites e gate pré-Apply

Antes do Apply, deve ser confirmada documentalmente e/ou em runtime a disponibilidade, no plano Free do Xano, do mecanismo selecionado para armazenar e obter no servidor `MIRA_FISCAL_AUTOMATION_KEY` e `MIRA_SIMULATOR_AUTOMATION_KEY`, bem como o acesso de endpoints/XanoScript aos headers `X-MIRA-Fiscal-Key` e `X-MIRA-Simulator-Key` conforme este design. Se qualquer capacidade não estiver disponível no Free, ou exigir recurso pago, o Apply deve parar com `HUMAN_DECISION_REQUIRED`; esta Propose não implementa alternativa automática nem sugere upgrade.

O limite Free também deve ser avaliado contra as periodicidades alvo e os 15 Totens documentados em `.env.example`. Fiscal e Simulator executam a cada cinco minutos; no Simulator, os cinco minutos são entre inícios de ciclos, não entre Totens. Dentro de cada ciclo, os 15 Totens são enviados sequencialmente a cada três segundos, de modo que o ciclo leva alguns segundos. Para a carga das automações, isso limita o burst a no máximo sete POSTs do Simulator por janela de vinte segundos, ou oito incluindo eventual disparo do Fiscal, e resulta na cadência média de 15 POSTs mais um GET por cinco minutos. O ciclo e o espaçamento podem ser sobrescritos por configuração de ambiente, sem alterar a regra de domínio. O Xano continua decidindo Offline somente pela última telemetria superior a quinze minutos; o Python não calcula esse timeout. Um ciclo de telemetria de quinze minutos junto de timeout superior a quinze minutos opera no limite e pode gerar falso Offline por atraso; ciclos de cinco minutos fornecem aproximadamente três períodos esperados de telemetria antes do timeout. O Fiscal apenas dispara a verificação e não conhece nem decide essa regra. Isso não reserva capacidade contra tráfego externo e não introduz fila, scheduler externo, rate limiter ou infraestrutura nova.

## Risks

- [Segredo ausente ou incorreto] A automação pode ser rejeitada e interromper sua operação → validar a variável antes da chamada, testar ausência/valor inválido/válido e não enviar fallback anônimo.
- [Privilégio cruzado] Uma chave pode ser aceita no endpoint errado → usar guardas e segredos lógicos distintos, com testes cruzados explícitos.
- [Vazamento] Logs ou respostas podem expor material de autenticação → nunca registrar headers ou valores, e usar rejeição uniforme.
- [Burst no Free] Execuções concorrentes do Simulator podem pressionar o plano → manter ciclos de cinco minutos e espaçamento de três segundos; o limite de sete POSTs em vinte segundos, ou oito com Fiscal, e a média de 15 POSTs mais um GET por cinco minutos não reservam capacidade contra tráfego externo.
- [Regressão operacional] A proteção pode alterar lógica já consolidada → validar que o guard executa antes de qualquer lógica e que chamadas válidas preservam heartbeat, payload e contrato atual.

## Estratégia incremental

1. Confirmar a disponibilidade Free e preparar, fora do versionamento, os dois segredos de ambiente.
2. Implementar e validar primeiro o guarda exclusivo do Fiscal, depois o do Simulator.
3. Inventariar código, documentação, testes, Makefile e scripts consumidores de `Fiscal --telemetria`; ajustar ou confirmar a ausência de cada consumidor e remover o modo sem substituto.
4. Atualizar os scripts para enviar somente sua credencial de finalidade e aplicar defaults operacionais de cinco minutos e espaçamento de três segundos; ciclo e espaçamento podem ser sobrescritos por configuração de ambiente, sem alterar a regra de domínio do heartbeat no Xano.
5. Executar testes de autenticação técnica, privilégio cruzado, regressão operacional e validação XanoScript; revisar dry-run antes de qualquer push autorizado.
