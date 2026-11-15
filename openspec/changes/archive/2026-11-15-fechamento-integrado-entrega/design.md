# Reconciliação documental do fechamento

## Context

Ver motivação e escopo em `proposal.md`. O levantamento encontrou 24 tarefas abertas em sete changes arquivadas. Seus checkboxes registram o estado de cada entrega na época; contratos, acessos e jornadas evoluíram posteriormente. O usuário confirmou os cinco roteiros essenciais e autorizou o fechamento documental.

## Goals / Non-Goals

Relacionar cada tarefa histórica ao comportamento vigente, distinguir aceite humano de execução técnica observada e retirar estados transitórios dos dois documentos estáveis. O registro não altera requisitos, não fabrica resultados individuais e não executa testes mutáveis.

## Decisions

- Centralizar aceite, matriz de reconciliação e validações em `tasks.md` desta change. Os documentos estáveis apontam para esse registro e para as specs vigentes.
- Preservar checkboxes e evidências dos arquivos arquivados. Reclassificar a situação atual na matriz evita reescrever a história ou apresentar o lint dos arquivos antigos como aprovado.
- Distinguir três situações: fluxo vigente aceito pelo usuário; critério antigo substituído por entrega posterior; limite específico de comprovação preservado. Uma linha pode ter mais de uma situação quando a tarefa original mistura critérios.
- Registrar o aceite como confirmação humana recebida em 15/11/2026. A data da execução pelo usuário, IDs dos dados, códigos HTTP e logs não foram fornecidos e não serão inferidos.
- Não criar delta specs: o conteúdo funcional de `openspec/specs/` permanece a autoridade. O README permanece fora do diff por instrução explícita.

## Risks / Trade-offs

- Aceite geral ser interpretado como execução de todos os cenários negativos → registrar que o aceite cobre os roteiros essenciais e preservar os limites granulares documentados.
- Tarefas antigas refletirem contratos superados → vincular a matriz às entregas posteriores e às specs atuais, sem reproduzir a regra antiga como vigente.
- Lint de arquivos arquivados continuar falhando → registrar explicitamente 34/41 aprovados e sete arquivos com tarefas abertas; não alterar a configuração de validação para ocultar o resultado.
- Confundir encerramento funcional com nova publicação → separar o aceite do produto do ciclo documental desta change, sem Archive, commit ou push implícitos.
