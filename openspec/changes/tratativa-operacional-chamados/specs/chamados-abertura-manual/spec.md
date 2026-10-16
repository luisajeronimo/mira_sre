# Delta: chamados-abertura-manual

## MODIFIED Requirements

### Requirement: SLA da categoria possui representação numérica segura
O sistema DEVE (MUST) representar `categorias_servico.sla_horas` e `chamados.sla_horas_aplicado` em formato numérico compatível entre si. Antes da mudança de tipo, a implementação DEVE (MUST) identificar e verificar todos os consumidores existentes de `categorias_servico.sla_horas`, incluindo XanoScript, Python e demais contratos locais relevantes, e definir a adaptação ou a evidência de compatibilidade de cada consumidor. A migração somente DEVE (MUST) converter valores textuais existentes cuja equivalência numérica seja inequívoca e DEVE (MUST) interromper a ativação dos novos contratos diante de consumidor incompatível ou de valor vazio, não numérico ou ambíguo em categoria que precise participar de um novo fluxo. Durante a tratativa operacional, troca efetiva de Categoria DEVE (MUST) atualizar `sla_horas_aplicado` para o SLA da Categoria resultante sem reiniciar a referência temporal original; alteração do SLA cadastral sem troca de Categoria no chamado não o modifica.

#### Scenario: Consumidores do SLA auditados antes da mudança de tipo
- **WHEN** a implementação evolui a representação de SLA usada por Categoria e chamado
- **THEN** os consumidores XanoScript, Python e contratos locais relevantes são auditados e adaptados ou validados antes da ativação

#### Scenario: Consumidor incompatível identificado
- **WHEN** a auditoria encontra consumidor incompatível com a representação numérica
- **THEN** a ativação permanece bloqueada sem alterar dados ou contratos remotos

#### Scenario: Valor textual inequivocamente numérico
- **WHEN** Categoria existente possui SLA textual cuja conversão preserva exatamente o valor numérico
- **THEN** a migração aprovada pode convertê-lo sem atribuir outro SLA

#### Scenario: Valor incompatível
- **WHEN** a auditoria encontra `sla_horas` vazio, não numérico ou ambíguo em Categoria que precise participar de fluxo novo
- **THEN** a migração ou ativação é interrompida para correção explícita, sem escolher SLA padrão

#### Scenario: Alteração posterior da categoria
- **WHEN** a Categoria é efetivamente alterada durante Save operacional válido
- **THEN** o `sla_horas_aplicado` passa a ser o SLA da Categoria resultante sem reiniciar a referência temporal do chamado
