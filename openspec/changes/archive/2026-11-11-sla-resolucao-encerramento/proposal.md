# Proposal

## Why

Cartão da Sprint 3 "Resolução, SLA e encerramento controlado". O domínio define as regras de contagem de SLA e o encerramento após `Resolvido` (`docs/domain-model.md` §10 e §12). A função interna de consumo já foi publicada, mas ainda não é exposta aos perfis; o encerramento por prazo ainda não possui endpoint. A decisão acadêmica atual usa um comando manual de disparo único.

Já existem e são preservados: bloqueio de edição funcional em `Encerrado` e `Cancelado` pelo Save; comentário público obrigatório para `Resolvido`, `Aguardando Solicitante` e `Cancelado`; telemetria que não resolve nem encerra chamado (`monitoramento-disponibilidade-totens`); `alteracao_chamado` com o par de status a cada mudança pelo Save, base do histórico projetado (H-1).

## What Changes

- Nova capability `sla-encerramento-chamados`:
  - **consumo de SLA** em tempo corrido, calculado no Xano a partir de `criado_em` e da linha do tempo de status (`alteracao_chamado`), contando os estados de trabalho e espera, parando em `Resolvido`, `Encerrado` e `Cancelado`, e retomando o saldo quando o chamado sai de `Resolvido`, inclusive por `Solução Rejeitada`;
  - chamado cuja linha do tempo não reconstrói o status atual é **não calculável**, sem estimativa;
  - **encerramento sob comando manual** de chamado `Resolvido` há 72 horas corridas sem rejeição, somente quando a entrada em `Resolvido` foi registrada após o início de vigência do encerramento; elegibilidade decidida e revalidada no Xano; comando `make encerrar-resolvidos` que dispara uma única verificação por API, sem agendamento; comentário público de sistema; autoria `Sistema`; proteção contra duplicidade.
- Nenhum dado histórico é reescrito; nenhum campo agregado de SLA é persistido.

## Capabilities

### New Capabilities

- `sla-encerramento-chamados`: consumo de SLA por estados e encerramento controlado por comando manual.

### Modified Capabilities

- `chamados-acompanhamento-gerente`: comentário público do encerramento sob comando apresenta `autor.nome = "Sistema"`, sem mudar a projeção segura dos demais comentários.

A DE-8 (2026-11-08) define a exibição de SLA por perfil (design D5). Os contratos e os detalhes de Gerente, Técnico e Administrador foram implementados; indicadores do Gerente e da Diretoria foram dispensados deste Apply pela responsável em 11/11/2026 e não estão implementados.

## Decisões aprovadas (2026-11-04)

| ID | Decisão | Efeito |
|---|---|---|
| DS-1 | SLA em tempo corrido | Sem calendário de expediente; D2 do design |
| DE-1 | Encerramento após 72 horas corridas da entrada em `Resolvido` | Elegibilidade `agora ≥ t_r + 72 h` |
| DE-2 | Chamados já `Resolvido` na implantação não são encerrados em massa | Regra de vigência (design D3): somente entradas em `Resolvido` registradas após o início de vigência são candidatas |
| DE-3 | O encerramento automático gera comentário público de sistema | Terceira escrita do encerramento; cumpre "toda alteração de status exige comentário" |
| DR2-0, DR2-1, DR2-2 | Rejeição na Sprint 3 pelo Gerente da Loja, com destino `Solução Rejeitada` | Fonte da retomada de SLA a partir de `Resolvido` (`rejeicao-solucao-gerente`) |
| DT-1 | Prova E0.3 obrigatória antes de novas escritas que dependam de atomicidade | O encerramento (três escritas) fica bloqueado até a prova; o cálculo de consumo é somente leitura e não depende dela |

## Dependências

- `rejeicao-solucao-gerente`: operação que produz `Resolvido` → `Solução Rejeitada`.
- `indicadores-governanca-formulas`: o indicador de SLA usa o consumo aqui definido.
- H-1 (`acompanhamento-solicitante-historico-status`): mesma leitura de `alteracao_chamado`.
- Prova E0.3: datasource próprio de teste no workspace `152692`, branch `v1`, autorizado em 2026-11-08 como alternativa ao workspace separado. Registros separados; schema e recursos publicados compartilhados. Prova e aprovação do relatório ainda pendentes.
- Referências externas "4", "5" e "D3" do planejamento: a responsável confirmou em 11/11/2026 que não há fonte disponível. Seu significado permanece desconhecido; elas não fundamentam requisito, decisão técnica nem bloqueio adicional nesta change. Uma futura fonte que altere o escopo exige revisão própria.

## Decisões complementares aprovadas em 2026-11-08

| ID | Decisão | Impacto |
|---|---|---|
| DE-3a | Comentário público: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução." | Conteúdo visível ao Gerente |
| DE-3b | O DTO público mostra autor `Sistema` para o comentário gerado pelo encerramento | Contrato público de comentários |
| DE-4 | Comando Python executado uma vez via `make encerrar-resolvidos`; chama endpoint próprio e não decide elegibilidade | Sem processo residente nem agendamento |
| DE-5 | Não se aplica frequência: o comando é disparado manualmente quando se deseja verificar e encerrar elegíveis | Um chamado pode permanecer `Resolvido` depois de 72 h até a próxima execução manual |
| DE-7 | Preservar o encerramento manual pelo Save a partir de estados não terminais | Ciclo de vida existente |
| DE-8 | Técnico na fila e no detalhe; Gerente nos chamados da própria Loja e em indicadores gerenciais; Diretoria em indicadores consolidados; Administrador em visão global; solicitante sem SLA nesta versão | Contratos e telas |
| DE-9 | Constante versionada na função Xano, fixada na publicação do encerramento | Configuração e auditoria |

`Aguardando Terceiro` não integra a lista canônica vigente; não há decisão nem trabalho adicional sobre esse status nesta change. A regra geral de linha do tempo inconsistente permanece.

## Impact

- Xano: função de cálculo de consumo (somente leitura); função e endpoint de encerramento autenticado por credencial de automação; nenhuma alteração no Save, schema ou dados históricos.
- Python e Makefile: comando de disparo único (DE-4), sem loop nem scheduler.
- Reflex: exibição do consumo nos detalhes de Gerente, Técnico e Administrador conforme DE-8; sem dashboards de indicadores.

## Fora do escopo

- Rejeição de solução (operação em `rejeicao-solucao-gerente`); aceitação explícita pelo solicitante (permanece somente leitura por DR2-1); dashboards; calendário de dias úteis; reabertura de `Encerrado` ou `Cancelado`.
