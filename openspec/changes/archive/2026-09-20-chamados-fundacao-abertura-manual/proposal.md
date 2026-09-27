## Why

O MIRA já possui autenticação, autorização e sessão, mas ainda não oferece uma operação funcional para o Gerente registrar e acompanhar problemas da própria Loja. O schema preliminar de chamados também não preserva descrição, origem explícita nem o SLA vigente na abertura, o que precisa ser estabilizado antes da fila e da tratativa técnica.

## What Changes

- Estabelecer a fundação funcional de chamados preservando, para os novos fluxos, descrição, origem canônica (`manual` ou `automatico`), `criado_em` como timestamp de negócio e um snapshot explícito do `sla_horas` vigente na categoria.
- Manter `created_at` somente como metadado técnico e preservar registros legados sem inferir origem, descrição, timestamp de negócio ou SLA histórico.
- Tornar explícita em `categorias_servico` a propriedade booleana `permite_abertura_manual`; somente categorias marcadas com `true` poderão ser usadas pelo Gerente, e a categoria do heartbeat permanecerá com `false`. A classificação das categorias existentes será um gate humano obrigatório por identificador: nenhuma categoria receberá `true` por inferência ou seleção automática.
- **BREAKING**: evoluir `categorias_servico.sla_horas` de texto opcional para uma representação numérica compatível com a cópia segura do snapshot. Antes da mudança de tipo, todos os consumidores existentes do campo deverão ser inventariados e verificados, incluindo XanoScript, Python e demais contratos locais relevantes. Valores existentes somente poderão ser convertidos quando sua representação numérica for inequívoca; qualquer consumidor incompatível ou valor incompatível interromperá a migração para correção explícita.
- Criar o grupo funcional Xano `mira-service-desk`, autenticado por `usuarios`, com contratos próprios para listar ativos e categorias permitidos, abrir chamado manual, listar chamados da Loja e consultar o detalhe de um chamado da Loja.
- Fazer o Xano derivar `solicitante_id` e Loja da identidade autenticada, validar o perfil Gerente e confirmar que o ativo pertence à sua Loja, sem aceitar esses dados como autoridade do frontend.
- Validar no Xano que a abertura contém ativo, categoria permitida, prioridade `Baixa`, `Média`, `Alta` ou `Urgente`, título e descrição; `titulo` e `descricao` serão rejeitados quando ausentes, vazios ou compostos somente por espaços, sem introduzir limite mínimo ou máximo de caracteres. Cada submissão válida criará um chamado `Novo` e de origem `manual`, sem deduplicação.
- Adaptar minimamente o criador automático existente para registrar origem `automatico`, `criado_em` e snapshot de SLA, sem redesenhar heartbeat, estados abertos, deduplicação, encerramento ou ativos sem telemetria.
- Adicionar ao Reflex a jornada autenticada do Gerente com listagem básica, formulário de abertura, detalhe básico e estados de carregamento, sucesso e erro, reutilizando a sessão já consolidada.
- Configurar uma URL base exclusiva do grupo de Service Desk, independente de `XANO_AUTH_BASE_URL` e dos grupos operacionais internos, sem codificar URL de ambiente.
- Manter bloqueados os CRUDs genéricos e deixar fora do escopo fila e tratativa técnica, atribuição, interações, diagnóstico, solução, mudanças de status, dashboards e indicadores.

## Capabilities

### New Capabilities

- `chamados-abertura-manual`: fundação persistida de chamados, abertura manual autorizada por Loja, acompanhamento pelo Gerente, contratos funcionais do Xano e compatibilidade mínima do criador automático.
- `frontend-chamados-gerente`: experiência Reflex para listar, abrir e consultar chamados da Loja por meio do grupo funcional de Service Desk.

### Modified Capabilities

- `frontend-sessao-navegacao`: estender a casca autenticada e os guards do Gerente para os destinos funcionais de chamados, preservando a sessão e a autorização no Xano.

## Impact

- Tabelas Xano `chamados` e `categorias_servico`, incluindo migração compatível com dados legados, validação dos valores atuais de SLA e auditoria prévia de todos os consumidores de `categorias_servico.sla_horas`.
- Novo grupo e endpoints XanoScript `mira-service-desk`; os CRUDs genéricos existentes permanecem negados.
- Criação automática em `verificar-falhas`, alterada somente para preencher os novos dados compartilhados de criação.
- Cliente HTTP, State, componentes, páginas, rotas, configuração e testes do Reflex, com nova variável de ambiente dedicada à base do Service Desk.
- Testes XanoScript e Python para autorização, escopo Loja/Ativo, categoria manual, prioridade, origem, timestamps, snapshot de SLA, contratos e estados da interface.
- Nenhuma mudança nas credenciais, nos perfis oficiais, na política de sessão, no Simulator, no disparo do Fiscal ou nos cálculos de SLA, MTTD e MTTR.
