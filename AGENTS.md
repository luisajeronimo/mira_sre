# AGENTS.md — MIRA

## Escopo

Este arquivo contém instruções permanentes para agentes que trabalham no repositório MIRA.
Ele é um **guia operacional do repositório**, não uma especificação funcional e não substitui o OpenSpec.

Este `AGENTS.md` na raiz vale para todo o repositório. Se uma área passar a exigir regras próprias, prefira um `AGENTS.md` mais próximo dessa área em vez de transformar este arquivo em um manual monolítico.

Não copie requisitos detalhados para cá. Mantenha comportamento funcional nas specs e nas changes do OpenSpec.

## Desenvolvimento assistido por agentes (opcional)

O funcionamento do MIRA, seus testes e o fluxo OpenSpec não dependem de Codex
ou de agentes. Colaboradores podem ignorar `.codex/` completamente.

Quando o usuário solicitar trabalho assistido por agentes, o agente principal
do Codex atua como **Supervisor** e pode delegar aos papéis nativos definidos em
`.codex/agents/`:

- **MIRA Implementer** executa somente o trabalho autorizado e devolve
  evidências ao Supervisor;
- **MIRA Reviewer** revisa de forma independente e estritamente read-only,
  devolvendo `aprovado`, `correção necessária` ou `decisão humana necessária`.

O Supervisor coordena as rodadas; os especialistas não coordenam outros
agentes. Em Explore, delega apenas investigação read-only. Em Propose e Apply,
pode alternar Implementer e Reviewer até aprovação ou gate humano. Archive só
pode ser delegado após autorização humana explícita e deve receber revisão
independente posterior.

Interrompa a automação para decisão humana diante de nova regra de negócio,
requisito ambíguo relevante, arquitetura não aprovada, nova entidade ou campo
relevante, recurso pago, alteração de segredo, operação destrutiva, push remoto
sensível, Archive, merge em `main` ou aceitação de limitação funcional. Tarefas
técnicas rotineiras já autorizadas, testes, lint, correções dentro do escopo e
validações locais reversíveis não exigem novo gate.

## Onde buscar contexto

Antes de alterar código ou documentação relevante, consulte o que se aplicar:

- `DESIGN.md` e o PNG relacionado em `docs/design/references/` para alterações
  de UI; PNG é referência visual e não define funcionalidade;
- `openspec/config.yaml` — restrições globais e orientação do processo OpenSpec;
- `docs/project-overview.md` — visão do produto, arquitetura e escopo atual/futuro;
- `docs/domain-model.md` — conceitos, entidades, relacionamentos e invariantes do domínio;
- `openspec/specs/` — comportamento aprovado e consolidado;
- `openspec/changes/<change-ativa>/` — delta em desenvolvimento, quando existir;
- código e testes afetados;
- `git status` e o diff relevante.

Changes arquivadas são histórico e evidência. Não as trate como documentação funcional vigente quando houver specs consolidadas mais novas.

## Precedência para comportamento do produto

Quando fontes divergirem, use esta ordem:

1. decisão humana explícita para o trabalho atual;
2. change OpenSpec ativa e aprovada, somente no que ela altera;
3. specs consolidadas em `openspec/specs/`;
4. documentação estável de domínio e visão do projeto;
5. implementação existente.

Código existente não vira requisito apenas por já existir.

Se houver conflito real entre fontes autoritativas, pare e reporte a inconsistência; não escolha silenciosamente uma versão.

## Mapa do repositório

- `.codex/` — configuração opcional do Codex, incluindo papéis especializados e Xano Developer MCP.
- `app/` — aplicação Reflex, navegação, UI, State e consumo das APIs.
- `xano/` — schemas, funções, APIs e regras de backend em Xano/XanoScript.
- `simulator/` — geração de telemetria para ativos existentes.
- `fiscal/` — suporte operacional à verificação de heartbeat.
- `tests/` — testes automatizados e harnesses.
- `docs/` — documentação de produto, arquitetura e domínio.
- `openspec/specs/` — specs consolidadas.
- `openspec/changes/` — changes ativas.
- `openspec/changes/archive/` — histórico de changes concluídas.

## Limites arquiteturais

- **Reflex**: interface web, navegação, apresentação de estado e chamadas aos contratos do backend.
- **Xano**: persistência, autenticação, autorização, APIs e regras de negócio.
- **Simulator**: gera telemetria; não é autoridade para ativos, chamados ou decisões de negócio.
- **Fiscal**: apoio operacional ao heartbeat; decisões de negócio continuam no Xano.

