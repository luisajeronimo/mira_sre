# Tarefas — listagens e detalhe dos chamados

## 1. Nomes e seleção

- [x] 1.1 Ocultar os prefixos de IDs nos filtros de Técnico, Totem e Loja usando apresentação opt-in no componente compartilhado; verificar rótulos completos, seleção por valor original e nomes repetidos na prévia local.
- [x] 1.2 Retirar IDs dos rótulos de Totens e dos fallbacks de Totem/Loja nos indicadores; verificar testes de estado que preservem valores, recortes e preferências por ID.

## 2. Detalhe e histórico

- [x] 2.1 Posicionar visibilidade compacta acima do comentário e preservar Público obrigatório e bloqueio durante envio; verificar composição renderizada, teclado e testes existentes de tratativa.
- [x] 2.2 Remover caixas e bordas internas das diferenças e do comentário agrupado, mantendo a grade e os fatos; verificar a prévia desktop com várias alterações, texto longo e estado vazio.
- [x] 2.3 Deduplicar a autoria pela identidade dos autores, preservando autores distintos e visibilidade exclusiva do comentário; verificar regressões de estado com mesma identidade, identidades diferentes e nomes iguais.
- [x] 2.4 Aplicar o mesmo acabamento ao histórico público do Gerente, retirando cards aninhados sem ampliar seu escopo; verificar componentes e contratos de leitura existentes.

## 3. Validação e revisão

- [x] 3.1 Executar `make check`, `git diff --check` e OpenSpec strict; registrar resultados reais e verificar que não há alteração de contrato Xano, README ou dados.
- [x] 3.2 Inspecionar os componentes reais na prévia local em 1280 e 1440 px, menus, foco, texto longo e seleção; deixar o dev normal acessível e avisar o usuário para testar antes de Archive ou commit.

## Validação local

- [x] 4.1 Aplicar a revisão visual do usuário: badge de Público/Interno abaixo da data e menor espaçamento entre as alterações do registro; conferir comentários isolados e agrupados em dev, em 1280 e 1440 px, texto longo e validações relevantes.

- **Passou na revisão:** 94 testes de `tests/test_technical_state.py`, `make reflex_check`, `git diff --check` e OpenSpec strict. Prévia dev em 1280 e 1440 px confirmou badge abaixo da data, alinhado à direita, colunas ajustadas ao conteúdo, 8 px entre linhas e blocos, autoria preservada e texto longo sem overflow ou erros JavaScript.

- **Passou:** `make check` — 770 testes passaram, 41 foram ignorados e a compilação Reflex concluiu. `git diff --check` e OpenSpec strict passaram.
- **Passou:** componentes reais em prévia isolada com dados fictícios, executada por `reflex run --env dev`, em 1280 e 1440 px. Conferidos histórico técnico e público, texto longo, vazio, Público obrigatório, seletor de 136 × 32 px, foco e escolha por teclado, filtros sem IDs visíveis e seleção independente de nomes iguais. Sem overflow horizontal ou erros JavaScript.
- IDs internos preservados nas seleções e consultas. Sem alterações em Xano, contratos, README ou dados persistidos.
- **Revisão humana:** após a revisão no dev e os ajustes de badge e espaçamento, o usuário aprovou o resultado e autorizou Archive, commit e push na `main` em 15/11/2026.
- **Consolidação:** quatro requisitos sincronizados nas duas specs afetadas, preservando seu conteúdo anterior. Validação strict das 24 specs consolidadas passou, sem falhas.
