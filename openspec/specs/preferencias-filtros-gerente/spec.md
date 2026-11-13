# preferencias-filtros-gerente Specification

## Purpose
Manter, por Gerente autenticado, os filtros básicos confirmados de sua lista
de chamados, sem ampliar a autorização persistida por Loja.

## Requirements

### Requirement: Gerente persiste os filtros básicos confirmados
O sistema DEVE (MUST) persistir por Gerente número, coleções de Status e Totens, período de abertura e período de última atualização confirmados. Valores do mesmo filtro DEVEM (MUST) combinar por OR e os filtros diferentes por AND. Rascunhos e ordenação NÃO DEVEM (MUST NOT) ser persistidos por esta capacidade; Aplicar e Limpar DEVEM (MUST) substituir integralmente a preferência. Na leitura, Totens persistidos que deixaram a Loja atual NÃO DEVEM (MUST NOT) integrar os filtros efetivos, sem reescrita do registro.

#### Scenario: Aplicação e restauração
- **WHEN** o Gerente aplica filtros válidos e retorna após navegação ou login
- **THEN** a lista consulta os mesmos cinco critérios confirmados, incluindo todos os Status e Totens selecionados que ainda pertencem à sua Loja atual

#### Scenario: Limpeza
- **WHEN** o Gerente escolhe Limpar filtros
- **THEN** a preferência passa a ter todos os filtros básicos vazios, sem mudar
  a ordenação local

#### Scenario: Rascunho
- **WHEN** o Gerente altera um campo sem aplicar nem limpar
- **THEN** a preferência persistida não é alterada

#### Scenario: Preferência escalar anterior
- **WHEN** a preferência existente possui Status ou Totem escalar e ainda não possui representação múltipla
- **THEN** o contrato restaura cada valor existente como coleção unitária, sem backfill ou perda do critério, desde que o Totem ainda pertença à Loja atual

#### Scenario: Limpeza não restaura valor legado
- **WHEN** o Gerente limpa os filtros e autentica novamente enquanto o registro conserva dado escalar histórico
- **THEN** a representação múltipla vazia prevalece e Status ou Totem antigos não reaparecem

#### Scenario: Preferência contém Totem transferido
- **WHEN** a preferência persistida contém um ou mais Totens que hoje pertencem a outra Loja
- **THEN** a leitura retorna os demais filtros e somente os Totens atualmente elegíveis, permite consultar a lista e não altera o registro persistido

### Requirement: Preferência local preserva o escopo autorizado da Loja
Os contratos de preferência local DEVEM (MUST) derivar usuário e Loja da sessão,
autorizar somente Gerente e validar todos os Totens selecionados pela Loja atual antes de consultar ou salvar. Eles
NÃO DEVEM (MUST NOT) alterar fila, escopo ou preferência global, nem oferecer ou aceitar filtro de Loja para o Gerente. Vínculo histórico do Totem com a Loja NÃO DEVE (MUST NOT) autorizar seu uso como filtro se a Loja atual for outra.

#### Scenario: Totem externo
- **WHEN** a consulta filtrada ou a gravação da preferência informa ao menos um Totem cuja Loja atual é outra
- **THEN** o Xano responde 403 sem retornar ou persistir dados fora do escopo

#### Scenario: Totem transferido com histórico da Loja
- **WHEN** a consulta filtrada ou a gravação informa Totem transferido para outra Loja que já pertenceu à Loja do Gerente
- **THEN** o Xano responde 403 mesmo existindo vínculo histórico com a Loja do Gerente

#### Scenario: Outro perfil
- **WHEN** Técnico, Diretoria ou Administrador usa o contrato local
- **THEN** o Xano responde 403 sem ler ou alterar preferência

#### Scenario: Tentativa de filtro de Loja
- **WHEN** o cliente do Gerente tenta informar uma ou mais Lojas como filtro
- **THEN** o Xano responde 422 sem consultar ou persistir preferência e não amplia o escopo derivado da sessão

### Requirement: Catálogo do filtro de Totem reflete a Loja atual do Gerente
O catálogo usado no filtro de Totem da lista do Gerente DEVE (MUST) retornar somente Totens cuja Loja atual seja a Loja associada ao Gerente autenticado. Vínculo histórico com a Loja NÃO DEVE (MUST NOT) tornar um Totem elegível para esse catálogo.

#### Scenario: Totem transferido para fora da Loja
- **WHEN** um Totem que já pertenceu à Loja do Gerente agora pertence a outra Loja
- **THEN** ele não aparece nas opções do filtro, enquanto os Totens atualmente vinculados à Loja permanecem disponíveis

#### Scenario: Acesso direto ao catálogo
- **WHEN** o Gerente consulta o catálogo de opções por chamada direta
- **THEN** o Xano aplica a mesma restrição pela Loja da sessão, sem retornar Totens de outra Loja
