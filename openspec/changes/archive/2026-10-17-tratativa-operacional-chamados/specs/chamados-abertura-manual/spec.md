# Delta: chamados-abertura-manual

## MODIFIED Requirements

### Requirement: SLA da categoria possui representação numérica segura
Durante a tratativa operacional, troca efetiva de Categoria DEVE (MUST) atualizar `sla_horas_aplicado` para o SLA da Categoria resultante sem reiniciar a referência temporal original. A alteração do SLA cadastral sem troca de Categoria no chamado não o modifica. Esta change preserva a representação de SLA já consolidada e não introduz migração de tipo, conversão textual ou auditoria global de consumidores.

#### Scenario: Consumidores do SLA auditados antes da mudança de tipo
- **WHEN** a implementação prepara a alteração de `categorias_servico.sla_horas` de texto para decimal
- **THEN** todos os usos existentes em XanoScript, Python e contratos locais relevantes estão inventariados, classificados quanto à compatibilidade e cobertos por adaptação ou verificação antes de a alteração ser aplicada

#### Scenario: Consumidor incompatível identificado
- **WHEN** a auditoria encontra um consumidor que depende da representação textual e ainda não possui adaptação validada
- **THEN** a mudança de tipo permanece bloqueada sem alterar dados ou contratos remotos

#### Scenario: Valor textual inequivocamente numérico
- **WHEN** uma categoria existente possui `sla_horas` textual cuja conversão preserva exatamente seu valor numérico
- **THEN** a migração converte o valor para a representação numérica aprovada sem atribuir outro SLA

#### Scenario: Valor incompatível
- **WHEN** a auditoria encontra `sla_horas` vazio, não numérico ou ambíguo em uma categoria que será usada na abertura manual ou pelo heartbeat
- **THEN** a migração ou ativação é interrompida para correção explícita, sem escolher um SLA padrão

#### Scenario: Alteração posterior da categoria
- **WHEN** a Categoria é efetivamente alterada durante Save operacional válido
- **THEN** o `sla_horas_aplicado` passa a ser o SLA da Categoria resultante sem reiniciar a referência temporal do chamado
