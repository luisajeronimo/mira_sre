## Why

O MIRA já registra chamados manuais e automáticos e permite que o Gerente os consulte, mas ainda não oferece uma fila funcional para o Técnico. Sem uma consulta técnica filtrada e uma assunção protegida pelo Xano, dois Técnicos podem disputar o mesmo chamado ou depender de mutações genéricas que permanecem proibidas.

## What Changes

- Criar a fila técnica no grupo existente `MIRA Service Desk`, exclusiva do perfil `tecnico`.
- Oferecer as visões `nao_atribuidos` e `atribuidos_a_mim`, ambas filtradas no Xano.
- Considerar elegíveis somente chamados com `status = "Novo"`.
- Definir “não atribuído” como `tecnico_id` ausente (`null` ou a representação legada `0`) e “atribuído a mim” como `tecnico_id = $auth.id`.
- Adicionar `atribuido_em` ao schema de `chamados`, sem backfill de registros legados.
- Criar consulta de detalhe técnico somente leitura.
- Criar assunção por autoatribuição do Técnico autenticado, sem aceitar `tecnico_id`, `status` ou `atribuido_em` do cliente.
- Implementar assunção com as operações gratuitas suportadas pelo Xano (`db.get`, validações, `db.edit` e `db.transaction`), com HTTP 409 para conflitos observáveis e sucesso idempotente quando o mesmo Técnico repetir a operação.
- Documentar que o plano Free não fornece evidência de compare-and-set ou isolamento forte suficiente para garantir matematicamente um único vencedor em uma simultaneidade exata; não usar `db.direct_query`, Direct Database Access ou upgrade de plano.
- Classificar a assunção como HTTP 422 para status nulo ou diferente de `Novo`, sucesso para `Novo` sem Técnico, sucesso idempotente para `Novo` já atribuído ao Técnico autenticado e HTTP 409 para `Novo` atribuído a outro Técnico.
- Manter o status `Novo` após a assunção; não iniciar tratativa formal.
- Transformar `/tecnico` em fila Reflex e criar `/tecnico/chamados/{chamado_id}`.
- Ordenar as duas visões por `id desc`, sem pesos de prioridade, ordenação por SLA ou paginação.
- Preservar compatibilidade com chamados manuais, automáticos e legados sem inferência ou limpeza de dados.
- Manter fora do escopo status adicionais, reatribuição, liberação, cancelamento, work logs, diagnóstico, solução, resolução, dashboards, indicadores, Simulator, Fiscal e heartbeat.

## Capabilities

### New Capabilities

- `chamados-fila-atribuicao-tecnica`: fila técnica, consulta de chamados, detalhe e assunção pelo Técnico autenticado.

### Modified Capabilities

- `frontend-sessao-navegacao`: o destino inicial do perfil Técnico deixa de ser neutro e passa a apresentar a fila técnica desta change, preservando a proteção de rota e a autorização no Xano.

## Impact

- **Xano:** evolução aditiva da tabela `chamados`, novos contratos no grupo `MIRA Service Desk`, DTOs técnicos, filtro de visão, autorização de Técnico e operação de assunção baseada em recursos do plano Free.
- **Reflex:** novos modelos e métodos no cliente Service Desk, State técnico, fila, detalhe, ação de assunção e tratamento de conflito.
- **Interface:** exibir `Assumir` quando o DTO indicar `status = "Novo"` e Técnico atual ausente; `atribuido_em` será somente informação histórica.
- **Testes:** XanoScript/harness para autorização, filtros, idempotência, conflitos observáveis, limitação de concorrência, legados e classificação HTTP; testes Python, rotas e compilação Reflex.
- **Compatibilidade:** não altera abertura manual do Gerente, heartbeat, Simulator, Fiscal, CRUDs genéricos ou ciclo de tratativa.
