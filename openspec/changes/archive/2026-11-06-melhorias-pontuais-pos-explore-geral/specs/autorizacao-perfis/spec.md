# Spec Delta

## ADDED Requirements

### Requirement: Leituras genéricas de interações não expõem registros internos ao Gerente
Os GETs genéricos de coleção e por ID de `interacoes_chamado` DEVEM (MUST) permitir somente Técnico autenticado a receber o registro bruto. Gerente DEVE (MUST) consultar comentários pela rota funcional pública já autorizada; esta restrição NÃO DEVE (MUST NOT) ampliar permissões de outros perfis.

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
- **THEN** a operação continua sem permissão genérica adicional nesta change
