# Tasks

## 1. Contratos Xano do filtro

- [x] 1.1 Restringir `ativo_ids` informados na consulta de chamados e na gravação da preferência à Loja atual; cobrir Totem atual, externo e transferido em testes nativos e validar os XanoScripts pelo Xano Developer MCP.
- [x] 1.2 Projetar na leitura da preferência apenas IDs de Totens atualmente elegíveis, sem gravação; cobrir preferência com IDs mistos, somente transferido e escalar legado em testes nativos e validar o XanoScript pelo Xano Developer MCP.

## 2. Catálogo da interface do Gerente

- [x] 2.1 Usar o catálogo de Totens da Loja atual na lista e preservar a reutilização do catálogo carregado; cobrir a exclusão de Totem transferido nos testes de State e executar `make reflex_check`.

## 3. Verificação integrada e publicação

- [x] 3.1 Executar `make py_test`, `git diff --check` e `openspec validate restringir-filtro-totens-gerente-loja-atual --strict`; registrar resultados e eventuais bloqueios de runtime.
- [x] 3.2 Executar dry-run seletivo das funções Xano alteradas, revisar o diff, publicar somente após autorização aplicável e confirmar dry-run posterior sem alterações pendentes; verificar a leitura da preferência do Gerente afetado sem modificar seu registro.

## Evidências

- Xano Developer MCP: três XanoScripts válidos, sem avisos.
- Xano runtime: nove testes nativos novos passaram (Loja atual, Totem transferido/externo e preferência mista, somente transferida e escalar legada).
- Consulta real da preferência do Gerente afetado: `ativo_ids = []`; catálogo atual: IDs `13`, `14`, `15`; consulta explícita com `ativo_ids = [17]`: acesso negado. Consulta sem filtro: 1 chamado autorizado.
- Registro persistido da preferência permaneceu com `ativo_ids = [17]`; nenhuma alteração de dados foi executada.
- `make py_test`: 657 passaram, 35 E2E pulados por credenciais ausentes. `make reflex_check`, `git diff --check` e OpenSpec strict passaram.
- Dry-run Xano anterior: somente três funções atualizadas; push seletivo concluído; dry-run posterior: nenhuma alteração pendente.
