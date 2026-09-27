# AGENTS.md — MIRA

## Finalidade

Este arquivo define como agentes de Inteligência Artificial devem trabalhar no projeto MIRA.

Antes de realizar alterações relevantes, consulte:

- `docs/project-overview.md`;
- `docs/domain-model.md`;
- `openspec/config.yaml`;
- a especificação consolidada vigente do projeto;
- a change do OpenSpec relacionada à tarefa atual, quando existir.

Não transforme este arquivo em uma cópia dos requisitos funcionais. Regras específicas de uma funcionalidade devem permanecer nas respectivas especificações e changes.

## Arquitetura

Respeite as responsabilidades já definidas:

- **Reflex** é responsável pela aplicação web, incluindo Service Desk, navegação e dashboards.
- **Xano** é responsável pelo backend, persistência, autenticação, autorização, APIs, agregações e regras de negócio.
- **Simulator Python** gera telemetria para ativos já cadastrados no Xano.
- **Fiscal Python** apenas dispara periodicamente a verificação de heartbeat.
- A decisão de marcar um ativo como Offline, verificar incidentes existentes e criar incidente automático pertence ao Xano.

Não transfira regras de negócio do Xano para o Reflex, Simulator ou Fiscal.

## Frontend

O frontend deve ser implementado com Reflex.

Utilize os mecanismos próprios do Reflex para:

- componentes;
- `State`;
- variáveis de estado;
- eventos;
- páginas;
- rotas;
- consumo das APIs do Xano.

As Agent Skills do Reflex são material de apoio ao agente e não substituem os documentos de contexto nem o OpenSpec.

## Backend e dados

Preserve o modelo e os relacionamentos já existentes antes de propor novas estruturas.

Não crie novos campos, entidades, estados ou regras apenas por serem comuns em sistemas de Service Desk.

Quando uma mudança exigir alteração do modelo de dados ou de uma regra de negócio, registre e revise essa decisão na change correspondente antes da implementação.

A autenticação e a autorização são responsabilidades do Xano. Não implemente autorização apenas escondendo elementos no frontend.

## Usuários e autenticação

O domínio possui usuários com perfis de **Gerente**, **Técnico** e **Diretoria**.

A documentação existente representa a autenticação como responsabilidade do Xano. Não trate senha como dado de negócio a ser manipulado pelo Reflex ou por scripts Python. Quando detalhes de credenciais forem necessários, utilize os mecanismos de autenticação do Xano e não introduza uma solução paralela sem uma change aprovada.

## Regras funcionais permanentes

- A referência temporal da telemetria é `evento_timestamp`.
- Mais de 15 minutos sem telemetria caracteriza indisponibilidade do ativo e permite que o Xano o marque como Offline.
- A criação automática de incidente deve evitar duplicidade para a mesma falha enquanto houver incidente equivalente aberto.
- A abertura manual de chamado pelo gerente permanece independente do monitoramento automático.
- O SLA é definido pela categoria de serviço por meio do parâmetro `sla_horas`.
- Não invente tempos fixos de SLA, matriz de impacto e urgência, novos status ou transições que ainda não estejam aprovados.

## OpenSpec

Mudanças relevantes devem seguir o processo incremental do OpenSpec.

Fluxo de trabalho:

1. Explore;
2. Propose;
3. revisão humana;
4. Apply;
5. Archive.

Durante o `Explore`, investigue e proponha alternativas sem implementar código.

Durante o `Apply`, implemente somente o que estiver aprovado na change atual. Se surgir uma decisão não especificada que altere regra de negócio, modelo de dados, autorização ou arquitetura, interrompa a implementação e proponha a revisão da change.

## XanoScript e sincronização

Quando necessário, utilize o Xano Developer MCP para consultar documentação e validar XanoScript.

Utilize o Xano CLI para sincronização operacional com o workspace Xano.

Revise alterações antes de executar operações destrutivas ou sincronizações que removam recursos existentes.

O projeto deve respeitar as restrições de plano definidas em `openspec/config.yaml`; recursos pagos do Xano não devem ser introduzidos sem decisão humana explícita.

## Código

- Reutilize código existente quando apropriado.
- Evite duplicação.
- Não altere funcionalidades não relacionadas à tarefa atual sem justificativa.
- Prefira soluções simples e compatíveis com o escopo acadêmico.
- Mantenha as responsabilidades de Reflex, Xano, Simulator e Fiscal separadas.

## Configuração e segredos

Credenciais, tokens e valores específicos de ambiente devem permanecer fora do versionamento.

Use `.env` para valores locais e `.env.example` apenas como referência das variáveis necessárias.

## Idioma

Escreva documentação, artefatos OpenSpec e explicações do projeto em português brasileiro.
