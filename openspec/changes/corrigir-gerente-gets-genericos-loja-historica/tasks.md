# Tasks

## 1. Implementação local

- [x] 1.1 Função `service_desk/listar_chamados_loja_historica_gerente` sem join com `ativos_referencia` (design D3), com 7 testes nativos XanoScript (inclusão com Totem transferido, regressão C-1, sem vínculo, sem Totem, sem `criado_em`, lista vazia, Gerente sem Loja). Evidência: `tests/test_c1_gets_genericos_loja_historica.py`.
- [x] 1.2 `GET /chamados`: ramo do Gerente pela função nova; Técnico e Diretoria globais.
- [x] 1.3 `GET /chamados/{chamados_id}`: `obter_chamado_gerente_autorizado` antes da leitura do registro (design D2).
- [x] 1.4 Testes locais de contrato, coerência dos esperados nativos com o modelo de referência e detector de regressão. Verificação de mutação (2026-11-08): endpoints vulneráveis anteriores, filtro sem comparação de Loja e mock de regressão adulterado são detectados (4, 1 e 2 falhas).
- [x] 1.5 E2E somente leitura `tests/test_e2e_c1_gets_genericos.py` (pula sem `MIRA_E2E_*`).

## 2. Validação no Xano (pendente de autorização específica)

- [ ] 2.1 Validar o XanoScript dos 3 arquivos no Xano Developer MCP (bloqueado por ferramenta nesta sessão).
- [ ] 2.2 Dry-run seletivo conforme `pacote-publicacao.md`: exatamente `+1 created` (função) e `~2 updated` (endpoints).
- [ ] 2.3 Publicação seletiva na ordem do pacote.
- [ ] 2.4 Testes nativos: 7 da função nova e 4 de `obter_chamado_gerente_autorizado`.
- [ ] 2.5 E2E somente leitura com contas de teste; registrar passou, falhou ou não executado.
