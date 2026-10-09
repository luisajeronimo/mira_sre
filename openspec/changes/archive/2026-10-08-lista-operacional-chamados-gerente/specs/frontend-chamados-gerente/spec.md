# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente possui listagem básica dos chamados da Loja
O sistema DEVE (MUST) apresentar ao Gerente autenticado uma tabela construída a partir de `GET /gerente/chamados`, com número, título e ocorrência resumida, status, prioridade, Totem, Categoria, abertura e última atualização. A ocorrência DEVE (MUST) ser derivada no Reflex dos primeiros 80 caracteres de `descricao`, com `…` somente quando houver truncamento; ela não possui ordenação independente.

#### Scenario: Listagem carregada
- **WHEN** o Gerente acessa sua página inicial com sessão revalidada e o Xano retorna chamados
- **THEN** o Reflex apresenta a tabela com somente os itens fornecidos pelo contrato da Loja e permite abrir o detalhe de cada item

#### Scenario: Loja sem chamados
- **WHEN** o contrato retorna uma coleção vazia
- **THEN** o Reflex apresenta um estado vazio explícito e mantém disponível a ação de criar chamado

#### Scenario: Chamado legado com dado ausente
- **WHEN** o contrato da lista retorna um timestamp funcional ausente em registro histórico
- **THEN** o Reflex não infere `created_at` nem apresenta data aproximada; a resposta é incompatível com a jornada operacional aprovada

#### Scenario: Datas funcionais da lista
- **WHEN** a lista contém chamado válido
- **THEN** o Reflex apresenta `criado_em` e `ultima_atualizacao_em` recebidos do contrato, sem fallback para `created_at` ou outra data técnica

#### Scenario: Ocorrência com até 80 caracteres
- **WHEN** a descrição possui no máximo 80 caracteres
- **THEN** o Reflex a apresenta integralmente como ocorrência sem reticências

#### Scenario: Ocorrência truncada
- **WHEN** a descrição possui mais de 80 caracteres
- **THEN** o Reflex apresenta somente os primeiros 80 caracteres seguidos de `…`

## ADDED Requirements

### Requirement: Reflex controla filtros, ordenação e contadores da lista
O Reflex DEVE (MUST) permitir editar, aplicar e limpar filtros de número exato, status, Totem e período de abertura, manter visíveis os filtros aplicados e enviar a ordenação escolhida ao contrato. A interface DEVE (MUST) mostrar o total filtrado retornado pelo backend e a quantidade de itens efetivamente exibidos, sem calcular o total carregando registros adicionais.

#### Scenario: Aplicação e limpeza de filtros
- **WHEN** o Gerente aplica ou limpa critérios de filtro
- **THEN** o State consulta novamente a lista, preserva a ordenação selecionada e apresenta os critérios efetivamente aplicados

#### Scenario: Ordenação de coluna
- **WHEN** o Gerente escolhe uma coluna ordenável e direção
- **THEN** o Reflex solicita a ordenação autorizada ao backend, sem ordenar somente a coleção local

#### Scenario: Falha de consulta não encerra sessão confirmada
- **WHEN** uma consulta de lista, filtro ou ordenação falha por indisponibilidade, timeout ou contrato incompatível
- **THEN** o Reflex apresenta erro sanitizado de serviço e preserva a identidade já confirmada; somente falha real de autenticação pode redirecionar ao login

#### Scenario: Contadores da consulta atual
- **WHEN** a lista responde a uma consulta com ou sem filtros
- **THEN** a interface apresenta o total filtrado e o tamanho atual de `items`

### Requirement: Formulário de abertura possui ações locais distintas
O formulário de abertura DEVE (MUST) oferecer Salvar, Limpar, Descartar e Voltar para a lista. Limpar remove somente o rascunho e permanece na tela; Descartar abandona o rascunho e retorna à lista; Voltar somente navega; nenhuma dessas três ações DEVE (MUST NOT) criar, cancelar, excluir ou alterar chamado.

#### Scenario: Limpar formulário
- **WHEN** o Gerente escolhe Limpar antes de salvar
- **THEN** os campos editáveis retornam ao estado inicial sem requisição de criação

#### Scenario: Descartar formulário
- **WHEN** o Gerente escolhe Descartar antes de salvar
- **THEN** o Reflex abandona o rascunho e retorna à lista sem requisição de criação

#### Scenario: Voltar para lista
- **WHEN** o Gerente escolhe Voltar para a lista
- **THEN** o Reflex navega sem executar operação backend sobre o rascunho

### Requirement: Sucesso de abertura permanece observável
Após criação manual aceita, o Reflex DEVE (MUST) apresentar confirmação de sucesso por tempo suficiente para ser percebida antes ou durante a navegação prevista, sem criar contrato backend apenas para mensagem visual.

#### Scenario: Criação bem-sucedida
- **WHEN** `POST /gerente/chamados` retorna sucesso
- **THEN** o Gerente percebe confirmação de abertura e continua podendo acessar o detalhe criado conforme a jornada existente
