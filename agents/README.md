# Agentes do projeto MIRA

Este diretório define papéis de agentes utilizados no desenvolvimento do projeto.

O OpenSpec continua sendo a fonte de verdade para planejamento, requisitos,
mudanças e estado das funcionalidades.

Os agentes não devem manter um backlog, conjunto de requisitos ou planejamento
paralelo ao OpenSpec.

## Papéis

### MIRA Reviewer

Responsável por revisar o estado do projeto, as changes OpenSpec, implementação,
testes, diffs e evidências.

O Reviewer não implementa funcionalidades.

Ele decide se o trabalho pode continuar, precisa de correção ou exige uma decisão humana.

Instruções:
`agents/mira-reviewer.md`

### MIRA Implementer

Responsável por executar o trabalho aprovado na change OpenSpec ativa.

Ele não deve ampliar o escopo nem tomar decisões de negócio não aprovadas.

Instruções:
`agents/mira-implementer.md`

## Fluxo

O fluxo padrão é:

Reviewer
→ Implementer
→ Reviewer
→ Implementer
→ ...
→ Gate humano
→ Archive

O humano deve ser envolvido principalmente quando houver:

- mudança de regra de negócio;
- decisão arquitetural relevante;
- limitação nova que precise ser aceita;
- recurso pago ou externo;
- operação destrutiva;
- push remoto relevante;
- archive.