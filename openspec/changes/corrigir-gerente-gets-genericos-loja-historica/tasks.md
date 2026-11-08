# Tasks

## 1. Implementação local

- [x] 1.1 Função `service_desk/listar_chamados_loja_historica_gerente` sem join com `ativos_referencia` (design D3), com 7 testes nativos XanoScript (inclusão com Totem transferido, regressão C-1, sem vínculo, sem Totem, sem `criado_em`, lista vazia, Gerente sem Loja). Evidência: `tests/test_c1_gets_genericos_loja_historica.py`.
- [x] 1.2 `GET /chamados`: ramo do Gerente pela função nova; Técnico e Diretoria globais.
- [x] 1.3 `GET /chamados/{chamados_id}`: `obter_chamado_gerente_autorizado` antes da leitura do registro (design D2).
- [x] 1.4 Testes locais de contrato, coerência dos esperados nativos com o modelo de referência e detector de regressão. Verificação de mutação (2026-11-08): endpoints vulneráveis anteriores, filtro sem comparação de Loja e mock de regressão adulterado são detectados (4, 1 e 2 falhas).
- [x] 1.5 E2E somente leitura `tests/test_e2e_c1_gets_genericos.py` (pula sem `MIRA_E2E_*`).

## 2. Validação no Xano (publicação autorizada em 2026-11-08)

- [ ] 2.1 Validar o XanoScript dos 3 arquivos no Xano Developer MCP. **Bloqueado por ferramenta** (MCP indisponível nas sessões de 2026-11-08); o parser do servidor aceitou os 3 documentos no dry-run e na publicação, o que não substitui a validação MCP.
- [x] 2.2 Dry-run seletivo conforme `pacote-publicacao.md`: exatamente `+1 created` (função) e `~2 updated` (endpoints). Evidência (2026-11-08): função `CREATE` isolado; `UPDATE query chamados GET` e `UPDATE query chamados/{chamados_id} GET`, cada um isolado, sem outro objeto.
- [x] 2.3 Publicação seletiva na ordem do pacote (função, lista, detalhe), um arquivo por vez. Dry-run posterior dos 3: "No changes to push"; `pull` somente leitura confirmou igualdade canônica com o repositório. Os avisos de referência não resolvida do push parcial (`chamados`, `usuarios`) são falsos positivos conhecidos.
- [x] 2.4 Testes nativos: 7/7 PASS da função nova (objeto 358611; inclui a regressão C-1 com Loja histórica diferente da do Gerente) e 4/4 PASS de `obter_chamado_gerente_autorizado`.
- [ ] 2.5 E2E somente leitura com contas de teste. **Parcial:** HTTP anônimo e com token inválido executados em 2026-11-08 (`GET /chamados` e `GET /chamados/1` → 401, sem dados). `tests/test_e2e_c1_gets_genericos.py` **não executado, bloqueado por credencial**: variáveis `MIRA_E2E_*` não definidas; permitido/negado do Gerente, Técnico, Diretoria e Administrador autenticados segue sem prova HTTP.
