# Tarefas — retomada contínua e demonstração

## 1. Revisão e preparação do escopo

- [x] 1.1 Obter revisão humana dos contratos e das decisões D1–D7, incluindo campo nullable, perfis operacionais, falha fechada, histórico nos Totens existentes (correção humana posterior) e efeito do lote nas médias da rede; verificar conclusão por decisão registrada nesta change antes de implementar.
- [x] 1.2 Preparar o inventário somente leitura do ambiente-alvo, IDs participantes, silêncio inicial, plano Free, capacidade disponível e parâmetros do lote; verificar por prévia sem segredos com data-base, nomes, contagens e operações previstas, sem executar carga.

## 2. Controle e contratos Xano

- [x] 2.1 Acrescentar o campo aprovado em `xano/table/ativos_referencia.xs` e a preparação explícita dos controles ausentes; validar XanoScript pelo MCP e testes de inicialização/repetição que preservem controles já retomados e todos os fatos operacionais. Documentar a semântica do controle no modelo de domínio durante essa alteração.
- [x] 2.2 Implementar a leitura agrupada na base operacional com chave exclusiva do Simulator; verificar testes nativos de chave ausente/incorreta/cruzada, negação antes de leitura e resposta mínima dos IDs solicitados, usando o MCP para validar o XanoScript afetado.
- [x] 2.3 Implementar a retomada na base Service Desk com autorização prévia e alteração somente do controle; verificar testes para os três perfis operacionais, Gerente negado, troca pendente, sessão inválida, alvo inexistente, alvo não gerenciado, estado incompatível e repetição sem alteração de disponibilidade ou chamado.
- [x] 2.4 Acrescentar o metadado de controle ao detalhe existente e atualizar o cliente/DTO em `app/services/service_desk.py`; verificar os contratos em `tests/test_monitoramento_operacional.py`, inclusive leitura de controle ausente sem habilitar ação e mapeamento dos erros da retomada. Registrar os contratos em `design.md` e as verificações no registro de validação no checklist, preservando o README anterior.

## 3. Consumo contínuo pelo Simulator

- [x] 3.1 Fazer a consulta de controle uma vez antes dos envios e enviar somente para participantes ativos; ampliar `tests/test_automation_auth.py` para comprovar agrupamento, chave correta, IDs silenciados/ausentes não enviados e ausência de chamadas extras ao Fiscal.
- [x] 3.2 Implementar falha fechada no ciclo e observação da retomada nos ciclos seguintes e após reinício; verificar testes com timeout, formato inválido, nova leitura bem-sucedida e variável local de silêncio incapaz de reverter controle persistido.
- [x] 3.3 Preservar ciclo de 300 s, ordem sequencial, espaçamento de 3 s e contagem de requisições com os 15 participantes existentes; verificar janelas de 20 s e limites entre ciclos nos testes, sem novo rate limiter. Atualizar `.env.example` e registrar na change o papel de inicialização de `SIMULATOR_ATIVO_SILENCIADO` e a lista explícita de participantes.

## 4. Retomada com confirmação no monitoramento

- [x] 4.1 Adicionar a ação elegível e o diálogo acessível em `app/monitoramento/`, preservando os componentes e tokens de `DESIGN.md`; verificar testes de estado para abrir/cancelar/fechar sem POST e confirmar somente para o alvo permitido.
- [x] 4.2 Implementar processamento, bloqueio de reenvio, troca de seleção e descarte de resposta tardia; verificar testes de concorrência local, cancelamento, expiração, conflito e preservação do detalhe de outro Totem, sem badge Online otimista.
- [x] 4.3 Recarregar lista/detalhe e apresentar autorização de envio após sucesso; verificar cenário com estado ainda Offline e chamado inalterado. Registrar na change a jornada e a espera pelos ciclos normais, sem alterar o README.

## 5. Favicon oficial

- [x] 5.1 Declarar o SVG oficial no cabeçalho global em `app/app.py`, sem redesenhar o asset; verificar compilação/exportação existente, presença do recurso e declaração efetiva no HTML de login, primeiro acesso e páginas autenticadas, sem favicon padrão concorrente prevalecendo.

## 6. Preparação do histórico de demonstração

- [x] 6.1 Implementar as funções Xano operacionais e o planejamento determinístico do lote, com namespace próprio, data-base, IDs existentes 1 e 2 e cronologia limitada; verificar testes de 60 pares, referências válidas, fiscalização de cinco minutos, 242 registros e rejeição de datas/capacidade/destinos inválidos. Validar todo XanoScript afetado pelo MCP.
- [x] 6.2 Executar a população pontual com prévia sem escrita, ambiente/data/identidades fixados e funções em etapas pequenas, sem endpoint público; verificar pelas evidências já registradas que o lote contém os 242 fatos autorizados e preserva registros operacionais externos.
- [x] 6.3 Conferir a integridade e a retomada parcial da mesma população pontual; verificar pelas evidências a comparação integral, rejeição de duplicidade/conflito, repetição de conferência sem novos fatos e ausência de finalização que altere cadastros/estado/controles.
- [x] 6.4 Descartar o utilitário temporário após a carga, remover suas dependências de testes, apagar o arquivo de repasse entre agentes e restaurar o README anterior; verificar ausência dos arquivos removidos, de imports quebrados e de referências ao acesso particular do servidor, mantendo os resultados no registro de validação no checklist.

