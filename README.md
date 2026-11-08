# MIRA

Plataforma acadêmica de **Service Desk + Observabilidade** para totens de autoatendimento.

O MIRA combina monitoramento técnico dos totens com abertura e tratamento de chamados, permitindo acompanhar falhas e disponibilidade.

O comportamento aprovado e vigente está em [`openspec/specs/`](openspec/specs/). A visão completa do produto, incluindo funcionalidades futuras, está em [`docs/project-overview.md`](docs/project-overview.md) e [`docs/domain-model.md`](docs/domain-model.md).

## Funcionalidades implementadas

- Recebimento de telemetria dos totens enviada pelo Simulator.
- Detecção de indisponibilidade por heartbeat, com transição Online/Offline decidida pelo Xano.
- Criação automática de incidente pelo Xano na transição para Offline, sem duplicar incidente vigente.
- Página de monitoramento dos totens para Técnico, Diretoria e Administrador.
- Abertura manual de chamados pelo Gerente para totens da própria loja.
- Lista, detalhe e comentários públicos do Gerente, restritos à própria loja, com filtros múltiplos e preferências persistidas.
- Fila global para Técnico, Diretoria e Administrador, com filtros múltiplos, ordenação, preferências e escopo `Atribuídos a mim` para o Técnico.
- Tratativa operacional por um único Save: responsável, status, prioridade e categoria, com comentário público ou interno e linha do tempo.
- SLA aplicado por categoria, copiado para o chamado na criação.
- Autenticação, troca obrigatória de senha no primeiro acesso e criação de usuários pelo Administrador.

## Funcionalidades planejadas (ainda não implementadas)

- Acompanhamento somente leitura dos chamados pelo solicitante e histórico público de status (Sprint 3: contratos publicados no Xano em 07/11; interface Reflex implementada localmente, fora do repositório até a liberação condicionada K-B; ver tabela abaixo).
- Rejeição de solução pelo Gerente da loja e encerramento automático após 72 horas corridas em `Resolvido` (Sprint 3, em especificação; dependem de prova de segurança transacional).
- Contagem de SLA em tempo corrido (Sprint 3: cálculo publicado no Xano em 08/11 como função interna, sem endpoint nem exibição; exposição por perfil decidida na DE-8 em 08/11 e ainda não implementada) e indicadores de consumo.
- Aceitação explícita da solução (sem regra definida).
- Dashboards de disponibilidade, incidentes, MTTD, MTTR e SLA.

## Estado da Sprint 3 (26/10 a 08/11/2026)

Situação em 08/11/2026, na branch `explore-monitoramento-xano`. Publicados no Xano com autorização: Pacote A (2 GETs genéricos, 07/11 17:41), Pacote B (7 funções e 5 endpoints do solicitante e do histórico, 07/11 19:19) a função interna `calcular_consumo_sla_chamado` e quatro funções de leitura do Gerente, do solicitante e do Técnico (08/11). A correção C-1 dos GETs genéricos de `chamados` (função nova e dois endpoints) e a atualização do cálculo de SLA foram publicadas em 08/11. O restante continua local.

Categorias de evidência (não se misturam):

- **Teste local:** pytest sobre código ou XanoScript versionado (contrato estático, modelo de referência).
- **Validação MCP:** sintaxe e documentação conferidas pelo Xano Developer MCP, sem executar nada no Xano.
- **Teste com mock:** cliente HTTP ou State Reflex com respostas simuladas.
- **Runtime:** execução de testes no Xano.
- **Persistência/rollback:** leitura real do banco depois de uma falha.
- **Publicação:** push para o workspace.

