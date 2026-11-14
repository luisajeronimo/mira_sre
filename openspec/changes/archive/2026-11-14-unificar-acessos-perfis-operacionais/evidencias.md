# Evidências — Acessos operacionais equivalentes

## Decisão e entrega

A responsável aprovou acessos operacionais iguais para Técnico, Diretoria e
Administrador, exceto Gestão e suas rotas, exclusivas do Administrador.
Confirmou expressamente: “Não, responsáveis continuam sendo somente Técnicos”.
Essa confirmação não autoriza atribuir chamados à Diretoria ou ao Administrador.

O backend compartilha os gates de consulta de SLA, indicadores, fila, escopos
pessoais e leituras globais. A abertura global usa contratos do Service Desk
(`GET /chamados/abertura/filtros` e `POST /chamados`), sem expor a Gestão.
O frontend compartilha navegação, guardas, abertura e escopos, preservando o
perfil real da sessão. O cálculo de SLA e a elegibilidade de responsável não
foram alterados. Gerente conserva seu escopo de Loja.

As regras foram registradas nos oito deltas desta change, na documentação
estável e na autorização da change ativa `dashboard-causas-recorrencia`.
Os textos explicativos reduzidos dos indicadores permanecem recolhidos por
padrão. Nenhuma change arquivada foi editada.

## Validação local

| Verificação | Resultado |
| --- | --- |
| `make check` | Passou: 736 testes Python; 41 ignorados por configuração/credenciais; compilação Reflex em 3,619 s |
| Testes após normalização de mocks legados | Passou: 86 testes dos módulos de autorização, fila, Gerente e leituras genéricas |
| Testes após alinhamento final de status da fixture de liberação | Passou: 25 testes de fila e filtros |
| OpenSpec strict, ambas as changes ativas | Passou |
| `git diff --check` | Passou |
| Developer MCP, 27 arquivos XanoScript desta correção | Válidos; dois avisos preexistentes de saída de `db.patch`/`db.edit` na função legada de atribuição |
| Developer MCP após ajuste de fixtures | Dois arquivos válidos; mesmos dois avisos preexistentes |
| Detector estático de UI nos alvos modificados | `[]` |

Os testes incluem a consulta de consumo de SLA no detalhe para os três perfis,
contratos compartilhados de abertura, catálogo malformado e preservação do
perfil real da sessão. Expectativas antigas de exclusividade da Diretoria ou
de escopo pessoal somente Técnico foram substituídas pela decisão atual.

## Revisão independente

O MIRA Reviewer realizou revisão read-only e emitiu **aprovado**, com
disposition **ship no alcance de código revisado**, antes da publicação.
Conferiu os gates e contratos, proteção de Gestão, isolamento de Gerente,
responsável somente Técnico e mocks completos de escrita para abertura.
Executou independentemente os testes relevantes e conferiu o log da suíte
completa. Os achados de catálogo inválido e texto de permissão contraditório
foram corrigidos e revistos. Esse parecer não declara aprovação visual nem
substitui validação de sessão HTTP.

Na revisão das fixtures finais, o Reviewer comparou as versões antes/depois
desconsiderando mocks e testes e confirmou produção idêntica nos dois arquivos.
Conferiu escritas mockadas, ator Técnico e preservação de status, executou
82 testes locais, validou novamente os dois arquivos no Developer MCP e
emitiu **aprovado / ship no alcance de código e fixtures revisados**.

No fechamento, o Reviewer conferiu os registros de 56 testes nativos, a
repetição final com duas asserções, as 42 verificações persistidas, os dois
401 HTTP e o dry-run dos 27 alvos sem mudanças. Confirmou `all_done`, 6/6 tasks,
nenhum achado pendente e **aprovado / ship no alcance do código, fixtures e
evidências conferidos**. Preservou explicitamente os limites visual e de
sessão HTTP autenticada.

## Publicação seletiva

Workspace: `152692`. O dry-run inicial, revisado e apresentado antes do push,
conteve somente os 27 documentos da correção: uma função e dois endpoints
novos, treze funções e onze endpoints atualizados. O push concluiu os 27.
Não houve alteração de tabela, registros, ambiente, segredo ou contratos da
Gestão. Três GUIDs novos foram sincronizados para os arquivos locais.

Uma segunda publicação conteve apenas a normalização de mocks nas funções
`autorizacao/exigir_escopo_loja` e `service_desk/assumir_chamado_tecnico`.
Fixtures legadas de objeto estavam codificadas como texto multilinha; um
cenário positivo antigo de Diretoria e o novo de Administrador falharam por
esse motivo. Os objetos de mock foram corrigidos, sem alteração da lógica de
produção. Também foi alinhado o ator do mock de evento da liberação por Técnico.
Developer MCP, dry-run seletivo de duas funções e revisão do diff precederam
esse push. Os cenários positivos de escopo passaram após a correção.