## 7. Apresentação dos indicadores

- [x] 7.1 Identificar o contexto acadêmico simulado no painel e manter os IDs de demonstração explicitados sem renomear cadastros nos filtros; verificar em `tests/test_indicadores_diretoria.py` que o filtro global continua global e nenhum valor ou seleção é substituído por mock local. Preservar o README anterior, conforme correção humana.
- [ ] 7.2 Refinar a leitura da série diária com legendas, cores, eixos e tooltip coerentes com o design atual; verificar que valores, unidades, lacunas, totais Xano e a visão Hoje permanecem preservados, por testes relevantes de contrato/estado e inspeção renderizada quando o ambiente estiver disponível.

## 8. Validação local e revisão humana

- [x] 8.1 Executar `make check`, `git diff --check` e `openspec validate retomada-telemetria-demonstracao --strict`, além da validação MCP do XanoScript alterado; registrar resultados reais e bloqueios, sem contabilizar runtime não executado como aprovação.
- [x] 8.2 Registrar as validações MCP, publicações Xano e dry-runs já realizados, distinguindo evidências históricas da validação local atual; verificar no registro de validação no checklist que o último dry-run não indicou deriva e que não houve remoção de recurso remoto. Não executar nova sincronização nesta rodada.
- [x] 8.3 Disponibilizar a aplicação somente em desenvolvimento local com `reflex run`; verificar resposta HTTP, carregamento do login e recurso do favicon local, sem testar ou publicar no servidor. Registrar URL local para o teste humano.
- [x] 8.4 Revisar o plano concreto do lote e, com a autorização de execução correspondente, realizar a carga somente nos Totens existentes 1 e 2; verificar contagens, identidades e fatos preservados fora do lote, preservação dos cadastros e envios posteriores, sem apresentar carga parcial como concluída.
- [ ] 8.5 Validar com o usuário o fluxo integrado pela aplicação dev: cancelar sem efeito e confirmar retomada para alvo elegível, mantendo o chamado e o estado real; associar os testes locais de ciclos/reinício e negações já existentes aos resultados observados. Não executar testes no servidor nem alterar dados para fabricar o cenário.
- [ ] 8.6 Preservar a conferência já executada dos indicadores normais dos Totens 1 e 2 e suas médias; verificar com o usuário o gráfico de 30 dias e o favicon na aplicação dev. Registrar o resultado real do teste humano, sem substituir inspeção por inferência.

Uma task só deve ser marcada após sua evidência existir. Por decisão humana, a validação ocorre somente em dev com `reflex run`. Parar e avisar o usuário para testar antes de Archive ou novo commit. Aguardar sua decisão; se posteriormente autorizado, Archive deve ocorrer antes do commit. Não realizar novos testes, publicação ou acesso operacional ao servidor nesta rodada.


## Encerramento autorizado

Após testar a aplicação dev e receber a correção do contrato de detalhe, o
usuário autorizou explicitamente **“OK PODE FAZER ARCHIVE E COMMIT AGORA”**.
A disponibilização local (8.3) está comprovada pelo HTTP e pelo acesso do usuário
à tela autenticada. As verificações 7.2, 8.5 e 8.6 permanecem sem conclusão
integral comprovada: a autorização de encerramento não é registrada como se
fossem testes executados. Os resultados técnicos parciais e as verificações
não executadas permanecem no registro de validação no checklist. Arquivar com essas ressalvas,
consolidar as specs e somente então criar o commit local, sem push.


## Registro final de validação

- Testes Python locais: **764 passed, 41 skipped** na última execução completa;
  os ignorados não contam como aprovação. Compilação Reflex passou nas rodadas
  locais registradas durante o Apply; dev disponível com frontend na porta 3000
  e backend na porta 8000, ambos com HTTP 200.
- XanoScript afetado validado pelo MCP. A correção do retorno do detalhe foi
  autorizada separadamente, publicou somente uma função de leitura e terminou
  com dry-run sem alterações; não houve nova publicação no Lightsail.
- População pontual concluída: **242 fatos** somente nos Totens existentes 1 e 2;
  repetição de conferência criou zero registros. Inventário preservou os hashes
  originais das 10 tabelas, os 16 Totens e as cinco Lojas, antes da inicialização
  autorizada dos controles.
- As seis delta specs foram consolidadas: duas specs novas e quatro atualizadas.
  A validação strict das specs principais aprovou **24/24**, sem falhas.
- README idêntico ao anterior à change. Utilitário temporário, arquivo de
  repasse e relatório separado de evidências removidos por solicitação humana.
  Não houve novos cadastros de Totens. A alteração preexistente em
  `.codex/config.toml` fica fora do commit.
- Inspeção completa do gráfico/favicon autenticado e execução integrada real de
  cancelamento/retomada com ciclos e reinício continuam **não comprovadas**;
  correspondem às tasks abertas 7.2, 8.5 e 8.6. O usuário autorizou o Archive e
  commit após o teste local; esse encerramento não transforma tais verificações
  em testes aprovados. Não há redução dos requisitos funcionais.
