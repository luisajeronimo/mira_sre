## ADDED Requirements

### Requirement: Painel informa o contexto acadêmico com dados simulados
O painel de confiabilidade DEVE (MUST) informar visivelmente que o ambiente acadêmico utiliza dados simulados. O painel DEVE (MUST) identificar os Totens existentes 1 e 2 como alvos do histórico fictício, sem renomear cadastros. A identificação NÃO DEVE (MUST NOT) alterar silenciosamente filtros, autorização, inclusão nos agregados ou fórmulas.

#### Scenario: Rede inclui o lote de demonstração
- **WHEN** um perfil operacional consulta a rede com fatos fictícios persistidos
- **THEN** o painel informa o contexto simulado e mantém o recorte global escolhido

#### Scenario: Usuário seleciona um Totem do histórico fictício
- **WHEN** o filtro é aplicado explicitamente
- **THEN** são apresentados os resultados normais desse recorte histórico, preservando o cadastro e sem inferir vínculo histórico de Loja

### Requirement: Série fictícia mantém leitura clara e integridade dos valores
A série diária de MTTD e MTTR DEVE (MUST) manter datas, unidades, legendas textuais, distinção visual entre métricas e consulta do valor de cada ponto. A apresentação DEVE (MUST) preservar os valores Xano, as lacunas e as médias do período, sem inventar eventos ou interpolar dias ausentes para fins estéticos. O atalho Hoje DEVE (MUST) preservar sua visão horária de disponibilidade.

#### Scenario: Intervalo completo do lote é selecionado
- **WHEN** o Xano devolve os pontos diários do histórico sintético
- **THEN** o gráfico permite distinguir detecção de recuperação e consultar data, métrica e valor com unidade

#### Scenario: Hoje ou dia sem evento é consultado
- **WHEN** não há evento elegível para uma média ou o usuário seleciona Hoje
- **THEN** a interface mantém a ausência de ponto ou a visão horária correspondente, sem fabricar uma curva de MTTD/MTTR para preencher espaço