Uma terceira publicação seletiva atualizou somente dois valores de status
na fixture de leitura do cenário `Técnico libera outro`, para ficar coerente
com o DTO e as asserções de preservação de `Em Atendimento`. A função passou
novamente no Developer MCP, em 25 testes locais e no dry-run de um arquivo.
Nenhuma lógica de produção foi alterada nessa rodada.
Após o push, `Técnico libera outro` foi repetido no Xano e passou nas duas
asserções de status e responsável vazio.

O dry-run posterior, limitado aos mesmos 27 arquivos, retornou
**`No changes to push`**.

## Verificações remotas

**Passaram 56/56 testes nativos selecionados**, distribuídos assim:

| Grupo | Casos |
| --- | ---: |
| Escopo de Loja: três perfis globais e isolamento de Gerente | 5 |
| Seis funções de indicadores: três perfis autorizados, Gerente e primeiro acesso negados | 30 |
| Abertura válida com mocks completos, incluindo os três perfis globais | 4 |
| Atribuição/liberação, incluindo Diretoria sem assumir e alvo não Técnico negado | 5 |
| Catálogo operacional de abertura | 5 |
| Consumo de SLA: três perfis autorizados, Gerente e chamado inexistente negados | 5 |
| Preferência pessoal de Diretoria e Administrador | 2 |

**Passaram 42/42 verificações com identidades já persistidas**, 14 por perfil
(Técnico, Diretoria e Administrador). Para cada identidade foram conferidos:
gate operacional preservando o perfil real, gate administrativo, fila global,
consumo de SLA do mesmo chamado, seis contratos de indicadores, catálogo de
abertura, fila pessoal, preferência pessoal e abertura inválida rejeitada antes
de escrita. As respostas de indicadores e SLA também passaram pelos parsers
estritos usados pelo frontend. O gate administrativo negou Técnico/Diretoria
e autorizou Administrador.

As duas rotas novas negaram chamadas HTTP anônimas com **401**. A chamada de
criação anônima foi feita com corpo vazio, sem criar chamado.

Os testes válidos de abertura e de liberação de atribuição usam mocks nas
escritas. As verificações com identidades persistidas executam somente
leituras, gates e abertura inválida rejeitada na validação de entrada, antes
de qualquer escrita. Nenhum usuário, role ou dado histórico foi alterado para
fazer testes passarem.

## Limites de validação

- **Bloqueado por credencial:** jornada HTTP autenticada dos três perfis,
  sem as credenciais E2E configuradas. Execução de função pelo CLI com uma
  identidade persistida valida regras e dados, mas não a autenticação HTTP.
- **Bloqueado por ferramenta:** inspeção renderizada, pois o host do navegador
  retornou indisponível e não havia superfícies acessíveis. Compilação e testes
  de State não constituem aprovação visual.
- O limite de requisições do Xano interrompeu uma rodada da matriz. A execução
  foi ajustada para espaçar chamadas e repetir apenas a recusa por limite;
  essa interrupção não foi contabilizada como aprovação.

O Archive permanece fora do escopo autorizado.

## Fechamento do Apply

As seis tarefas possuem evidência de implementação e validação. As validações
HTTP autenticada e visual permanecem bloqueadas nas condições descritas acima;
não são registradas como aprovadas.

`openspec instructions apply --change unificar-acessos-perfis-operacionais --json`
retornou **`all_done`**, com **6/6 tarefas concluídas** e nenhuma restante.
As duas changes passaram novamente em strict e o diff passou na conferência
de espaços após o fechamento do checklist.

## Encerramento autorizado

Em 14/11/2026, a responsável solicitou remover os breadcrumbs do login, manter
em `docs/` somente os dois documentos estáveis, arquivar ambas as changes,
fazer commit e push. O login perdeu somente a trilha e seu import; o logotipo
oficial continua em `assets/mira-logo.svg`. Links vigentes foram ajustados e
a restrição de conteúdo de `docs/` foi registrada no AGENTS.md.

`make check` passou: **735 testes**, **41 ignorados** e compilação Reflex em
**2,693 s**. A diferença de um teste é a remoção da comparação entre duas cópias
do mesmo SVG, cuja referência em `docs/design/` foi excluída por esta solicitação.
Os testes funcionais e de reutilização do logotipo permanecem. As limitações
visuais/HTTP registradas anteriormente permanecem identificadas.

Antes do Archive, os deltas foram consolidados e comparados com todas as
capacidades afetadas, preservando os demais requisitos e os Purposes existentes.
A validação strict das specs consolidadas passou: **22/22**, sem falhas.
