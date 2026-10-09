# Proposal

## Why

Na abertura manual de chamado, a interface permite selecionar um Totem e uma categoria, mas o salvamento ainda pode validar os campos como ausentes. Isso impede a criação válida e torna divergentes a seleção visual, o State e o payload enviado ao backend.

## What Changes

- Tornar explícita a representação de cada opção de Totem e categoria na tela de criação.
- Preservar o identificador numérico selecionado no State e convertê-lo de forma segura no payload de abertura.
- Manter a validação para seleções ausentes ou inválidas e cobrir o fluxo válido com testes automatizados.
- Não alterar o contrato Xano, o schema, as regras de autorização ou os fluxos automáticos.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-abertura-manual`: a seleção de Totem e categoria deve permanecer coerente entre UI, State, validação e payload.

## Impact

- Componentes Reflex da página e State de abertura manual do Gerente.
- Testes automatizados da jornada de criação.
- Nenhuma alteração prevista em Xano, schema, records ou contratos públicos.
