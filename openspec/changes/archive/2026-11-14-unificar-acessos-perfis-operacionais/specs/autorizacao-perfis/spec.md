## ADDED Requirements

### Requirement: Perfis operacionais compartilham os mesmos acessos
Técnico, Diretoria e Administrador DEVEM (MUST) ter os mesmos acessos operacionais, incluindo SLA na fila/detalhe, indicadores, monitoramento, abertura manual global e escopos de consulta. Gestão administrativa e seus contratos de Usuários, Lojas e Totens DEVEM (MUST) continuar exclusivos do Administrador. Autenticação e primeiro acesso continuam obrigatórios.

#### Scenario: Matriz operacional comum
- **WHEN** qualquer um dos três perfis operacionais consulta uma funcionalidade operacional com sessão concluída
- **THEN** recebe os mesmos contratos e ações, sujeitos às mesmas validações

#### Scenario: Gestão continua exclusiva
- **WHEN** Técnico ou Diretoria tenta acessar Gestão ou contratos administrativos diretamente
- **THEN** o acesso é negado; somente Administrador tem essa permissão

#### Scenario: Acesso não muda elegibilidade de responsável
- **WHEN** Diretoria ou Administrador abre um chamado ou consulta atribuições
- **THEN** continua podendo selecionar apenas Técnicos como responsáveis; o perfil da sessão não é reescrito

#### Scenario: Leituras genéricas operacionais
- **WHEN** um perfil operacional consulta Loja, Totem, telemetria ou interações pelos contratos de leitura existentes
- **THEN** recebe o mesmo escopo global dos outros perfis operacionais, sem ganhar mutações genéricas

### Requirement: Preferências operacionais são isoladas por identidade e escopo
O Xano DEVE (MUST) autorizar leitura e escrita de preferências da fila global
somente para Técnico, Diretoria e Administrador autenticados, usando o usuário
da sessão como único dono do registro. Gerente não possui esse contrato;
Os três perfis podem usar `Todos` e `Atribuídos a mim`, com preferência própria por usuário e escopo.

#### Scenario: Identificador de usuário forjado
- **WHEN** cliente tenta indicar outro usuário ao ler ou salvar preferência
- **THEN** o contrato ignora ou rejeita o identificador e usa exclusivamente a
  identidade autenticada, sem expor preferência alheia

#### Scenario: Perfil autorizado usa a própria preferência
- **WHEN** Técnico, Diretoria ou Administrador autenticado usa escopo permitido
- **THEN** o Xano lê ou grava somente o registro pertencente àquela identidade

#### Scenario: Escopo pessoal acessível aos perfis operacionais
- **WHEN** Diretoria ou Administrador solicita `Atribuídos a mim`
- **THEN** a consulta e a preferência são autorizadas para a própria identidade; sem atribuições correspondentes, a consulta retorna vazia

#### Scenario: Gerente tenta preferência global
- **WHEN** Gerente autenticado chama leitura ou save de preferências globais
- **THEN** o Xano responde HTTP 403 sem expor ou alterar registro

## MODIFIED Requirements

### Requirement: Leituras genéricas de interações não expõem registros internos ao Gerente
Os GETs genéricos de coleção e por ID de `interacoes_chamado` DEVEM (MUST) permitir Técnico, Diretoria e Administrador autenticados a receber o registro bruto. Gerente DEVE (MUST) consultar comentários pela rota funcional pública já autorizada; esses acessos NÃO DEVEM (MUST NOT) conceder mutações genéricas ou Gestão.

#### Scenario: Técnico consulta interação genérica
- **WHEN** Técnico autenticado chama o GET genérico de coleção ou de ID
- **THEN** o Xano mantém a leitura atualmente autorizada para Técnico

#### Scenario: Gerente consulta interação genérica
- **WHEN** Gerente autenticado chama qualquer um dos dois GETs genéricos de interações, mesmo para chamado de sua Loja
- **THEN** o Xano rejeita a consulta sem retornar comentário interno ou registro bruto

#### Scenario: Gerente consulta comentários públicos funcionais
- **WHEN** Gerente autenticado solicita os comentários de chamado autorizado por `GET /gerente/chamados/{chamados_id}/comentarios`
- **THEN** o contrato funcional continua retornando somente comentários públicos permitidos

#### Scenario: Outro perfil solicita GET genérico
- **WHEN** Diretoria ou Administrador chama um dos dois GETs genéricos de interações
- **THEN** o Xano autoriza a mesma leitura global permitida ao Técnico, sem conceder mutação genérica

## REMOVED Requirements

### Requirement: Preferências globais de fila são autorizadas pelo dono autenticado
**Reason**: Substituído pela decisão humana de acessos operacionais equivalentes, que revoga as restrições de perfil anteriores.
**Migration**: Aplicar o requisito "Preferências operacionais são isoladas por identidade e escopo" nesta mesma capacidade; contratos e dados históricos permanecem compatíveis.
