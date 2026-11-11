# Design

## Context

Fontes, todas somente leitura: dry-run completo de 2026-11-08 15:32 e `xano workspace pull` de 2026-11-08 14:55 e 16:28 (os dois pulls idênticos nos quatro documentos). Antes da cópia, os quatro documentos locais eram iguais ao `HEAD` e o publicado continha todo o conteúdo local, exceto formatação; nenhum conteúdo local foi perdido (cópias de segurança feitas antes da substituição).

## Decisions

### D1. Fonte da verdade

Os documentos são copiados do `pull` publicado, esvaziando apenas linhas compostas somente de espaços, a mesma convenção de `regularizar-loja-historica-totem`. Nenhuma lógica é reescrita.

### D2. Loja ativa

`listar_opcoes_lojas` filtra `$db.lojas.status == "Ativa" || "ativa" || "Ativo"`. `validar_criacao_usuario` exige `$loja != null` e o mesmo conjunto de status para Gerente, com erro `inputerror` "Loja inexistente ou Inativa.". `Ativo` existe para Lojas legadas e é tratado como ativo; qualquer outro valor, inclusive nulo, é inativo. A regra é independente da Loja histórica do Totem.

### D3. Gate do Gerente na abertura manual

`POST /gerente/chamados` chama `exigir_perfil` com `gerente: true` antes de `abrir_chamado_manual`. Assim, Técnico, Diretoria e Administrador são negados nesse contrato, como já exige o requisito "Contratos funcionais preservam autenticação e negação por padrão", qualquer que seja o comportamento interno da função.

### D4. Resposta 401 do Simulator

A guarda passa a inicializar `$resultado = {error: "Não autenticado."}`, definir `HTTP/1.1 401 Unauthorized` e executar a validação e a persistência somente no `else`, respondendo `$resultado`. Status e corpo continuam os exigidos pela spec; a diferença é a ausência do `Content-Type` explícito no cabeçalho definido manualmente. A forma é a mesma já usada por `verificar-falhas`.

## Risks / Trade-offs

- [Loja sem `status` ou com valor fora do conjunto] → deixa de aparecer nas opções e não aceita novo Gerente; Gerentes existentes não são afetados (a regra vale somente na criação).
- [Cliente que dependia de `Content-Type` explícito no 401 do Simulator] → o Simulator do repositório trata o status, não o cabeçalho; nenhuma dependência encontrada.
- [Teste do formato de `verificar-falhas`] → `test_automation_auth.py` declara, por endpoint, a forma de resposta do documento versionado.

## Evidências

| Categoria | Resultado |
|---|---|
| Testes nativos XanoScript no Xano (funções somente leitura, com mocks, 2026-11-08 16:32–16:34) | `listar_opcoes_lojas` 5/5 PASS; `validar_criacao_usuario` 12/12 PASS |
| Teste local de contrato | `test_contratos_publicados_reconciliados.py` 4/4; ajustes em `test_administracao_xanoscript.py` e `test_automation_auth.py` |
| Checagem de mutação | Os 4 testes novos falham contra as versões do `HEAD` |
| HTTP | Não executado nesta change (sem credenciais de teste no ambiente) |
| Publicação | Nenhuma; os documentos já estavam publicados |