| Item | Implementado localmente | Teste local | Validação MCP | Teste com mock | Runtime | Persistência/rollback | Publicado |
|---|---|---|---|---|---|---|---|
| GETs genéricos de interações negam o Gerente | Sim | Sim (mutação contra o `HEAD`) | Válido | — | HTTP: Gerente, Diretoria e Administrador 403; Técnico 200/404 | Não se aplica | **Sim** (Pacote A, 07/11) |
| Contratos do solicitante e do histórico de status | Sim (Xano) | Sim | Válido | Testes nativos 14/14 PASS | HTTP parcial: 404 uniforme e 403; caminho com chamado próprio não executado (sem dados) | Não se aplica (somente leitura) | **Sim** (Pacote B, 07/11) |
| Interface do solicitante e seção de histórico | Somente local (Reflex), fora do repositório até K-B | Sim, localmente | Não se aplica | Sim, localmente (cliente, State, rotas, navegação) | Não se aplica | Não se aplica | Não; o código entra no repositório, com a flag de liberação, depois da validação dos contratos (task 5.8) |
| Confirmação de publicação de comentário do Gerente | Sim (Reflex) | — | Não se aplica | Sim | Não se aplica | Não se aplica | Não |
| Consumo de SLA (`calcular_consumo_sla_chamado`), **interna**, sem endpoint (DE-8 decidida, exposição não implementada) | Sim (Xano) | Sim (modelo de referência e mutação) | Válido (versão de 07/11) | Testes nativos 20/20 PASS (08/11), incluindo troca de Categoria e instante padrão | Sem HTTP (não há endpoint) | Não se aplica (somente leitura) | **Sim** (função interna, atualizada em 08/11) |
| Prova E0.3 (atomicidade) | Pacote de prova preparado | Sim (coerência da matriz) | Válido | Não se aplica | Não executado | **Não comprovado** | Nunca no workspace compartilhado |
| GETs genéricos de `chamados` pela Loja histórica (correção C-1) | Sim (Xano; change `corrigir-gerente-gets-genericos-loja-historica`) | Sim (contrato, modelo de referência e mutação) | Bloqueada (MCP indisponível na sessão) | Testes nativos 7/7 PASS (função nova) e 4/4 PASS (autorizador do detalhe) | HTTP anônimo e token inválido: 401; E2E autenticado não executado (sem credenciais `MIRA_E2E_*`) | Não se aplica (somente leitura) | **Sim** (08/11) |
| Rejeição de solução e encerramento automático | Não: dependem da E0.3 (DT-1) e das decisões DE-3a/b e DE-4 a DE-9 | — | — | — | — | — | Não |
| Loja histórica do Totem (regra já publicada no Xano) | Regularização local em andamento (change `regularizar-loja-historica-totem`) | Sim (contrato e mutação) | Válido | Testes nativos 36/36 PASS (9 funções somente leitura) e 14/14 PASS das escritas com `mock` (`abrir_chamado_manual`, `transferir_totem`, 08/11) | HTTP: Gerente 403 em chamados sem Loja histórica; cenários de escrita não executados | Não se aplica | Já estava publicada; nenhum push nesta change |

Pacote seletivo de publicação, com o pacote A (segurança) e o B (contratos): [`pacote-publicacao.md`](openspec/changes/acompanhamento-solicitante-historico-status/pacote-publicacao.md). Evidências de validação: [`validacao-xano-2026-11.md`](openspec/changes/acompanhamento-solicitante-historico-status/validacao-xano-2026-11.md). Prova E0.3: [`prova-e03/`](openspec/changes/rejeicao-solucao-gerente/prova-e03/README.md).

## Tecnologias

- **Reflex** — frontend
- **Xano / XanoScript** — backend, banco de dados e regras de negócio
- **Python** — Simulator e Fiscal
- **OpenSpec** — especificação e evolução das funcionalidades
- **Xano CLI** — sincronização entre os arquivos locais e o workspace Xano
- **GNU Make** — automação de comandos do ambiente (opcional no Windows)

## Configuração

1. Crie o ambiente virtual e instale as dependências de [`requirements.txt`](requirements.txt).
2. Copie `.env.example` para `.env` e preencha os valores. O `.env` não é versionado.

