## Contexto

Fiscal e Simulator são processos máquina-a-máquina distintos das identidades humanas do MIRA. Eles não usam `usuarios`, login ou token de sessão. A autorização de domínio — heartbeat, disponibilidade, deduplicação e incidentes — continua no Xano e não é transferida aos scripts Python.

## Decisão técnica

Cada automação terá uma credencial de finalidade, fornecida ao processo Python por variável de ambiente e enviada somente em seu header dedicado:

| Processo | Header | Variável/segredo lógico Xano |
| --- | --- | --- |
| Fiscal | `X-MIRA-Fiscal-Key` | `MIRA_FISCAL_AUTOMATION_KEY` |
| Simulator | `X-MIRA-Simulator-Key` | `MIRA_SIMULATOR_AUTOMATION_KEY` |

Cada endpoint compara, no backend, somente o header aplicável ao seu segredo lógico antes de qualquer leitura operacional, cálculo de heartbeat, consulta necessária ou persistência. Header ausente, inválido ou segredo Xano não configurado recebe HTTP 401 com o corpo público exato `{"error":"Não autenticado."}`, sem outros campos, valor esperado, configuração, existência parcial de recurso ou dados operacionais. Segredo Xano ausente falha fechado, sem comparação permissiva com valor vazio ou nulo. Antes dessa rejeição não ocorre leitura, persistência, cálculo de heartbeat, alteração de disponibilidade ou incidente. Headers e segredos não entram em logs ou respostas.

O guard do Fiscal protege somente `GET /verificar-falhas`; o guard do Simulator protege somente `POST /telemetria_equipamentos`. Não há chave compartilhada, privilégio cruzado ou uso das chaves em endpoints humanos: todas as credenciais técnicas NÃO DEVEM autorizar endpoints humanos. A credencial técnica não cria usuário técnico, Bot de Fiscalização, identidade humana nem substitui as regras de autorização existentes no Xano.

## Fluxo

1. O processo Python lê sua variável de ambiente obrigatória antes de efetuar a chamada.
2. Com variável ausente, o processo falha explicitamente sem enviar chamada anônima.
3. Com variável presente, envia URL, método e payload existentes mais seu único header técnico.
4. O Xano compara o header ao segredo de mesma finalidade antes de processar a rota.
5. Somente após a comparação bem-sucedida o endpoint executa seu contrato já consolidado.

## Periodicidades e plano Free

Fiscal e Simulator terão default operacional de cinco minutos. O Simulator inicia um ciclo operacional a cada cinco minutos; os cinco minutos são entre inícios de ciclos, não entre cada Totem. Dentro do ciclo, envia os 15 Totens sequencialmente com espaçamento padrão de três segundos entre POSTs, portanto o ciclo leva alguns segundos. O ciclo e o espaçamento podem ser sobrescritos por configuração de ambiente, sem alterar a regra de domínio. O Xano continua decidindo Offline exclusivamente quando a última telemetria supera quinze minutos; o Python não calcula esse timeout. Um ciclo de telemetria de quinze minutos junto de timeout superior a quinze minutos opera no limite e pode gerar falso Offline por atraso; ciclos de cinco minutos fornecem aproximadamente três períodos esperados de telemetria antes do timeout. O Fiscal apenas dispara a verificação e não conhece nem decide a regra de quinze minutos.

Considerando os 15 Totens documentados em `.env.example`, o espaçamento de três segundos limita o burst a no máximo sete POSTs do Simulator por janela de vinte segundos, ou oito incluindo eventual disparo do Fiscal. Com um ciclo do Simulator e um disparo do Fiscal a cada cinco minutos, a cadência média das automações é de 15 POSTs mais um GET por cinco minutos. Isso não reserva capacidade contra tráfego externo. Esta change não cria fila, worker, scheduler externo ou infraestrutura de rate limit. A compatibilidade dessas periodicidades e do mecanismo selecionado para armazenar/obter os dois segredos no servidor, além do acesso de endpoints/XanoScript aos headers técnicos, é um gate pré-Apply: a documentação oficial e/ou validação runtime deve confirmar que tudo está disponível no plano Free. Na ausência de confirmação ou diante de recurso pago, o Apply para com `HUMAN_DECISION_REQUIRED`, sem alternativa automática ou sugestão de upgrade.

## Rotação e revogação

A rotação simples consiste em substituir um segredo no ambiente Python e no mecanismo de ambiente Xano de mesma finalidade, validar a automação correspondente e revogar o valor anterior. A revogação ocorre ao substituir ou remover o segredo no Xano e interromper a automação afetada até que a configuração Python válida seja restaurada. Valores reais nunca serão colocados no repositório, em logs ou em respostas.

## Migração

1. Confirmar o mecanismo Free antes de editar Xano ou scripts.
2. Configurar os segredos reais somente nos ambientes apropriados.
3. Adicionar e validar os guardas antes da lógica de cada endpoint.
4. Inventariar código, documentação, testes, Makefile e scripts consumidores de `--telemetria`; ajustar ou confirmar a ausência de cada consumidor e remover o modo sem ferramenta substituta.
5. Atualizar Fiscal e Simulator com as variáveis Python `MIRA_FISCAL_AUTOMATION_KEY` e `MIRA_SIMULATOR_AUTOMATION_KEY` e seus headers dedicados.
6. Validar chamadas sem, com valor inválido e com valor correto; testar separação de privilégios, HTTP 401 uniforme e regressão de heartbeat/payload.
7. Executar validação XanoScript e `xano workspace push --dry-run`; aguardar autorização antes de push real.
