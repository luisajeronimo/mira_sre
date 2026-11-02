# Spec Delta

## ADDED Requirements

### Requirement: Visibilidade de comentário não define autorização do chamado
Público/Interno DEVE (MUST) classificar somente comentários. O acesso do Gerente ao chamado e ao status atual DEVE (MUST) continuar derivado da sessão e da Loja persistida. O contrato público de comentários DEVE (MUST) retornar somente interações de comentário explicitamente públicas, sem inferir que evento operacional sem visibilidade seja público ou privado.

#### Scenario: Gerente consulta status atual
- **WHEN** o Gerente autorizado abre chamado de sua Loja após alteração operacional de Status
- **THEN** o detalhe apresenta o Status atual persistido independentemente da visibilidade dos comentários associados

#### Scenario: Comentário interno permanece protegido
- **WHEN** chamado autorizado possui comentário Interno e eventos operacionais
- **THEN** a consulta pública não retorna o comentário Interno nem usa os eventos para contornar essa restrição

#### Scenario: Evento operacional não é comentário privado
- **WHEN** evento operacional novo ou histórico não possui classificação funcional de visibilidade
- **THEN** o contrato de comentários não o retorna nem o classifica como comentário Público ou Interno

#### Scenario: Escopo da change no histórico do Gerente
- **WHEN** o Gerente consulta o acompanhamento autorizado
- **THEN** permanece com o detalhe atual e os comentários públicos vigentes, sem receber por esta change a timeline operacional global dos perfis internos
