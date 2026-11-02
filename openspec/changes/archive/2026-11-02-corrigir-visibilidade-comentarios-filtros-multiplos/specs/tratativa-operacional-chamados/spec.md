# Spec Delta

## ADDED Requirements

### Requirement: Visibilidade pertence exclusivamente a comentários
Cada comentário novo DEVE (MUST) possuir visibilidade Pública ou Interna. Eventos `atribuicao`, `reatribuicao`, `liberacao` e `alteracao_chamado` NÃO DEVEM (MUST NOT) possuir classificação de visibilidade nem badge correspondente. A autorização da timeline DEVE (MUST) ser decidida pelo contrato, perfil e chamado, sem interpretar ausência de visibilidade operacional como Público ou Interno.

#### Scenario: Novo evento operacional
- **WHEN** atribuição, reatribuição, liberação ou Save funcional cria evento automático
- **THEN** o evento é persistido e apresentado como fato do chamado sem visibilidade Público/Interno

#### Scenario: Comentário interno correlacionado
- **WHEN** um Save permitido cria comentário Interno e `alteracao_chamado` correlacionado
- **THEN** somente o comentário é identificado como Interno e o evento permanece sem badge de visibilidade

#### Scenario: Comentário público correlacionado
- **WHEN** um Save de Status cria comentário Público e `alteracao_chamado` correlacionado
- **THEN** somente o comentário é identificado como Público e o evento permanece sem badge de visibilidade

#### Scenario: Metadado legado em evento operacional
- **WHEN** evento operacional histórico possui `publica` ou `interna` armazenado
- **THEN** o sistema preserva o registro sem backfill ou exclusão, ignora esse metadado para classificação e autorização e apresenta o evento sem badge

#### Scenario: Evento e comentário permanecem fatos distintos
- **WHEN** a timeline apresenta comentário agrupado a `alteracao_chamado`
- **THEN** conteúdo, autor, instante e visibilidade vêm do comentário, enquanto diferenças e tipo vêm do evento correlacionado, sem copiar classificação entre os registros
