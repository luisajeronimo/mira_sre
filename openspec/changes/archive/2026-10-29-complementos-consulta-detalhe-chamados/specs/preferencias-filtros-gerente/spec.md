# Spec Delta

## Purpose

Manter, por Gerente autenticado, os filtros básicos confirmados de sua lista
de chamados, sem ampliar a autorização persistida por Loja.

## ADDED Requirements

### Requirement: Gerente persiste os filtros básicos confirmados

O sistema DEVE (MUST) persistir por Gerente número, Status, Totem, período de
abertura e período de última atualização confirmados. Rascunhos e ordenação
NÃO DEVEM (MUST NOT) ser persistidos por esta capacidade; Aplicar e Limpar
DEVEM (MUST) substituir integralmente a preferência.

#### Scenario: Aplicação e restauração
- **WHEN** o Gerente aplica filtros válidos e retorna após navegação ou login
- **THEN** a lista consulta os mesmos cinco critérios confirmados

#### Scenario: Limpeza
- **WHEN** o Gerente escolhe Limpar filtros
- **THEN** a preferência passa a ter todos os filtros básicos vazios, sem mudar
  a ordenação local

#### Scenario: Rascunho
- **WHEN** o Gerente altera um campo sem aplicar nem limpar
- **THEN** a preferência persistida não é alterada

### Requirement: Preferência local preserva o escopo autorizado da Loja

Os contratos de preferência local DEVEM (MUST) derivar usuário e Loja da sessão,
autorizar somente Gerente e validar o Totem antes de consultar ou salvar. Eles
NÃO DEVEM (MUST NOT) alterar fila, escopo ou preferência global.

#### Scenario: Totem externo
- **WHEN** a preferência informa Totem de outra Loja
- **THEN** o Xano responde 403 sem retornar ou persistir dados fora do escopo

#### Scenario: Outro perfil
- **WHEN** Técnico, Diretoria ou Administrador usa o contrato local
- **THEN** o Xano responde 403 sem ler ou alterar preferência
