## Context

Ver `proposal.md` para a motivação e as delta specs para o comportamento observável. O Xano já possui as tabelas `chamados`, `categorias_servico`, `ativos_referencia`, `usuarios` e `interacoes_chamado`, mas os campos de chamado são majoritariamente opcionais, `sla_horas` é texto, não existe origem ou descrição persistida e as mutações CRUD genéricas estão corretamente bloqueadas.

O único produtor funcional de chamados é `verificar-falhas`: ele cria um registro com ativo, categoria, título, `Novo`, `Urgente` e `created_at`. As consultas genéricas atuais aplicam parte do escopo de Loja, mas não constituem um contrato estável para o frontend. O Reflex possui somente cliente de autenticação, token backend-only, guards e páginas iniciais neutras.

A mudança atravessa modelo Xano, dados existentes, criador automático, novos contratos funcionais e uma jornada Reflex. Autenticação, autorização por perfis, sessão, heartbeat e CRUDs genéricos devem preservar seus comportamentos consolidados, exceto pelo preenchimento explícito dos novos dados compartilhados na criação automática.

## Goals / Non-Goals

**Goals:**

- Introduzir os dados mínimos compartilhados que tornem chamados novos rastreáveis sem falsificar registros históricos.
- Disponibilizar uma fronteira funcional única do Service Desk para a jornada do Gerente.
- Garantir que identidade, solicitante e escopo de Loja sejam derivados e validados no Xano.
- Entregar uma jornada Reflex pequena, testável e integrada à sessão existente.
- Permitir implantação e rollback controlados diante da migração de `sla_horas`.

**Non-Goals:**

- Generalizar o grupo para Técnico ou Diretoria nesta change.
- Modelar fila, assunção, atribuição, interações, diagnóstico, solução ou resolução.
- Definir outros status, transições, calendário, vencimento, pausa ou compliance de SLA.
- Alterar a equivalência, a concorrência ou os demais critérios do heartbeat.
- Corrigir dados históricos por aproximação ou introduzir rotinas administrativas de categorias.
- Adicionar paginação, ordenação configurável ou filtros avançados à listagem inicial.

## Decisions

### 1. Evoluir o schema de forma aditiva para chamados e tipada para SLA

`chamados` receberá:

- `descricao`: texto opcional fisicamente, obrigatório no endpoint manual;
- `origem`: enum opcional com somente `manual` e `automatico`, obrigatório nos dois produtores novos;
- `sla_horas_aplicado`: decimal opcional fisicamente, obrigatório nos dois produtores novos.

`criado_em` continuará fisicamente opcional para preservar registros legados, mas será preenchido pelo backend em toda criação nova. `created_at` permanecerá privado e técnico. Os campos existentes de status, prioridade e relacionamentos continuarão fisicamente compatíveis com registros antigos; a rigidez será aplicada pelos contratos funcionais, não por uma migração destrutiva ampla.

`categorias_servico` receberá `permite_abertura_manual`, booleano com padrão `false`. `sla_horas` passará de texto opcional para decimal opcional, a mesma representação de `chamados.sla_horas_aplicado`. Decimal foi escolhido para não impor que horas sejam inteiras, uma restrição de negócio inexistente. Nenhuma faixa mínima ou máxima será criada nesta change.

Campos novos de chamado permanecerão anuláveis no schema porque torná-los obrigatórios fisicamente exigiria fabricar dados para registros antigos. Em contraposição, todos os produtores novos deverão preencher os valores aplicáveis explicitamente.

**Alternativas consideradas:**

- Tornar os campos obrigatórios no banco e preencher legados: rejeitada porque exigiria inferência histórica.
- Manter `sla_horas` como texto e copiar a string: rejeitada porque não assegura um snapshot numérico utilizável e permite valores incompatíveis.
- Alterar `prioridade` e `status` para enum nesta change: rejeitada porque ampliaria a migração e formalizaria um ciclo de vida ainda fora do escopo.

### 2. Migrar SLA e categorias em uma etapa auditável, sem classificação heurística

