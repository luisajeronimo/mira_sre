# Proposta — retomada de telemetria e demonstração de confiabilidade

## Why

O silêncio configurado no Simulator não pode ser desfeito pela interface, e um Totem Offline precisa voltar a enviar telemetria continuamente para demonstrar sua recuperação. A apresentação também precisa identificar o MIRA na aba do navegador e dispor de histórico fictício coerente para ilustrar a evolução diária de MTTD e MTTR pelas fórmulas reais do Xano.

## What Changes

- Disponibilizar **Retomar telemetria** no detalhe de um Totem simulado Offline e silenciado, com confirmação explícita, cancelamento e retorno da operação. A retomada será contínua, conforme decisão do usuário, e não uma única amostra de recuperação.
- Propor um controle persistido por Totem no Xano e sua consulta pelo Simulator a cada ciclo. A ação não altera diretamente `status_atual`, não dispara outro Fiscal e não modifica chamados.
- Reutilizar o logotipo oficial `assets/mira-logo.svg` como favicon nas páginas públicas e autenticadas.
- Registrar a população pontual já concluída, somente nos Totens existentes 1 e 2, com histórico fictício de 30 dias civis completos e sem novos cadastros. O usuário escolheu persistir esse histórico no Xano, em vez de um modo de apresentação com números locais.
- Gerar telemetrias de referência e pares Offline/Online consistentes; calcular os indicadores pelos contratos existentes. Sinalizar dados simulados e melhorar a leitura do gráfico sem mudar fórmulas ou inventar pontos nos dias sem eventos.
- Preservar o lote único já carregado e as evidências de conferência, retomada da carga parcial e repetição sem duplicatas. O utilitário temporário de carga é descartado após a conclusão; não integra a aplicação nem o repositório final. Não alterar ou apagar histórico operacional existente.

### Limites do escopo

Não inclui comando remoto sobre equipamento físico, pausa de telemetria pela interface, reinício de serviços pela aplicação, novas credenciais, outro mecanismo de autenticação, automações pagas do Xano, resolução automática de chamados, reescrita de fatos legados ou gráfico abastecido por valores inventados no frontend. A validação da aplicação ocorre somente em desenvolvimento local, com `reflex run`. O README permanece na versão anterior à change. Não manter arquivo de repasse entre agentes nem utilitário permanente para repetir a carga. O usuário testa a aplicação antes de autorizar Archive; somente depois do Archive pode haver novo commit. Não executar publicação ou testes no servidor neste trabalho.

### Revisão humana antes do Apply

Aprovar em conjunto as propostas detalhadas em `design.md`: campo nullable de controle e inicialização dos Totens já simulados; acesso dos três perfis operacionais; comportamento quando a consulta do controle falhar; uso exclusivo dos Totens existentes, conforme correção explícita do usuário; exceção restrita para timestamps fictícios sem reescrever fatos; e participação desses registros nas consultas normais da rede. Os detalhes do lote e do ambiente devem estar identificados antes de qualquer carga real. O Apply foi autorizado pelo usuário e o desenho de novos cadastros foi revogado pela instrução posterior que proíbe criar Totens.

## Capabilities

### New Capabilities

- `simulacao-telemetria`: controle persistido de envio contínuo, retomada autenticada e consumo pelo Simulator.
- `dados-demonstracao-confiabilidade`: população pontual de fatos fictícios de confiabilidade, com identificação, prévia e preservação dos demais registros.

### Modified Capabilities

- `monitoramento-disponibilidade-totens`: acrescentar confirmação e feedback de retomada e delimitar a exceção de histórico sintético sem alterar a fiscalização regular.
- `autenticacao-automacoes`: proteger a leitura do controle com a chave do Simulator e contabilizar a requisição adicional no ciclo operacional.
- `frontend-sessao-navegacao`: apresentar o favicon oficial em todas as páginas.
- `dashboard-disponibilidade-confiabilidade`: identificar o contexto simulado e preservar unidades, valores, filtros e lacunas na apresentação do histórico de demonstração.
Os vínculos históricos vigentes permanecem íntegros; a demonstração não cria nem retroage vínculos.

## Impact

- **Modelo e contratos Xano propostos:** um campo em `ativos_referencia`; leitura técnica de controle no grupo operacional; retomada no grupo Service Desk; metadado de controle no detalhe do monitoramento; funções operacionais de preparação do lote, sem endpoint público de importação histórica.
- **Simulator:** `simulator/simulator.py`, configuração de IDs e transição de `SIMULATOR_ATIVO_SILENCIADO` para controle persistido. Fiscal e regras normais de heartbeat são preservados.
- **Reflex:** `app/monitoramento/`, cliente em `app/services/service_desk.py`, `app/app.py`, `app/indicadores/pages.py` e o SVG já existente.
- **Operação e validação:** carga pontual já executada, com resultados preservados na change e utilitário temporário removido; testes locais de contratos, estado e integridade do histórico, testes XanoScript já registrados, compilação Reflex, validação OpenSpec e execução local com `reflex run`. Não se presume homologação isolada nem comprovação de rollback no Free.
- **Documentação na implementação:** documentos estáveis de domínio quando necessário e evidências de entrega nesta change; restaurar o README anterior, conforme instrução humana. Não registrar instruções de acesso ao servidor.
