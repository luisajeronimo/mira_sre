# Spec Delta

## ADDED Requirements

### Requirement: Fila global inclui filtros básicos completos e Loja

A fila de Técnico, Diretoria e Administrador DEVE (MUST) oferecer número,
Status, Totem, período de abertura, período de última atualização e Loja, além
dos filtros globais já aprovados. Loja DEVE (MUST) aparecer como coluna e todos
os critérios DEVEM (MUST) ser filtrados no Xano e persistidos por usuário e
escopo sem alterar ordenação ou escopo rápido.

#### Scenario: Filtro de Loja confirmado
- **WHEN** perfil global aplica Loja válida junto aos demais filtros
- **THEN** a resposta contém somente chamados daquela Loja e a preferência
  restaurada conserva o mesmo identificador de Loja

#### Scenario: Última atualização confirmada
- **WHEN** perfil global confirma período de última atualização
- **THEN** a fila retorna somente chamados atualizados no intervalo inclusivo e
  restaura o período após novo login

#### Scenario: Loja inválida
- **WHEN** o cliente informa Loja inexistente ou inválida
- **THEN** o Xano responde 422 sem consultar ou alterar a preferência válida

### Requirement: Fila global ordena pela Loja exibida

A coluna Loja da fila global DEVE (MUST) ser ordenável. O primeiro clique DEVE
(MUST) solicitar ordem ascendente e o clique seguinte ordem descendente; o
cabeçalho ativo DEVE (MUST) exibir somente a seta correspondente. O Xano DEVE
(MUST) ordenar pelo nome de Loja exibido, sem depender da ordenação local do
Reflex, e desempatar pelo ID do chamado. A ordenação DEVE (MUST) permanecer na
preferência existente, isolada por usuário e escopo.

#### Scenario: Loja ascendente persistida
- **WHEN** perfil global ordena a coluna Loja pela primeira vez
- **THEN** o Xano retorna as Lojas em ordem alfabética ascendente, desempata
  pelo ID e a preferência do mesmo usuário e escopo passa a usar `loja` e
  `ASC`

#### Scenario: Loja descendente persistida
- **WHEN** perfil global aciona novamente a coluna Loja já ativa
- **THEN** o Xano retorna as Lojas em ordem alfabética descendente, desempata
  pelo ID e a preferência do mesmo usuário e escopo passa a usar `loja` e
  `DESC`

### Requirement: Detalhe global direciona ao Monitoramento do Totem

O detalhe autorizado a Técnico, Diretoria e Administrador DEVE (MUST) oferecer
ação para abrir `/monitoramento` com o Totem do chamado selecionado. A seleção
DEVE (MUST) sobreviver à recarga pela URL e manter a autorização consolidada do
Monitoramento.

#### Scenario: Abertura do detalhe do Totem
- **WHEN** perfil global aciona Detalhe do Totem em chamado autorizado
- **THEN** a rota abre o painel existente com aquele Totem carregado

#### Scenario: Perfil não autorizado
- **WHEN** perfil sem acesso ao Monitoramento manipula a URL de seleção
- **THEN** a rota mantém sua negação consolidada sem expor dados do Totem
