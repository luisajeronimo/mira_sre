# frontend-administracao Specification

## Purpose

Definir a área Reflex de gestão de Usuários, Lojas e Totens para Administrador, com estados de consulta e edição seguros e feedback funcional.

## Requirements

### Requirement: Dashboard administrativo consolida os três módulos
`/administracao/gestao` DEVE (MUST) apresentar cards de Usuários, Lojas e Totens, com hierarquia visual, contexto, indicadores derivados dos dados reais e duas ações em cada card: criar e ver listagem. O layout DEVE (MUST) seguir `DESIGN.md` e usar o frame Figma `Main` como referência de composição, sem tomar seus exemplos como fatos. A visualização DEVE (MUST) acomodar larguras distintas sem perder legibilidade.

#### Scenario: Entrada administrativa
- **WHEN** Administrador confirmado abre `/administracao/gestao`
- **THEN** encontra os três cards e suas métricas calculadas apenas dos registros recebidos

#### Scenario: Distribuição de perfis
- **WHEN** o card de Usuários apresenta seus indicadores
- **THEN** mostra as quantidades reais de Administradores, Gerentes, Técnicos e Diretoria, além do total de registros

#### Scenario: Sem estado operacional conhecido
- **WHEN** Totem não possui estado informado
- **THEN** o dashboard não o contabiliza como Online ou Offline e a listagem mostra estado não informado

### Requirement: Criação ocorre em modais reutilizando contratos existentes
Criar Usuário, Criar Loja e Criar Totem DEVEM (MUST) abrir diálogos com campos e validações já aprovados, ação de cancelar/fechar, indicação de envio, erro funcional e sucesso. O Reflex DEVE (MUST) impedir submissão duplicada no estado local, atualizar a listagem depois do sucesso e não manter formulários de criação permanentemente no dashboard. A senha temporária NÃO DEVE (MUST NOT) persistir como variável de State.

#### Scenario: Criação de usuário
- **WHEN** Administrador aciona Criar Usuário
- **THEN** vê modal com Nome, E-mail, Perfil, Loja quando Gerente, senha temporária e confirmação, utilizando o contrato existente

#### Scenario: Criação de Loja ou Totem
- **WHEN** Administrador aciona Criar Loja ou Criar Totem
- **THEN** vê o modal correspondente, com campos obrigatórios e seleção apenas de Loja ativa para novo Totem

#### Scenario: Cancelamento
- **WHEN** Administrador cancela ou fecha um modal
- **THEN** nenhuma mutação é enviada e os campos temporários são descartados

#### Scenario: Erro e sucesso
- **WHEN** o Xano rejeita a criação ou a confirma
- **THEN** a interface respectivamente mantém o modal com erro funcional ou fecha o modal, informa sucesso e atualiza os registros

### Requirement: Listagens administrativas permanecem na mesma rota
Cada ação Ver listagem DEVE (MUST) apresentar os registros da categoria em `/administracao/gestao`, com busca textual, cabeçalhos, identificação, situação quando aplicável, estados de vazio, carregamento e erro e ações autorizadas de edição, transferência e exclusão. As operações de backend e suas validações DEVEM (MUST) continuar nos contratos Xano existentes.

As listagens NÃO DEVEM (MUST NOT) exibir IDs internos. A Loja de cada usuário DEVE (MUST) aparecer pelo nome; perfil, situação da Loja e estado do Totem DEVEM (MUST) aparecer visualmente em letras maiúsculas. A ação de Totem DEVE (MUST) usar o rótulo `Editar`, mantendo a transferência disponível no formulário. A busca DEVE (MUST) oferecer limpeza contextual e o indicador da listagem DEVE (MUST) refletir a quantidade filtrada quando houver busca.

#### Scenario: Seleção e busca
- **WHEN** Administrador abre uma listagem e informa termo de busca
- **THEN** a mesma rota mostra somente os registros correspondentes, mantendo os cards visíveis

#### Scenario: Limpeza da busca
- **WHEN** Administrador limpa o termo de busca
- **THEN** a lista completa e sua contagem voltam a aparecer sem trocar de rota

#### Scenario: Edição, transferência e exclusão
- **WHEN** Administrador escolhe uma ação de linha
- **THEN** a interface oferece o formulário ou confirmação apropriada e preserva a validação final do Xano

#### Scenario: Lista vazia ou erro
- **WHEN** não há registros correspondentes ou a consulta falha
- **THEN** a interface apresenta respectivamente um estado vazio ou erro, sem inventar registros

### Requirement: Área administrativa reúne três cadastros
O Reflex DEVE (MUST) permitir a Administrador com sessão confirmada navegar entre Usuários, Lojas e Totens, listar e consultar cada cadastro e abrir criação ou edição. Outros perfis e sessões pendentes NÃO DEVEM (MUST NOT) receber conteúdo administrativo.

#### Scenario: Administrador acessa a área
- **WHEN** Administrador sem pendência abre a área administrativa
- **THEN** encontra as três gestões e pode consultar seus registros

#### Scenario: Acesso indevido
- **WHEN** outro perfil, sessão pendente ou pessoa sem sessão abre rota administrativa
- **THEN** o Reflex não exibe dados ou formulários protegidos

### Requirement: Formulários administrativos apresentam validação e resultado
Os formulários DEVEM (MUST) apresentar rótulos persistentes, campos previstos pelos contratos, erro próximo à ação e indicação de sucesso. A seleção de novo vínculo ou transferência de Gerente/Totem DEVE (MUST) mostrar somente destinos `Ativa`; vínculo atual com Loja `Inativa` continua visível no detalhe. A validação final permanece no Xano.

#### Scenario: Entrada inválida
- **WHEN** o Xano rejeita criação, edição ou transferência por dado inválido
- **THEN** a interface informa o erro funcional sem indicar sucesso nem perder o registro confirmado

#### Scenario: Destino ativo
- **WHEN** Administrador escolhe Loja para novo Gerente, novo Totem ou transferência
- **THEN** a interface oferece somente Lojas `Ativa`, sujeitas à revalidação pelo Xano

#### Scenario: Vínculo atual Inativo
- **WHEN** Administrador consulta cadastro já vinculado a Loja que se tornou `Inativa`
- **THEN** a interface apresenta a Loja atual sem tratá-la como destino elegível para novo vínculo

#### Scenario: Último Administrador protegido
- **WHEN** o Xano bloqueia mudança de perfil que deixaria zero Administradores
- **THEN** a interface informa o erro funcional sem confirmar alteração local da conta

### Requirement: Exclusão administrativa exige confirmação explícita
A interface DEVE (MUST) mostrar a identidade do registro e exigir confirmação antes de solicitar exclusão. Se o Xano bloquear por dependência, a interface DEVE (MUST) manter o registro, deixar a confirmação aberta e informar o motivo funcional dentro dela, sem mensagem encoberta na página.

#### Scenario: Cancelamento
- **WHEN** Administrador cancela a confirmação
- **THEN** nenhuma exclusão é enviada

#### Scenario: Dependência impeditiva
- **WHEN** exclusão confirmada é bloqueada pelo Xano
- **THEN** o registro permanece na lista e o motivo funcional é exibido no diálogo de confirmação
