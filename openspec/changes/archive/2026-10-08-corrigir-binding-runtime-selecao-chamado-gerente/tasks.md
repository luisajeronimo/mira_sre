# Tasks

## 1. Implementação defensiva de abertura de chamado

- [x] 1.1 Ajustar `abrir_chamado` em `app/chamados/gerente/state.py` para ignorar payloads de clique do mouse e ler com prioridade as variáveis de seleção mantidas no State, verificando que chaves de evento não anulem a seleção.
- [x] 1.2 Ajustar o botão Salvar em `app/chamados/gerente/pages.py` para não passar dados de evento DOM para o handler de submissão, verificando a compilação do componente Reflex.

## 2. Testes de regressão e validações locais

- [x] 2.1 Adicionar teste automatizado em `tests/test_gerente_lista_state.py` que passe um dicionário de clique de mouse para `abrir_chamado` comprovando que o State prevalece e o payload numérico de domínio é gerado corretamente.
- [x] 2.2 Executar testes direcionados, suíte completa, `reflex compile --dry`, validações OpenSpec e `git diff --check`.

## 3. Validação em runtime e revisão

- [x] 3.1 Executar o fluxo completo no navegador real autenticado (selecionar Totem, Categoria, Prioridade, preencher Título e Descrição, clicar em Salvar) e comprovar a superação do erro "Selecione um ativo e uma categoria." com o gate `RUNTIME_SELECT_BINDING_FIXED`.
- [x] 3.2 Realizar revisão independente read-only com o subagente `mira-reviewer`.
- [x] 3.3 Arquivar a change via OpenSpec e validar consolidação final.