Antes da mudança de tipo, serão inventariados todos os consumidores existentes de `categorias_servico.sla_horas`. A busca abrangerá XanoScript, Simulator, Fiscal, Reflex, testes, scripts e demais contratos locais relevantes; cada ocorrência será classificada como leitura, escrita, serialização, validação ou documentação. A mudança permanecerá bloqueada até que cada consumidor executável esteja comprovadamente compatível com decimal ou tenha sua adaptação e regressão definidas.

Também serão inventariados por identificador os valores atuais de `categorias_servico.sla_horas`. Somente representações textuais inequivocamente numéricas serão convertidas preservando o mesmo valor. Campo vazio, unidade embutida, texto ou formato ambíguo em categoria que participará do fluxo manual ou automático impedirá a ativação até correção humana explícita.

Todas as categorias iniciarão `permite_abertura_manual = false`. Antes de qualquer classificação, será apresentada uma tabela com identificador, nome, tipo atual, SLA atual, indicação de uso pelo heartbeat e valor atual/proposto de `permite_abertura_manual`. Esse ponto é um gate humano obrigatório: o conjunto que receberá `true` será fornecido por decisão operacional explícita sobre os identificadores apresentados, nunca por nome, `tipo_itil`, descrição ou escolha automática. A categoria já usada pelo heartbeat será confirmada e mantida explicitamente com `false`. Uma categoria somente poderá ser marcada como manual quando possuir SLA numérico não nulo.

Os chamados existentes não serão atualizados com `origem`, `descricao`, `criado_em` ou `sla_horas_aplicado`. Consultas funcionais retornarão `null` para esses campos quando o chamado legado puder ser associado a uma Loja por seu ativo. Chamados sem ativo válido não poderão ser autorizados por Loja e ficarão fora desses contratos.

**Alternativas consideradas:**

- Inferir chamados automáticos pela categoria ou pelo título: rejeitada por decisão explícita e por risco de falsificar origem.
- Copiar `created_at` para `criado_em`: rejeitada porque transformaria metadado técnico em fato de negócio não comprovado.
- Habilitar categorias por convenção de nome: rejeitada; a nova propriedade booleana é a única fonte de permissão.

### 3. Criar uma fronteira funcional única chamada `mira-service-desk`

Será criado um grupo de API autenticado por `usuarios`, com canonical próprio e cinco rotas:

| Método e rota | Finalidade |
|---|---|
| `GET /gerente/ativos` | Ativos da Loja derivada do Gerente |
| `GET /gerente/categorias` | Categorias com `permite_abertura_manual = true` |
| `POST /gerente/chamados` | Abertura manual |
| `GET /gerente/chamados` | Todos os chamados vinculados à Loja |
| `GET /gerente/chamados/{chamados_id}` | Detalhe autorizado |

As rotas usarão as funções consolidadas de identidade, perfil e escopo. O grupo não será uma fachada para os CRUDs genéricos: cada endpoint selecionará inputs, joins e outputs explicitamente. Os CRUDs existentes continuarão bloqueados.

Uma única base funcional evita que o Reflex conheça os canonicals separados de ativos, categorias e chamados. Rotas prefixadas por `gerente` tornam explícito que esta primeira superfície não concede operações futuras a outros perfis.

**Alternativas consideradas:**

- Consumir diretamente os três grupos gerados a partir de tabela: rejeitada por acoplar o Reflex à organização interna e exigir múltiplas bases.
- Reabrir POST/PATCH genéricos: rejeitada porque contornaria a negação por padrão e permitiria campos controlados pelo cliente.
- Criar um endpoint agregador único para toda a página: rejeitada porque misturaria catálogos, lista e comandos com ciclos de erro diferentes.

### 4. Usar contratos explícitos e pequenos

`GET /gerente/ativos` responderá:

```json
{
  "items": [
    {
      "id": 1,
      "nome_ativo": "Totem 01",
      "tipo": "totem",
      "status_atual": "online"
    }
  ]
}
```

`GET /gerente/categorias` responderá:

```json
{
  "items": [
    {
      "id": 1,
      "nome": "Falha física",
      "tipo_itil": "incidente",
      "descricao": "...",
      "sla_horas": 8
    }
  ]
}
```

