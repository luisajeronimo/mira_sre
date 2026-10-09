# Design

## Context

A abertura manual de chamado pelo Gerente utiliza controles Reflex com seleção vinculada ao State (`ChamadosGerenteState.ativo_formulario` e `ChamadosGerenteState.categoria_formulario`). No entanto, o botão "Salvar" disparava `on_click=ChamadosGerenteState.abrir_chamado`, fazendo com que o Reflex compilasse a passagem do evento DOM de clique (`_e`, contendo `button`, `client_x`, etc.) como argumento para `abrir_chamado(self, form_data)`. O método avaliava `dados = form_data or {...}`, resultando em `dados` sendo o dicionário do clique em vez das variáveis do State, falhando na validação de seleção.

## Goals / Non-Goals

**Goals:**

- Fazer com que o salvamento acionado pelo botão consuma estritamente o State de formulário.
- Ignorar eventos de clique do DOM ou payloads não relacionados a dados de domínio.
- Proteger o handler contra chamadas diretas ou sintaxes que passem dicionários de eventos de UI.
- Validar o fluxo com testes automatizados de regressão e no navegador real autenticado.

**Non-Goals:**

- Alterar schemas, endpoints, regras de autorização ou contratos do Xano.
- Modificar o fluxo de seleção nos componentes de select (`rx.select.root`).
- Alterar paginação, ordenação ou filtros da lista operacional.

## Decisions

1. **Assinatura e leitura prioritária do State em `abrir_chamado`:**
   O handler `abrir_chamado` passa a ler primordialmente as propriedades mantidas no State (`self.ativo_formulario`, `self.categoria_formulario`, `self.prioridade_formulario`, `self.titulo_formulario`, `self.descricao_formulario`).
   Caso um argumento `form_data` seja fornecido (ex: testes legados ou submissão programática), ele só é considerado se contiver chaves explícitas de domínio (`ativos_referencia_id` ou `categorias_servico_id`). Dicionários decorrentes de eventos de clique do mouse (contendo `button`, `client_x`, etc.) são sumariamente ignorados.
2. **Desacoplamento de parâmetros de clique no botão:**
   Em `pages.py`, a chamada do botão `on_click` garante que o evento seja invocado como uma ação pura sem repassar argumentos de clique para a camada de dados.
3. **Teste de regressão em nível de evento:**
   Adicionar teste automatizado que passe um dicionário de evento de clique do DOM para `abrir_chamado` e comprove que o State é preservado, validado e que o payload correto com inteiros é enviado ao cliente backend.

## Risks / Trade-offs

- [Chamada legada passando dados via dicionário em testes] → O handler aceita `form_data` somente quando contiver chaves de domínio reais, mantendo compatibilidade com testes que possam injetar dados diretamente.
- [Regressão em outros botões de formulário] → Botões "Limpar", "Descartar" e "Voltar" já são métodos sem parâmetros; apenas "Salvar" recebe o ajuste defensivo.

## Migration Plan

1. Ajustar `app/chamados/gerente/state.py` para ignorar eventos de clique e priorizar o State.
2. Ajustar `app/chamados/gerente/pages.py` para invocar o handler sem parâmetros de evento.
3. Executar suíte de testes e teste de regressão específico.
4. Validar em runtime no navegador autenticado (gate `RUNTIME_SELECT_BINDING_FIXED`).
