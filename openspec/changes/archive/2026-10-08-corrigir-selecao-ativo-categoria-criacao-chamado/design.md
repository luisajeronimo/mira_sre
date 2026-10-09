# Design

## Context

A página de criação usa catálogos de ativos e categorias fornecidos pelo backend. A regressão observada ocorre quando a opção exibida e o valor consumido pela validação não permanecem no mesmo contrato durante a interação. O backend continua sendo a autoridade para validar ativo, categoria, Loja e demais campos.

## Goals / Non-Goals

**Goals:**

- Exibir nomes amigáveis sem perder os IDs funcionais.
- Fazer o evento de seleção atualizar o mesmo State lido pelo salvamento.
- Enviar IDs inteiros válidos ao cliente de Service Desk.
- Preservar erros para ativo ou categoria ausentes, inválidos ou não autorizados.

**Non-Goals:**

- Alterar endpoint, schema, regras de autorização, catálogo, ordenação ou criação automática.
- Aceitar valores arbitrários, labels como autoridade ou IDs inválidos.

## Decisions

1. **Opções estruturadas no formulário.** O State mantém, para a tela de criação, listas com `id` e `nome`. O `id` é o valor do controle e o nome é apenas a apresentação. Isso evita depender de parsing de labels compostas.
2. **Seleção controlada pelo State existente.** Os controles escrevem em `ativo_formulario` e `categoria_formulario`, que são as mesmas variáveis lidas por `abrir_chamado`. O valor recebido pelo evento é textual por ser um controle HTML; a validação converte-o para inteiro positivo antes do request.
3. **Payload de domínio permanece numérico.** O cliente Xano recebe `ativos_referencia_id` e `categorias_servico_id` como inteiros, sem alteração de contrato ou responsabilidade de autorização.
4. **Validação antes da chamada.** Se qualquer seleção estiver vazia, não positiva ou não conversível, o State mantém a mensagem de seleção e não executa POST. Com ambas válidas, o fluxo existente de criação e feedback continua sendo usado.

Alternativa descartada: usar a string visual `"id — nome"` como contrato primário do controle. Ela mistura apresentação e transporte e foi a fonte provável da divergência observada.

## Risks / Trade-offs

- [Catálogo vazio ou recarregado] → manter a validação negativa e deixar o backend rejeitar qualquer ID fora do escopo; não criar opções locais.
- [Diferença entre string do controle e inteiro do contrato] → converter explicitamente e testar o payload final.
- [Mudança visual incidental] → tocar apenas nos controles do formulário, seguindo o layout vigente.

## Migration Plan

1. Atualizar os controles e o State do formulário.
2. Executar testes de seleção completa e incompleta, compilação Reflex e suíte local.
3. Não há migração de dados nem publicação Xano prevista.
4. Em rollback, restaurar os componentes do formulário sem alterar dados remotos.

## Open Questions

Nenhuma.
