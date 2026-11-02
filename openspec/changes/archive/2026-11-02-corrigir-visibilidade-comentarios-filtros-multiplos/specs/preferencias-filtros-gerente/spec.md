# Spec Delta

## MODIFIED Requirements

### Requirement: Gerente persiste os filtros básicos confirmados

O sistema DEVE (MUST) persistir por Gerente número, coleções de Status e Totens, período de abertura e período de última atualização confirmados. Valores do mesmo filtro DEVEM (MUST) combinar por OR e os filtros diferentes por AND. Rascunhos e ordenação NÃO DEVEM (MUST NOT) ser persistidos por esta capacidade; Aplicar e Limpar DEVEM (MUST) substituir integralmente a preferência.

#### Scenario: Aplicação e restauração
- **WHEN** o Gerente aplica filtros válidos e retorna após navegação ou login
- **THEN** a lista consulta os mesmos cinco critérios confirmados, incluindo todos os Status e Totens selecionados

#### Scenario: Limpeza
- **WHEN** o Gerente escolhe Limpar filtros
- **THEN** a preferência passa a ter todos os filtros básicos vazios, sem mudar
  a ordenação local

#### Scenario: Rascunho
- **WHEN** o Gerente altera um campo sem aplicar nem limpar
- **THEN** a preferência persistida não é alterada

#### Scenario: Preferência escalar anterior
- **WHEN** a preferência existente possui Status ou Totem escalar e ainda não possui representação múltipla
- **THEN** o contrato restaura cada valor existente como coleção unitária, sem backfill ou perda do critério

#### Scenario: Limpeza não restaura valor legado
- **WHEN** o Gerente limpa os filtros e autentica novamente enquanto o registro conserva dado escalar histórico
- **THEN** a representação múltipla vazia prevalece e Status ou Totem antigos não reaparecem

### Requirement: Preferência local preserva o escopo autorizado da Loja

Os contratos de preferência local DEVEM (MUST) derivar usuário e Loja da sessão,
autorizar somente Gerente e validar todos os Totens selecionados antes de consultar ou salvar. Eles
NÃO DEVEM (MUST NOT) alterar fila, escopo ou preferência global, nem oferecer ou aceitar filtro de Loja para o Gerente.

#### Scenario: Totem externo
- **WHEN** a preferência informa ao menos um Totem de outra Loja
- **THEN** o Xano responde 403 sem retornar ou persistir dados fora do escopo

#### Scenario: Outro perfil
- **WHEN** Técnico, Diretoria ou Administrador usa o contrato local
- **THEN** o Xano responde 403 sem ler ou alterar preferência

#### Scenario: Tentativa de filtro de Loja
- **WHEN** o cliente do Gerente tenta informar uma ou mais Lojas como filtro
- **THEN** o Xano responde 422 sem consultar ou persistir preferência e não amplia o escopo derivado da sessão
