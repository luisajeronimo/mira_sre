# Design

## Context

- `chamados`: `criado_em` (instante funcional de abertura, igual a `ultima_atualizacao_em` na criação), `status`, `sla_horas_aplicado` (snapshot da Categoria; troca de Categoria atualiza o valor sem reiniciar a referência), `ultima_atualizacao_em`.
- Chamados manuais e automáticos são criados em `Novo`.
- `alteracao_chamado`: um registro por Save efetivo; com mudança de status, `alteracoes.status = {anterior, resultante}` e `criado_em` do instante do Save. Existe desde a implantação do Save operacional (`2026-10-17-tratativa-operacional-chamados`).
- Não há `resolvido_em`, `encerrado_em`, consumo persistido nem job de encerramento. O Fiscal é a única automação de fiscalização (heartbeat) e usa credencial própria.

## Goals / Non-Goals

**Goals:** SLA calculável e auditável a partir de fatos persistidos; encerramento automático decidido pelo Xano, idempotente e protegido contra rejeição concorrente.

**Non-Goals:** persistir consumo; alterar o Save; reescrever histórico; calendário de dias úteis.

## Decisions

### D1. Linha do tempo de status

Para o chamado `c`: `T_c = [(criado_em, "Novo")]` seguido, em ordem de `criado_em` e `id`, dos pares `(criado_em, resultante)` de cada `alteracao_chamado` com `alteracoes.status` válido (mesmo critério de H-1).

`T_c` é **consistente** se o `anterior` do primeiro par é `Novo`, o `anterior` de cada par seguinte é o `resultante` do anterior e o último `resultante` (ou `Novo`, sem pares) é igual a `chamados.status`. Inconsistente ⇒ SLA **não calculável**, reportado com motivo; nenhum intervalo é estimado.

### D2. Consumo de SLA

Estados que contam: `Novo`, `Em Atendimento`, `Aguardando Solicitante`, `Aguardando Mudança`, `Solução Rejeitada`. Status fora da lista canônica, como o legado `Aguardando Terceiro`, tornam o SLA não calculável até a decisão DE-6. Estado de pausa: `Resolvido`. Estados finais: `Encerrado`, `Cancelado`.

```
C_c(t) = Σ  | [s_j, min(s_{j+1}, t)) |   para cada segmento j de T_c cujo estado conta SLA
U_c(t) = C_c(t) / (sla_horas_aplicado × 3.600.000 ms)
```

- **Início:** `criado_em`.
- **Pausa:** instante de entrada em `Resolvido`.
- **Retomada:** instante de saída de `Resolvido` para estado que conta, inclusive `Solução Rejeitada`; o saldo acumulado é preservado porque a soma apenas ignora o segmento pausado.
- **Múltiplas pausas:** cada segmento em `Resolvido` é ignorado individualmente.
- **Fim:** entrada em `Encerrado` ou `Cancelado`; `t` posterior não altera `C`.
- **Tempo:** corrido (DS-1 aprovada); sem calendário de expediente ou feriados.
- **Troca de Categoria:** `S` é o `sla_horas_aplicado` vigente; a referência inicial permanece `criado_em`.

**Exemplo (sintético):** `S = 4 h`; `Novo` 08:00; `Em Atendimento` 08:30; `Resolvido` 10:00; `Solução Rejeitada` 13:00; `Em Atendimento` 14:00; `Resolvido` 15:00. `C = 2 h + 2 h = 4 h`, `U = 100%`. O intervalo 10:00–13:00 não conta.

### D3. Encerramento automático

Função `service_desk/encerrar_chamados_resolvidos_elegiveis` e endpoint de automação (nome final no Apply):

1. Autenticação por credencial de automação (DE-4), no padrão do Fiscal; nenhum perfil humano a executa.
2. Candidatos: `status == "Resolvido"`.
3. Para cada candidato: `t_r` = `criado_em` da última transição com `resultante = "Resolvido"` em `T_c` consistente. Sem `t_r` ⇒ não elegível (nenhum timestamp é inferido).
4. **Vigência (DE-2):** elegível somente se `t_r ≥ T_v`, onde `T_v` é o instante de início de vigência do encerramento automático, definido explicitamente na publicação aprovada e registrado na evidência de publicação (armazenamento: DE-9). `T_v` nunca é derivado dos dados. Chamados com `t_r < T_v`, inclusive os que já estavam `Resolvido` na implantação, nunca são candidatos automáticos e continuam sujeitos ao encerramento manual pelo Save; se forem rejeitados e resolvidos de novo, a nova entrada em `Resolvido` é posterior a `T_v` e passa a valer.
5. **Prazo (DE-1):** elegível se `agora ≥ t_r + 72 h` (259.200.000 ms), em tempo corrido.
6. Dentro de `db.transaction`, por chamado: releitura; revalidação de `status == "Resolvido"` e de `ultima_atualizacao_em` igual ao lido em 2; comentário público de sistema (DE-3; texto DE-3a; `usuarios_id` nulo); `db.patch` com `status = "Encerrado"` e `ultima_atualizacao_em = agora`; `alteracao_chamado` com `Resolvido → Encerrado`, `comentario_interacao_id` e `usuarios_id` nulo (autor `Sistema`). Três escritas: bloqueadas até a prova E0.3 (DT-1).
7. Resposta: contagens de avaliados, encerrados, fora da vigência, prazo não vencido, não calculáveis e conflitos; nenhum dado pessoal.