O nome externo `descricao` normaliza o campo físico atual `desc`; detalhes da tabela não vazam para o frontend. A permissão continua sendo filtrada por `permite_abertura_manual`, sem filtro por nome.

`POST /gerente/chamados` aceitará somente:

```json
{
  "ativos_referencia_id": 1,
  "categorias_servico_id": 2,
  "prioridade": "Alta",
  "titulo": "Leitor não reconhece cartão",
  "descricao": "O leitor permanece sem resposta durante as tentativas."
}
```

A resposta será HTTP 201:

```json
{
  "chamado": {
    "id": 123,
    "titulo": "Leitor não reconhece cartão",
    "descricao": "O leitor permanece sem resposta durante as tentativas.",
    "status": "Novo",
    "prioridade": "Alta",
    "origem": "manual",
    "criado_em": 1780000000000,
    "sla_horas_aplicado": 8,
    "ativo": {"id": 1, "nome_ativo": "Totem 01"},
    "categoria": {"id": 2, "nome": "Falha física"},
    "solicitante": {"id": 8, "nome": "Gerente"},
    "tecnico": null
  }
}
```

`GET /gerente/chamados` responderá `{"items": [...]}` com `id`, `titulo`, `status`, `prioridade`, `origem`, `criado_em`, `ativo` e `categoria`. Campos novos poderão ser nulos somente para legados. Não haverá paginação ou contrato de ordenação nesta primeira versão.

`GET /gerente/chamados/{chamados_id}` responderá `{"chamado": {...}}` no mesmo formato funcional da criação, admitindo nulos legados. Credenciais, senha, token e `created_at` não integrarão os DTOs.

Os contratos usarão:

- 401 para token ausente, inválido ou expirado;
- 403 para perfil inadequado, Gerente sem Loja ou recurso confirmado fora da Loja;
- 404 para identificador inexistente;
- 422 para corpo ausente/inválido, prioridade fora do vocabulário ou categoria existente não permitida/incompatível;
- 5xx para falha interna.

Respostas de erro serão sanitizadas e não incluirão registros protegidos nem detalhes internos. Os testes validarão a classificação; nenhuma taxonomia de códigos de erro de domínio será criada nesta change.

### 5. Derivar identidade e Loja antes de validar os dados informados

O comando manual seguirá esta ordem lógica no Xano:

1. autenticar pela tabela `usuarios`;
2. exigir perfil `gerente` e Loja associada válida;
3. validar os cinco inputs permitidos e a prioridade canônica, rejeitando `titulo` e `descricao` ausentes, vazios ou compostos somente por espaços após remoção de espaços nas extremidades, sem impor limite mínimo ou máximo de caracteres;
4. buscar o ativo e conferir sua `lojas_id` contra a identidade;
5. buscar a categoria e exigir `permite_abertura_manual = true` e SLA numérico não nulo;
6. capturar o timestamp do backend uma vez como `criado_em`;
7. adicionar um único registro com solicitante igual a `$auth.id`, `Novo`, `manual` e o snapshot do SLA;
8. montar o DTO funcional a partir do registro persistido e das relações validadas.

Uma submissão válida sempre executará um novo `db.add`. Não haverá busca de duplicidade, chave de idempotência ou comparação com chamados automáticos. Inputs extras não participarão do `db.add`; os campos sob autoridade do Xano nunca serão obtidos de um `dblink` genérico.

Consultas de lista e detalhe usarão a relação `chamados.ativos_referencia_id -> ativos_referencia.lojas_id`. Solicitante e origem não limitam a visibilidade. O detalhe verificará existência antes de acessar relações e autorizará a Loja antes de devolver o DTO.

### 6. Adaptar o heartbeat somente no ponto de criação

O algoritmo, a consulta de categoria por nome, os três status usados na busca de incidente aberto, o limite de 15 minutos e o comportamento para ativo sem telemetria permanecerão inalterados. Somente o bloco `db.add chamados` receberá:

- `origem: "automatico"`;
- `criado_em: "now"`;
- `sla_horas_aplicado: $categoria_heartbeat.sla_horas`.