| Variável | Uso |
|---|---|
| `XANO_BASE_URL` | Grupo operacional do Xano usado pelo Simulator e pelo Fiscal |
| `XANO_AUTH_BASE_URL` | Grupo de autenticação usado pelo Reflex |
| `XANO_SERVICE_DESK_BASE_URL` | Grupo de Service Desk usado pelo Reflex |
| `XANO_REQUEST_TIMEOUT_SECONDS` | Timeout das requisições do Reflex |
| `MIRA_SIMULATOR_AUTOMATION_KEY` / `MIRA_FISCAL_AUTOMATION_KEY` | Credenciais obrigatórias das automações |
| `SIMULATOR_ATIVOS`, `SIMULATOR_INTERVAL_SECONDS`, `SIMULATOR_INTERVAL_BETWEEN_ASSETS` | Ativos simulados, ciclo e intervalo entre envios |
| `SIMULATOR_ATIVO_*` | Cenários de teste opcionais (deixe vazio para desativar) |
| `FISCAL_INTERVAL_SECONDS` | Intervalo entre verificações do Fiscal |
| `FISCAL_REQUEST_TIMEOUT_SECONDS` | Opcional; padrão de 30 segundos |

Variáveis numéricas não podem ficar vazias: para usar o valor padrão, remova a linha em vez de deixá-la sem valor.

## Heartbeat

- Telemetria normal: ciclo a cada **5 minutos**, com os 15 ativos enviados
  sequencialmente a cada **3 segundos** (valores de `.env.example`).
- Mais de **15 minutos sem telemetria**: ativo marcado como `Offline`.
- Se não existir incidente vigente para a mesma falha, o Xano cria um chamado `Novo/Urgente`.
- Chamados duplicados para a mesma indisponibilidade são evitados.

## Execução

### Linux e macOS (GNU Make)

```bash
make setup        # cria .venv, instala dependências e cria .env a partir do exemplo
make simulator
make fiscal
make mock         # Simulator e Fiscal em paralelo
make check        # testes e compilação Reflex
```

Para a interface web, execute `reflex run` com o ambiente virtual ativado.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env   # somente se .env ainda não existir

.venv\Scripts\python.exe simulator\simulator.py
.venv\Scripts\python.exe fiscal\fiscal.py
.venv\Scripts\reflex.exe run

$env:PYTHONPATH = "."; .venv\Scripts\python.exe -m pytest -q
```

Limitações conhecidas no Windows:

- `make mock` depende de `bash`, `setsid` e grupos de processos POSIX; execute Simulator e Fiscal em terminais separados.
- `make py_test`, `make reflex_check` e `make check` usam o Python do `.venv` de cada sistema e funcionam no Windows com GNU Make; sem permissão de symlink, defina `REFLEX_BACKEND_ONLY=1` antes (ver abaixo).
- O Reflex cria links simbólicos para assets compartilhados. Sem permissão para criar symlinks (por exemplo, sem o Modo de Desenvolvedor do Windows), a interface e parte dos testes falham com `WinError 1314`.
- `tzdata` é instalado somente no Windows (marcador em `requirements.txt`), porque o sistema não fornece a base de fusos usada por `America/Sao_Paulo`.
- Para executar os testes ou `reflex compile --dry` sem permissão de symlink, defina `$env:REFLEX_BACKEND_ONLY = "1"`; nesse modo a compilação não gera os assets compartilhados do frontend.
- Para a compilação completa, use Linux: o workflow [`.github/workflows/verificacao.yml`](.github/workflows/verificacao.yml) executa `make setup` e `make check` em `ubuntu-latest` (manual ou em PR para `main`), ou WSL2. Outra opção é ativar o Modo de Desenvolvedor do Windows, que concede permissão de symlink e exige administrador.

## Service Desk

O Gerente abre e acompanha os chamados da própria loja e registra comentários públicos.

Técnico, Diretoria e Administrador consultam a fila global e tratam os chamados pelo Save operacional, alterando responsável, status, prioridade e categoria e registrando comentários públicos ou internos.

As categorias de serviço classificam os chamados e armazenam o parâmetro de SLA em `sla_horas`.

## OpenSpec

O projeto utiliza **Spec-Driven Development**.

Mudanças relevantes de regra de negócio, API ou banco devem passar pelo OpenSpec antes da implementação.

Fluxo:

```text
explore -> propose -> revisão -> apply -> archive
```

As especificações ficam em:

```text
openspec/
```
