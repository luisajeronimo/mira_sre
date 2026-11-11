# Tasks

> Encerramento do Apply por decisão humana em 11/11/2026: as tasks 3.4 e 4.3 foram fechadas com dispensa das provas restantes. O `[x]` não transforma teste pulado nem revisão não executada em validação aprovada. Archive não autorizado.

## 1. Decisões

- [x] 1.1 RC-1 a RC-5 aprovadas pela responsável pelo projeto em 2026-11-08 (incorporar as versões publicadas, preservar gate do Gerente, Loja ativa e compatibilidade `Ativo`, reconciliar a resposta do Simulator; nenhuma publicação no Xano).

## 2. Repositório

- [x] 2.1 Confirmar por `pull` somente leitura que o publicado não mudou e que os documentos locais eram iguais ao `HEAD`. Evidência: pulls de 14:55 e 16:28 idênticos nos quatro documentos; `git diff --quiet HEAD` nos quatro antes da cópia; cópias de segurança feitas.
- [x] 2.2 Copiar as versões publicadas dos quatro documentos para `xano/`, esvaziando somente linhas com espaços. Evidência: diff limitado aos quatro arquivos.

## 3. Testes

- [x] 3.1 Testes nativos XanoScript das duas funções somente leitura no Xano (mocks; sem escrita). Evidência: `listar_opcoes_lojas` 5/5 PASS e `validar_criacao_usuario` 12/12 PASS em 2026-11-08 16:32–16:34.
- [x] 3.2 Ajustar `test_administracao_xanoscript.py` (projeção independente da formatação) e `test_automation_auth.py` (resposta do Simulator na forma publicada). Evidência: suíte local.
- [x] 3.3 Teste de contrato `test_contratos_publicados_reconciliados.py` (Loja ativa, Loja legada, gate do Gerente). Evidência: 4/4; os quatro falham contra o `HEAD` (mutação).
- [x] 3.4 Encerrar a matriz HTTP por dispensa da responsável em 11/11/2026. **Parcial:** `tests/test_e2e_contratos_reconciliados.py` comprovou 403 do Administrador e 401 do Simulator com `{error: "Não autenticado."}`; a lista de opções coincidiu com as Lojas ativas do cadastro e continha só `id`/`nome`. Não há Loja inativa no ambiente: sua exclusão em HTTP **não foi testada** (caso pulado). Nenhum registro foi alterado.

## 4. Validação e encerramento

- [x] 4.1 Suíte completa, `openspec validate reconciliar-contratos-publicados --strict` e `git diff --check`.
- [x] 4.2 Confirmar tratamento das rotas administrativas antes consideradas somente publicadas. A change arquivada [administracao-mira](../archive/2026-11-08-administracao-mira/proposal.md), integrada em `d75db38`, já as versionou e consolidou as specs. Pull somente leitura de 11/11/2026: 18/18 GUIDs coincidem entre Xano e `xano/api/mira_administracao/`; dry-run seletivo retornou `No changes to push`. Não é necessária nova change para essa divergência.
- [x] 4.3 Registrar dispensa da revisão independente e da consolidação das specs neste Apply por decisão da responsável em 11/11/2026. **Não executadas**; Archive não autorizado.
