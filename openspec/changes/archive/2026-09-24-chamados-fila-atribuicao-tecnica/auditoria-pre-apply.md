# Auditoria pré-Apply — fila e atribuição técnica

Data da auditoria: 2026-09-20

## Contexto e ponto de recuperação

Os arquivos de contexto exigidos pelo `AGENTS.md` foram lidos antes do Apply: `AGENTS.md`, `docs/project-overview.md`, `docs/domain-model.md`, `openspec/config.yaml` e as cinco specs consolidadas vigentes. A change ativa é `chamados-fila-atribuicao-tecnica`; as changes em `openspec/changes/archive/` foram tratadas apenas como histórico.

O workspace local já continha alterações da change anterior antes deste Apply. Elas foram preservadas e não foram revertidas. O estado de referência dos arquivos de contexto no início desta auditoria foi registrado por hash SHA-256:

| Arquivo | SHA-256 |
|---|---|
| `AGENTS.md` | `4908e5cc6d94466d0dd340c32fd97e29a3e55abd96f177040177d33003366d50` |
| `docs/project-overview.md` | `ea5c4a5a90b6c67a7d91a2531265f7f5fde118c9180a87ccd76521552b53885e` |
| `docs/domain-model.md` | `7e5ec88c6c54491ed21fcbd9a36e6386b00d184f39715ed68e483c7dabe08bce` |
| `openspec/config.yaml` | `1511188fb4c80f1d264ab84e3a7c3cb1a05a9f33b4d1ca8e55b3dd1fba0335b2` |

Não foi criado snapshot remoto de registros: não há nesta sessão uma credencial de consulta de dados que possa ser usada sem expor segredo ou alterar o workspace. A tarefa 1.3 permanece pendente; nenhum registro remoto foi inferido, alterado ou excluído.

Não haverá backfill de `atribuido_em`, limpeza, exclusão ou alteração de chamados legados. O rollback operacional deve preservar os valores existentes de `tecnico_id` e todos os chamados já persistidos.

## Matriz de consumidores locais

| Campo | Consumidores atuais identificados | Observação para a change |
|---|---|---|
| `chamados.tecnico_id` | `xano/table/chamados.xs`; funções `service_desk/abrir_chamado_manual.xs`, `listar_chamados_gerente.xs` e `obter_chamado_gerente.xs`; APIs genéricas de consulta; `app/services/service_desk.py`; `app/states/chamados.py`; DTOs/testes de abertura e listagem | A abertura manual e automática gravam nulo; consultas do Gerente preservam o técnico atual. A fila técnica adicionará consultas e assunção sem reabrir CRUD genérico. |
| `chamados.status` | schema; abertura manual/automática; heartbeat (`verificar_falhas_GET.xs`); listagem/detalhe do Gerente; cliente e State Reflex; testes de heartbeat e Service Desk | A fila filtra `Novo`; heartbeat e ciclo de status permanecem fora do escopo. |
| `chamados.criado_em` | abertura manual/automática; DTOs do Gerente; listagem/detalhe e testes | Deve continuar sendo somente leitura na fila e no detalhe técnico. |
| `chamados.origem` | schema; abertura manual/automática; DTOs e testes do Gerente; heartbeat | Valores `manual` e `automatico` devem ser preservados para compatibilidade. |
| `chamados.sla_horas_aplicado` | abertura manual/automática; DTOs e testes de criação/listagem/detalhe; heartbeat | Snapshot somente leitura; sem alteração de SLA nesta change. |
| `chamados.atribuido_em` | Nenhum consumidor atual; campo ainda não existe no schema | Será adicionado de forma opcional. Somente a assunção Xano poderá preenchê-lo; registros existentes permanecerão nulos. |

Consumidores fora do escopo confirmados: Simulator apenas envia telemetria; Fiscal apenas dispara/consulta heartbeat; nenhum deles consome ou deve passar a consumir atribuição técnica.

## Validação do mecanismo de atomicidade

O Xano Developer MCP (documentação 2.7.1) documenta `timestamp?`, `db.transaction` e uma forma conceitual de `isolation = "serializable"`. A validação sintática no parser disponível produziu o seguinte resultado:

- `timestamp atribuido_em?` foi aceito pelo validador;
- `db.transaction { stack { ... } }` foi aceito;
- `db.transaction { isolation = "serializable" stack { ... } }` foi rejeitado: o parser esperava `stack` imediatamente após a abertura;
- colocar `isolation` após `stack` também foi rejeitado;
- `util.set_header` com `HTTP/1.1 409 Conflict` foi aceito;
- a validação é somente sintática e não comprova comportamento concorrente em runtime.

Conclusão: não se deve implementar assumindo a sintaxe de isolamento serializável da documentação. A validação adicional aceitou `db.direct_query` com SQL parametrizado, `UPDATE ... WHERE id = ? AND status = 'Novo' AND tecnico_id IS NULL RETURNING id` e `response_type = "list"`. Esse é o mecanismo condicional escolhido para a assunção: a operação fica restrita ao predicado elegível e o tamanho do retorno indica o vencedor; a releitura posterior classifica idempotência, conflito ou status inelegível. A validação permanece sintática e não substitui teste de runtime concorrente. Nenhuma regra de heartbeat ou dado remoto foi tocada nesta auditoria.

## Revisão arquitetural Free posterior

Após a auditoria, foi confirmada a restrição de que o workspace permanece no plano Free e não pode habilitar `Allow Direct Query`, usar Direct Database Access ou depender de `db.direct_query`. A conclusão acima fica registrada como histórico da decisão anterior e foi supersedida antes da implementação final.

A implementação revisada utiliza somente `db.get`, validações, `db.edit` e `db.transaction { stack { ... } }`, sem parâmetro de isolamento que o parser local rejeita. O fluxo relê o chamado antes da edição, edita apenas quando o status continua `Novo` e o Técnico permanece ausente (`null` ou `0`), relê após a edição e classifica conflito observável como HTTP 409. O plano Free não fornece evidência suficiente de compare-and-set ou isolamento forte para declarar garantia matemática de um único vencedor em simultaneidade exata; essa limitação foi incorporada ao design, à especificação e às tarefas.

## Inventário remoto

O inventário de chamados com `status`, `tecnico_id` e campos novos nulos não foi executado: as ferramentas disponíveis nesta sessão não fornecem consulta autenticada de registros e o arquivo `.env` não foi lido nem exposto. `xano workspace list`, se usado, não substitui inventário de dados. A tarefa 1.3 não está concluída.

## Dry-run do Apply Xano

Executado em 2026-09-20 com `xano workspace push --dry-run -d xano -w 152692 -b v1`. O preview não aplicou alterações e retornou somente:

- `UPDATE table chamados`;
- `ADD_FIELD table chamados` (`atribuido_em`);
- criação das funções `service_desk/assumir_chamado_tecnico`, `construir_dto_chamado_tecnico`, `listar_chamados_tecnico` e `obter_chamado_tecnico`;
- criação dos endpoints `GET /tecnico/chamados`, `GET /tecnico/chamados/{chamados_id}` e `POST /tecnico/chamados/{chamados_id}/assumir`.

O preview não listou exclusões nem recursos de heartbeat, Simulator, Fiscal, abertura manual ou grupos CRUD genéricos. O push real ficou condicionado à aprovação humana explícita; qualquer alteração posterior em XanoScript exigiria novo dry-run.

## Pós-sincronização

Em 2026-09-20, após aprovação humana, foi executado `xano workspace push -d xano -w 152692 -b v1 --force`, sem `--sync`, `--delete`, `--records` ou `--truncate`. O CLI informou `Pushed 76 documents` e sincronização de um GUID. Um novo dry-run com as mesmas fontes retornou `No changes to push`.

O validador local confirmou novamente 76 XanoScript válidos; a suíte Python (83 testes), compilação Reflex, `git diff --check` e OpenSpec strict também passaram. A consulta de registros pós-deploy e o pull remoto não puderam ser executados porque o host Xano não resolveu nesta sessão e não há `XANO_SERVICE_DESK_BASE_URL` nem credencial de sessão disponível no ambiente. Portanto, não há inventário remoto ou resultado runtime inventado; a ausência de mutação de chamados fica pendente de consulta autenticada/operacional posterior.
