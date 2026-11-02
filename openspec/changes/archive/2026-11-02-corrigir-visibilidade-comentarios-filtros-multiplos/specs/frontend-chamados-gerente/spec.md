# Spec Delta

## ADDED Requirements

### Requirement: Lista do Gerente usa multisseleção somente nos filtros existentes elegíveis
Na lista do Gerente, somente Status e Totem DEVEM (MUST) usar dropdown com indicador por opção selecionada e aceitar múltiplos valores. Marcar ou desmarcar opções NÃO DEVE (MUST NOT) aplicar a consulta antes de `Aplicar`. Número e períodos preservam seus controles, e nenhum filtro de Loja, Responsável ou Prioridade deve ser criado por esta mudança.

#### Scenario: Gerente combina Status e Totens
- **WHEN** o Gerente seleciona vários Status e Totens e aciona Aplicar
- **THEN** a lista apresenta a interseção entre os dois filtros dentro da Loja derivada da sessão

#### Scenario: Dropdown conserva seleções anteriores
- **WHEN** o Gerente abre novamente um dropdown e marca outra opção
- **THEN** as opções anteriormente marcadas continuam selecionadas até serem desmarcadas ou os filtros serem limpos

#### Scenario: Perfil permanece sem novos filtros
- **WHEN** o Gerente visualiza o painel de filtros após a mudança
- **THEN** Loja, Responsável e Prioridade continuam ausentes e o escopo permanece restrito à própria Loja

#### Scenario: Ações e demais critérios permanecem
- **WHEN** o Gerente aplica ou limpa filtros múltiplos junto de número ou períodos
- **THEN** Aplicar, Limpar, ordenação, número e períodos mantêm o comportamento vigente