A categoria do heartbeat será preparada com SLA numérico válido e `permite_abertura_manual = false` antes da ativação. O fluxo não receberá descrição nem solicitante, porque essas obrigatoriedades foram aprovadas apenas para abertura manual. Nenhuma solução de concorrência será introduzida.

### 7. Separar o cliente de Service Desk sem duplicar a política de sessão

O frontend usará `XANO_SERVICE_DESK_BASE_URL`, documentada em `.env.example`, além de `XANO_AUTH_BASE_URL`. A base será validada e normalizada independentemente; nenhum fallback para `XANO_BASE_URL` ou para a base de autenticação será aceito.

Um adaptador de Service Desk terá modelos tipados para ativo, categoria, resumo e detalhe, e reutilizará a camada comum de transporte, timeout, cabeçalho Bearer e erros Xano. A extração de transporte comum somente será feita se preservar integralmente os testes e contratos do cliente de autenticação. A resposta `items` continuará sendo validada como coleção e os objetos internos serão validados antes de publicar State.

401 será encaminhado ao mesmo encerramento de sessão já consolidado. 403 não removerá token ou identidade. 404, 422/contrato inválido e indisponibilidade terão estados apresentáveis próprios.

**Alternativas consideradas:**

- Acrescentar operações de Service Desk ao cliente configurado com `XANO_AUTH_BASE_URL`: rejeitada porque repetiria o acoplamento de base que a change anterior separou.
- Fazer chamadas HTTP diretamente nos eventos Reflex: rejeitada por duplicar timeout, token e classificação de erros.
- Persistir novo token ou contexto de Loja para o Service Desk: rejeitada; o token e a identidade atuais são reutilizados e a Loja não é autoridade do frontend.

### 8. Implementar a jornada com State e rotas Reflex protegidas

A jornada será composta por:

- `/gerente`: página inicial do Gerente convertida na listagem básica;
- `/gerente/chamados/novo`: formulário de abertura;
- `/gerente/chamados/[chamado_id]`: detalhe dinâmico.

Um State de chamados do Gerente reutilizará o ciclo de vida da sessão e manterá dados, seleção de formulário, carregamento, sucesso e erro separados do estado de autenticação. O token continuará backend-only. Cada `on_load` revalidará a sessão/perfil antes da chamada funcional; conteúdo protegido continuará condicionado à sessão confirmada.

O formulário carregará catálogos do Xano, apresentará somente as quatro prioridades aprovadas e enviará somente os cinco campos. Durante o POST, novos envios do mesmo formulário ficarão desabilitados. Após sucesso, a interface mostrará confirmação e encaminhará para o detalhe retornado. Uma nova submissão iniciada depois disso será independente.

A listagem não criará filtros ou ordenação local com significado de negócio. Valores nulos legados serão apresentados como não informados. O detalhe será somente leitura e não renderizará controles futuros de tratativa.

### 9. Cobrir regras de backend, transporte, State e compilação

Os testes XanoScript usarão mocks controlados para verificar:

- perfil Gerente, Gerente sem Loja e perfis indevidos;
- isolamento entre duas Lojas e tentativa de ativo externo;
- categoria permitida, bloqueada, inexistente e sem SLA aplicável;
- as quatro prioridades e valor fora do vocabulário;
- `titulo` e `descricao` ausentes, vazios ou compostos somente por espaços, sem restrição adicional de tamanho;
- derivação do solicitante e rejeição da autoridade de campos extras;
- origem, `criado_em` e snapshot de SLA nos fluxos manual e automático;
- duas submissões manuais equivalentes criando dois registros;
- lista e detalhe incluindo todos os chamados da Loja e excluindo outra Loja;
- permanência da negação dos CRUDs genéricos.

Os testes Python usarão transporte HTTP simulado para validar base dedicada, DTOs e mapeamento de 401, 403, 404, 422, 5xx, timeout e conexão. Testes do State cobrirão carregamento, vazio, sucesso, bloqueio de envio concorrente, sessão expirada, negação, legado nulo e navegação. A compilação Reflex verificará Vars, eventos, rotas estáticas/dinâmicas e herança/reutilização segura da sessão.