**Concorrência:** rejeição ou Save confirmados antes da revalidação mudam `status` ou `ultima_atualizacao_em` e impedem o encerramento; rejeição posterior ao encerramento recebe conflito (`Encerrado` é terminal). Sem isolamento comprovado no Free, a janela entre revalidação e escrita permanece e é registrada.

**Duplicidade e falhas:** a revalidação torna a operação idempotente; execuções perdidas são recuperadas na próxima execução, que encerra no instante em que roda (o SLA não é afetado, pois `Resolvido` já está pausado). O job não decide elegibilidade, não envia lista de chamados e não altera chamados fora da resposta do Xano.

**Rejeição no limite do prazo:** vale a operação confirmada primeiro pelo Xano; a outra recebe conflito ou é pulada.

### D4. Job

Conforme DE-4 (recomendado: script Python separado, no padrão do Fiscal: chama o endpoint, aguarda a resposta, registra contagens sem dados sensíveis e espera o intervalo DE-5). A disponibilidade de tarefas agendadas do Xano no plano Free não foi confirmada na documentação oficial consultada.

### D5. Exposição do consumo por perfil (DE-8, decidida em 2026-11-08)

Fonte única: `calcular_consumo_sla_chamado` (D1–D2). Nenhuma camada recalcula, estima ou completa valores.

| Perfil | Onde | O que |
|---|---|---|
| Técnico | Fila e detalhe | Percentual consumido, tempo restante e situação |
| Gerente | Lista e detalhe dos chamados da própria Loja histórica; indicadores gerenciais | Percentual, tempo restante, situação e alerta de proximidade ou vencimento |
| Diretoria | Indicadores consolidados e evolução por período | Agregados de cumprimento (fórmula depende de DS-2) |
| Administrador | Visão global, respeitando as permissões vigentes | Mesmos campos do Técnico |
| Solicitante | Nenhum nesta versão | Somente status; o SLA interno não é exposto |

Situação apresentada, derivada do retorno da função sem regra nova:

| Situação | Condição |
|---|---|
| Dentro do SLA | `calculavel` e `faixa = normal` |
| Próximo do vencimento | `calculavel` e `faixa` em `risco` ou `critico` (domínio §12) |
| Vencido | `calculavel` e `faixa = violado` |
| Pausado | `estado_contagem = pausada` (em `Resolvido`); a faixa no instante da pausa continua visível |
| Encerrado | `estado_contagem = encerrada` (`Encerrado` ou `Cancelado`) |
| Não calculável | `calculavel = false`; exibir o motivo, sem percentual nem prazo |

Percentual: `fracao_consumida × 100`. Tempo restante: `sla_horas_aplicado × 3 600 000 − consumo_ms`, exibido somente em contagem; valor negativo é apresentado como tempo excedido. A autorização de cada consulta permanece no Xano: o Gerente só recebe consumo de chamados autorizados pela Loja histórica; o solicitante não recebe campos de SLA.

Pendências: indicadores do Gerente e da Diretoria dependem de DS-2 e DI-1 a DI-5 (change `indicadores-governanca-formulas`); o desenho dos contratos de exposição (campos novos nos DTOs existentes ou consulta própria) é decidido no Apply desta parte, com testes.

## Risks / Trade-offs

- [Transação não comprovada] → prova E0.3 obrigatória (DT-1) para as três escritas; ambiente isolado ainda não autorizado.
- [Chamados anteriores ao Save sem linha do tempo] → não calculáveis e não elegíveis, reportados.
- [Primeiro encerramento em massa de chamados já vencidos] → impedido pela vigência `T_v` (DE-2).
- [Corrida com rejeição] → revalidação; janela residual registrada.
- [Credencial nova] → somente em `.env`; `.env.example` com placeholder após aprovação.

## Migration Plan

Decisões DE-3a, DE-3b, DE-4 a DE-9 → função de consumo com testes (sem dependência da prova) → prova E0.3 e relatório aprovado → encerramento com testes → validação MCP, dry-run e push aprovados → job Python → validação integrada. Sem schema e sem backfill. Reversão: parar o job e desativar o endpoint; encerramentos realizados permanecem registrados.
