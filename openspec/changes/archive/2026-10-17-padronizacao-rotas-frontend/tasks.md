# Tasks

## 1. Registro e resolução de rotas Reflex

- [x] 1.1 Registrar as rotas canônicas e os aliases transitórios em `app/app.py`, incluindo a precedência de `/chamados/novo` sobre `/chamados/[chamado_id]`.
- [x] 1.2 Implementar o dispatcher fino e protegido de `/inicio`, `/chamados` e detalhe, reutilizando as jornadas e States existentes por perfil.
- [x] 1.3 Substituir destinos por perfil, guards e fluxo de primeiro acesso para que a entrada autenticada seja `/inicio`, sem alterar a revalidação de identidade.
- [x] 1.4 Fazer aliases legados redirecionarem somente após aplicar sessão, troca pendente e perfil, preservando identificador de chamado quando aplicável.

## 2. Navegação preservada

- [x] 2.1 Atualizar botão `Início`, links de tabelas, links de detalhe e retornos de formulário para as rotas canônicas.
- [x] 2.2 Mover a tela administrativa existente para `/administracao/usuarios` e manter `/administracao` exclusivamente como alias protegido.
- [x] 2.3 Manter `/monitoramento`, seu guard atual e a apresentação visual existente sem ampliar ou restringir acesso.
- [x] 2.4 Confirmar que nenhum endpoint ou cliente Xano é renomeado e que a tratativa operacional não é alterada.

## 3. Testes e validação

- [x] 3.1 Atualizar `tests/test_app_routes.py` para registro, handlers e precedência das rotas canônicas e aliases.
- [x] 3.2 Atualizar `tests/test_auth_state.py`, `tests/test_technical_state.py`, `tests/test_administracao_lojas.py` e testes de navegação do Gerente para `/inicio`, guards, primeiro acesso e redirecionamentos legados.
- [x] 3.3 Adicionar cobertura para os quatro perfis em `/inicio` e `/chamados`, `Atribuídos a mim` exclusivo do Técnico, detalhe contextual, abertura exclusiva do Gerente e administração exclusiva do Administrador.
  Evidência: `tests/test_rotas_funcionais.py` verifica a escolha adiada de
  `ChamadosGerenteState` ou `ChamadosTecnicoState` pelo dispatcher para os
  quatro perfis, a escolha contextual do detalhe, abertura e administração;
  `tests/test_technical_state.py` já verifica que `Atribuídos a mim` só é
  selecionável por Técnico.
- [x] 3.4 Cobrir acesso direto sem sessão, sessão expirada, 403 sem perda de sessão, preservação de `chamado_id` nos aliases legados e o redirecionamento estático de `/gerente/chamados/novo` para `/chamados/novo`.
  Evidência: `tests/test_rotas_funcionais.py` cobre acesso direto sem sessão
  a `/inicio`, `/chamados`, detalhe, abertura e administração canônicas, além
  de estado neutro antes de revalidação de alias, 401, 403 sem limpar sessão,
  pendência antes de carregar catálogos, fila ou detalhe para Gerente e os
  três perfis globais, perfil negado, preservação de identificador e
  precedência das duas rotas estáticas `novo`. A regressão de troca de sessão
  também é coberta em `tests/test_technical_state.py` e
  `tests/test_rotas_funcionais.py`: uma identidade global não reutiliza
  filtros, dados ou o escopo pessoal do Técnico em `/inicio` e `/chamados`;
  a reentrada do mesmo Técnico preserva filtros, mas reinicia o escopo. A
  sequência usa no mesmo State-tree os handlers reais de `logout`, `login` e
  `GET /me`, para Técnico, Diretoria, Administrador e Gerente.
- [x] 3.5 Executar a suíte Python relevante, compilação/validação Reflex, `openspec validate padronizacao-rotas-frontend --strict` e `git diff --check`; registrar qualquer validação não executada como tal.
  Evidência inicial: `pytest -q` (324 passed), `reflex compile --dry` (passou),
  `openspec validate padronizacao-rotas-frontend --strict` (válida) e
  `git diff --check` (passou). As evidências adicionais das tasks 3.3 e 3.4
  foram executadas posteriormente na validação de Apply.
