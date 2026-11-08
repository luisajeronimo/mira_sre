# Tasks

## 1. Decisões

- [x] 1.1 RC-1 a RC-5 aprovadas pela responsável pelo projeto em 2026-11-08 (incorporar as versões publicadas, preservar gate do Gerente, Loja ativa e compatibilidade `Ativo`, reconciliar a resposta do Simulator; nenhuma publicação no Xano).

## 2. Repositório

- [x] 2.1 Confirmar por `pull` somente leitura que o publicado não mudou e que os documentos locais eram iguais ao `HEAD`. Evidência: pulls de 14:55 e 16:28 idênticos nos quatro documentos; `git diff --quiet HEAD` nos quatro antes da cópia; cópias de segurança feitas.
- [x] 2.2 Copiar as versões publicadas dos quatro documentos para `xano/`, esvaziando somente linhas com espaços. Evidência: diff limitado aos quatro arquivos.

## 3. Testes

- [x] 3.1 Testes nativos XanoScript das duas funções somente leitura no Xano (mocks; sem escrita). Evidência: `listar_opcoes_lojas` 5/5 PASS e `validar_criacao_usuario` 12/12 PASS em 2026-11-08 16:32–16:34.
- [x] 3.2 Ajustar `test_administracao_xanoscript.py` (projeção independente da formatação) e `test_automation_auth.py` (resposta do Simulator na forma publicada). Evidência: suíte local.
- [x] 3.3 Teste de contrato `test_contratos_publicados_reconciliados.py` (Loja ativa, Loja legada, gate do Gerente). Evidência: 4/4; os quatro falham contra o `HEAD` (mutação).
- [ ] 3.4 HTTP com contas de teste autorizadas: Administrador 403 em `POST /gerente/chamados`; opções de Loja sem Loja inativa; 401 do Simulator com o corpo exato. Sem credenciais de teste no ambiente: não executado.

## 4. Validação e encerramento

- [x] 4.1 Suíte completa, `openspec validate reconciliar-contratos-publicados --strict` e `git diff --check`.
- [ ] 4.2 Change futura para as rotas administrativas que existem somente no publicado (fora do escopo).
- [ ] 4.3 Revisão independente e consolidação das specs antes do Archive.