## Risks / Trade-offs

- **[Conversão de SLA incompatível]** Valor textual não pode ser convertido sem perda → auditar antes, bloquear a ativação e exigir correção explícita; manter snapshot dos dados originais.
- **[Consumidor oculto do SLA]** Código ou contrato depende da representação textual → inventariar XanoScript, Python e demais contratos locais antes da mudança, registrar a compatibilidade de cada uso e bloquear a conversão enquanto houver consumidor não verificado.
- **[Deploy parcial]** Heartbeat ou endpoint escreve antes do schema/dados estarem prontos → aplicar na ordem schema, dados, backend funcional, heartbeat e frontend, com verificação entre etapas.
- **[Categoria manual classificada incorretamente]** Um valor `true` amplia as opções do Gerente → revisar a lista por identificador e manter `false` como padrão seguro.
- **[Registro legado invisível]** Chamado sem ativo não pode ser associado a uma Loja → preservá-lo no banco e excluí-lo dos contratos escopados, sem inventar vínculo.
- **[Lista sem paginação]** Volume futuro pode tornar a resposta grande → aceitar no escopo acadêmico atual e deixar paginação para change posterior sem criar semântica agora.
- **[Regressão de autenticação]** Compartilhamento do transporte pode alterar login ou `/me` → manter a API pública do cliente atual e executar toda a suíte consolidada.
- **[Confusão entre timestamps]** Consumidor pode continuar usando `created_at` → omitir esse campo dos DTOs funcionais e testar `criado_em` como abertura.
- **[Duplicidade manual por clique posterior]** Duas submissões válidas criam dois registros por decisão → bloquear apenas concorrência do mesmo envio na UI e não implementar deduplicação.
- **[Rollback com dados novos]** Remover campos apagaria informação criada após o deploy → preferir rollback compatível que desative rotas e preserve colunas/dados.

## Migration Plan

1. Consultar o workspace Xano alvo e registrar snapshot/ponto de recuperação das tabelas, categoria do heartbeat, endpoint `verificar-falhas` e APIs afetadas.
2. Inventariar todos os consumidores de `categorias_servico.sla_horas` em XanoScript, Python e demais contratos locais relevantes; registrar compatibilidade ou adaptação necessária e bloquear a mudança de tipo enquanto houver consumidor não verificado.
3. Auditar todos os valores atuais de `categorias_servico.sla_horas`; interromper diante de valor incompatível em categoria necessária e obter correção explícita.
4. Apresentar por identificador a tabela completa das categorias e aguardar decisão humana explícita sobre quais IDs receberão `permite_abertura_manual = true`; manter as demais, inclusive a do heartbeat, como `false`, sem escolha automática.
5. Adicionar os campos anuláveis de chamado e a flag de categoria, converter `sla_horas` para decimal preservando somente valores inequívocos e validar a integridade após a migração.
6. Criar e testar o grupo `mira-service-desk` sem reabrir CRUDs genéricos.
7. Adaptar apenas o bloco de criação automática e executar novamente os cenários atuais de heartbeat e não duplicidade sequencial.
8. Fazer dry-run e revisar o diff Xano completo; sincronizar somente após aprovação explícita e executar a matriz de testes no datasource alvo.
9. Configurar `XANO_SERVICE_DESK_BASE_URL` fora do código, publicar o cliente/State/páginas Reflex e executar testes, compilação e validação manual dos dois Gerentes de Lojas distintas.
10. Confirmar que Simulator, disparo principal do Fiscal, Técnico e Diretoria mantêm o comportamento anterior.

Em rollback, desabilitar primeiro a navegação e os endpoints funcionais, restaurar o heartbeat anterior e manter as colunas aditivas e chamados já criados para evitar perda. Se a conversão de `sla_horas` precisar ser revertida, restaurar exclusivamente os valores textuais capturados no snapshot, sem reconversão inferida. A remoção física de campos ou registros novos exigirá uma decisão destrutiva separada e não faz parte do rollback automático.
