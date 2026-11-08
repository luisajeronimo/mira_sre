# Proposal

## Why

Cartão da Sprint 3 "Resolução, SLA e encerramento controlado" (estado informado: inexistente). O domínio define as regras de contagem de SLA e o encerramento automático em `Resolvido` (`docs/domain-model.md` §10 e §12), mas nada disso está implementado: não há cálculo de consumo, campos de resolução ou encerramento, nem automação de encerramento.

Já existem e são preservados: bloqueio de edição funcional em `Encerrado` e `Cancelado` pelo Save; comentário público obrigatório para `Resolvido`, `Aguardando Solicitante` e `Cancelado`; telemetria que não resolve nem encerra chamado (`monitoramento-disponibilidade-totens`); `alteracao_chamado` com o par de status a cada mudança pelo Save, base do histórico projetado (H-1).

## What Changes

- Nova capability `sla-encerramento-chamados`:
  - **consumo de SLA** em tempo corrido, calculado no Xano a partir de `criado_em` e da linha do tempo de status (`alteracao_chamado`), contando os estados de trabalho e espera, parando em `Resolvido`, `Encerrado` e `Cancelado`, e retomando o saldo quando o chamado sai de `Resolvido`, inclusive por `Solução Rejeitada`;
  - chamado cuja linha do tempo não reconstrói o status atual é **não calculável**, sem estimativa;
  - **encerramento automático** de chamado `Resolvido` há 72 horas corridas sem rejeição, somente quando a entrada em `Resolvido` foi registrada após o início de vigência do encerramento; elegibilidade decidida e revalidada no Xano; job que apenas dispara a verificação; comentário público de sistema; autoria `Sistema`; proteção contra duplicidade.
- Nenhum dado histórico é reescrito; nenhum campo agregado de SLA é persistido.

## Capabilities

### New Capabilities

- `sla-encerramento-chamados`: consumo de SLA por estados e encerramento automático controlado.

### Modified Capabilities

Nenhuma nesta proposta. A exibição do consumo de SLA em telas ou DTOs existentes depende de DE-8.

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
- Prova E0.3 em ambiente isolado: nenhum ambiente isolado autorizado.
- Dependências "4", "5" e "D3" do planejamento: sem origem documental no repositório; registradas como dependências externas não esclarecidas.

## Decisões pendentes

| ID | Pergunta | Alternativas | Impacto |
|---|---|---|---|
| DE-3a | Texto do comentário público de sistema | Proposta: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução." | Conteúdo visível ao Gerente |
| DE-3b | Como o autor do comentário de sistema aparece | Manter o DTO público vigente (`autor = null`, apresentado como autor não informado); ampliar o DTO de comentário para identificar `Sistema` (MODIFIED de `chamados-acompanhamento-gerente`) | Contrato público de comentários |
| DE-4 | Mecanismo do job | Script Python no padrão do Fiscal, com credencial própria (recomendado); ampliar o Fiscal; tarefa agendada do Xano (disponibilidade no Free não confirmada) | Arquitetura, credenciais, `.env.example` |
| DE-5 | Frequência do job | Ex.: 15 min (atraso máximo de 15 min após as 72 h); 1 h | Pontualidade do encerramento |
| DE-6 | `Aguardando Terceiro` (legado) conta SLA? | Conta como espera; manter não calculável (comportamento da spec até decidir) | Chamados legados |
| DE-7 | Encerramento manual pelo Save a partir de qualquer estado não terminal permanece? | Manter (atual); restringir | Ciclo de vida |
| DE-8 | Onde o consumo de SLA é exposto? | Somente no futuro dashboard; detalhe técnico; detalhe do Gerente | Contratos e telas |
| DE-9 | Onde fica o início de vigência do encerramento | Variável de ambiente do Xano (se disponível no Free, a validar no MCP); constante versionada na função, definida no Apply | Configuração e auditoria |

## Impact

- Xano: função de cálculo de consumo (somente leitura); função e endpoint de encerramento autenticado por credencial de automação; nenhuma alteração no Save, schema ou dados históricos.
- Python: script do job (conforme DE-4).
- Reflex: somente se DE-8 incluir telas.

## Fora do escopo

- Rejeição de solução (operação em `rejeicao-solucao-gerente`); aceitação explícita pelo solicitante (permanece somente leitura por DR2-1); dashboards; calendário de dias úteis; reabertura de `Encerrado` ou `Cancelado`.
