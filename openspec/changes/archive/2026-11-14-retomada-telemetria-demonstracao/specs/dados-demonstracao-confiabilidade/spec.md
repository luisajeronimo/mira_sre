## Purpose

Preparar histórico fictício no Xano usando exclusivamente Totens existentes, sem criar cadastros ou reescrever fatos anteriores.

## ADDED Requirements

### Requirement: População é pontual e não integra a aplicação
O histórico fictício DEVE (MUST) resultar de uma única população operacional delimitada pelo lote `DEMO-CONFIABILIDADE-V2-2026-11-14`, já concluída. A execução DEVE (MUST) preservar a prévia e as evidências de ambiente, versão, data-base, IDs e contagens. Após a conclusão, o utilitário temporário de carga DEVE (MUST) ser removido. A aplicação, o deploy e a validação da interface NÃO DEVEM (MUST NOT) repetir a população, e NÃO DEVE (MUST NOT) existir endpoint público de importação ou CLI permanente de carga no repositório.

#### Scenario: População foi concluída
- **WHEN** os 242 fatos do lote estão conferidos no Xano
- **THEN** as evidências são preservadas e o utilitário temporário é descartado, sem excluir os fatos

#### Scenario: Aplicação é iniciada ou validada
- **WHEN** o Reflex, o Simulator, o Fiscal ou o deploy é executado após a carga
- **THEN** nenhum deles chama as funções de população nem recarrega o histórico fictício

### Requirement: Nenhum cadastro novo é criado
O lote DEVE (MUST) usar somente os Totens existentes 1 e 2, conferindo seus nomes e Loja contra o plano. NÃO DEVE (MUST NOT) criar Totem, Loja, usuário, chamado, interação ou vínculo, nem renomear ou transferir cadastros. A proibição de criar Totens é uma decisão humana explícita que substitui o desenho anterior.

#### Scenario: Cadastros válidos
- **WHEN** os Totens 1 e 2 correspondem ao inventário revisado
- **THEN** seus IDs são utilizados sem qualquer alteração cadastral

#### Scenario: Cadastro mudou ou destino é outro
- **WHEN** o ID não é 1 ou 2, está ausente ou seu cadastro divergiu
- **THEN** a carga é rejeitada sem criar substitutos

### Requirement: Cronologia fictícia respeita os fatos existentes
O lote DEVE (MUST) cobrir 15/10 a 13/11/2026 em Brasília, com uma amostra inicial e 30 pares Offline/Online por Totem. Os pares DEVEM (MUST) ter referências válidas, MTTD de 16–20 min, MTTR de 30–180 min e detecções na cadência fictícia de cinco minutos. Janelas ocupadas por fatos externos ao plano DEVEM (MUST) ser rejeitadas.

#### Scenario: Janelas livres e válidas
- **WHEN** o plano é conferido contra as telemetrias e transições do Xano
- **THEN** há 60 detecções e 60 recuperações ordenadas, sem sobreposição nem fatos futuros

#### Scenario: Janela ocupada ou data inválida
- **WHEN** há telemetria ou transição conflitante, estado anterior Offline, referência inválida ou data fora do plano
- **THEN** a preparação rejeita a etapa antes de escrevê-la

### Requirement: Lote preserva operação atual e vínculos
A carga DEVE (MUST) alterar somente novos fatos sintéticos do plano. NÃO DEVE (MUST NOT) escrever estado atual, controle de envio, identificação ou Loja do Totem. NÃO DEVE (MUST NOT) criar amostra atual de finalização nem inferir vínculos retroativos. O recorte por Loja DEVE (MUST) continuar limitado à evidência histórica existente.

#### Scenario: Lote termina ou sua integridade é conferida
- **WHEN** a preparação conclui as etapas históricas
- **THEN** estado, controles, cadastros, vínculos e chamados existentes permanecem íntegros

### Requirement: Integridade da população compara os fatos integralmente
A conferência e a retomada da carga parcial pertencem à mesma população pontual já realizada; não exigem manter um importador depois de concluída. Amostras DEVEM (MUST) ser identificadas por Totem/timestamp e transições por Totem/status/detecção. Uma correspondência DEVE (MUST) coincidir no conteúdo integral e nas referências para ser reutilizada. Duplicidade ou divergência DEVE (MUST) interromper a carga sem exclusão, substituição ou promessa de rollback global.

#### Scenario: Repetição exata
- **WHEN** o lote já existe íntegro no Xano
- **THEN** nenhum novo registro é criado

#### Scenario: Interrupção e retomada
- **WHEN** parte dos fatos existe e coincide com o mesmo plano
- **THEN** as etapas confirmadas são preservadas e somente os fatos faltantes são criados

#### Scenario: Conteúdo divergente
- **WHEN** uma chave encontra múltiplos registros ou dados diferentes
- **THEN** a carga interrompe e informa a etapa sem apagar ou substituir dados

### Requirement: Capacidade limita a carga a fatos históricos
O lote DEVE (MUST) criar no máximo 242 registros: 122 telemetrias e 120 transições. A preparação DEVE (MUST) conferir capacidade do plano Free antes de escrever. Capacidade insuficiente DEVE (MUST) interromper sem limpeza automática ou upgrade implícito.

#### Scenario: Há capacidade
- **WHEN** o Xano comporta os 242 fatos previstos
- **THEN** a carga permanece limitada às duas tabelas históricas autorizadas

#### Scenario: Não há capacidade
- **WHEN** a carga ultrapassaria a capacidade disponível
- **THEN** nenhuma escrita é iniciada

### Requirement: Indicadores usam os contratos normais
Os fatos DEVEM (MUST) participar dos filtros e agregados normais da rede e dos Totens existentes, com nota visível do contexto fictício e dos IDs utilizados. MTTD e MTTR DEVEM (MUST) vir dos cálculos Xano existentes, sem seleção oculta de filtro ou valores locais substitutos.

#### Scenario: Intervalo completo por Totem
- **WHEN** um perfil operacional seleciona Totem 1 ou 2 no intervalo completo
- **THEN** recebe a série diária calculada dos fatos persistidos

#### Scenario: Recorte global ou por Loja
- **WHEN** o usuário consulta outro recorte
- **THEN** a consulta mantém as fórmulas normais e a resolução histórica de Loja, sem excluir fatos ou inventar vínculos