Não mova autorização ou regra de negócio para o frontend apenas para fazer um fluxo funcionar.
Não introduza mecanismo paralelo de autenticação, persistência ou regras sem change aprovada.

## Fluxo OpenSpec

Mudanças relevantes de produto, API, modelo de dados ou arquitetura seguem:

1. **Explore** — investigar sem implementar;
2. **Propose** — proposal, specs, design e tasks;
3. **Revisão humana** — resolver decisões que exigem aprovação;
4. **Apply** — implementar somente o que foi aprovado;
5. **Archive** — consolidar specs e arquivar após revisão final.

Durante o Apply:

- não amplie o escopo implicitamente;
- não invente regra, campo, status, transição, permissão ou fallback;
- se surgir decisão nova de negócio, arquitetura, autorização ou modelo de dados, pare e volte para revisão;
- trate `tasks.md` como checklist executável: uma task só está concluída quando seus critérios possuem evidência.

## Xano

Respeite as restrições de plano definidas em `openspec/config.yaml`. O MIRA não deve depender de recurso pago do Xano sem decisão humana explícita.

Quando a disponibilidade por plano ou o comportamento de um recurso Xano não estiver claro, valide na documentação oficial e/ou no Xano Developer MCP antes de desenhar a solução em torno dele.

Antes de push real ao Xano:

- valide o XanoScript afetado;
- execute `xano workspace push --dry-run`;
- revise o diff completo;
- não use opções destrutivas nem remova recursos remotos sem aprovação explícita.

Após o push, execute novo dry-run e verifique se não restaram alterações não aprovadas.

## Disciplina de mudança

- Faça alterações focadas na tarefa/change atual.
- Não refatore código alheio ao escopo apenas por conveniência.
- Preserve comportamento público fora do delta aprovado.
- Não faça limpeza, exclusão, backfill, fechamento ou reescrita de dados históricos sem requisito explícito.
- Não edite changes arquivadas para “corrigir” o presente; evolua comportamento/documentação por uma nova change quando necessário.
- Preserve recursos remotos fora do escopo em sincronizações seletivas.

Prefira soluções simples e compatíveis com o escopo acadêmico, sem enfraquecer requisitos aprovados silenciosamente.

## Validação

Use os comandos já definidos pelo projeto; não invente um fluxo alternativo de build/teste sem necessidade.

Conforme a área alterada, valide:

- testes Python relevantes e, para mudanças transversais, a suíte completa;
- compilação/validação Reflex para alterações de frontend;
- XanoScript com Xano Developer MCP para alterações Xano;
- `git diff --check`;
- OpenSpec strict para a change ativa;
- dry-run Xano antes de qualquer sincronização real.

Em validações runtime, diferencie claramente: **passou**, **falhou**, **não executado**, **bloqueado por ambiente/ferramenta/credencial** e **limitação aceita**.
Nunca registre “não executado” como “passou”.

## Segurança e ambiente

- Mantenha credenciais, tokens, senhas e segredos fora do versionamento.
- Use `.env` para valores locais e `.env.example` somente para variáveis necessárias e valores seguros/placeholders.
- Não registre tokens, senhas ou headers `Authorization` em logs/evidências.
- Não altere usuários, roles ou dados persistidos apenas para fazer um teste passar sem autorização explícita.

## Responsabilidade dos documentos

- `AGENTS.md` — regras gerais e permanentes de trabalho no repositório.
- `.codex/agents/` — papéis opcionais do Codex; não contém requisitos funcionais do produto.
- `openspec/config.yaml` — restrições globais do projeto/processo.
- `docs/project-overview.md` — visão do produto, arquitetura e estado atual/futuro.
- `docs/domain-model.md` — conceitos e invariantes estáveis do domínio.
- `openspec/specs/` — comportamento aprovado.
- change ativa — comportamento em alteração.
- archive — histórico.

Evite duplicar a mesma regra em vários arquivos. Se documentação e código divergirem, reporte a deriva antes de “corrigir” uma fonte por inferência.

## Idioma

Escreva documentação, artefatos OpenSpec e explicações do projeto em português brasileiro.
Mantenha identificadores de código, APIs e schema consistentes com a base existente e com os contratos aprovados.
