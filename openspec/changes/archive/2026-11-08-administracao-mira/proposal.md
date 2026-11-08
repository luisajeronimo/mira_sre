# Proposal

## Why

O MIRA já permite criar usuários com primeiro acesso seguro, mas ainda não oferece ao Administrador a manutenção dos três cadastros necessários à operação. A Sprint 5 amplia essa capacidade sem liberar CRUDs genéricos nem perder vínculos e fatos históricos.

## What Changes

- Reaproveita `POST /administracao/usuarios`, a seleção de Loja e a política vigente de senha temporária; acrescenta listagem, consulta, edição de nome, e-mail, perfil e Loja, e exclusão física condicionada à ausência de dependências.
- Introduz contratos administrativos específicos para criar, consultar, editar, inativar, reativar e, quando íntegro, excluir Lojas. Novas Lojas nascem `Ativa`; `Inativa` permanece consultável e não recebe novos Gerentes ou Totens, mas sua operação existente continua.
- Introduz contratos administrativos específicos para criar, consultar, editar, transferir e, quando íntegro, excluir Totens. Identificação, nome e Loja são obrigatórios; ausência de primeira telemetria não cria estado operacional artificial.
- Permite transferir Gerente ou Totem somente para Loja `Ativa`, preservando IDs e fatos. O vínculo temporal Totem–Loja passa a registrar criação e transferências; a Loja de cada ocorrência é resolvida pelo instante funcional do fato, sem backfill ou inferência de vínculo legado não comprovado.
- Mudanças de perfil preservam histórico e não podem invalidar responsabilidade técnica existente nem remover o último Administrador, inclusive quando ele altera a própria conta.
- Autoriza Administrador a abrir chamado manual para qualquer Totem e sua Loja, com solicitante humano autenticado e as validações já aprovadas para abertura manual.
- Amplia a interface administrativa existente com as três gestões, consulta, criação, edição, exclusão com confirmação e erros funcionais, seguindo `DESIGN.md`.
- **BREAKING para consumidores que presumam que a Loja de um fato antigo acompanha o vínculo atual do Totem:** consultas e autorização histórica passam a usar vínculo temporal demonstrável; fatos legados sem Loja comprovável permanecem sem atribuição histórica, com acesso do Gerente negado por padrão.

## Capabilities

### New Capabilities

- `administracao-lojas`: cadastro, situação, consulta, edição e exclusão condicionada de Lojas.
- `administracao-totens`: cadastro, transferência, consulta, edição e exclusão condicionada de Totens.
- `frontend-administracao`: jornadas administrativas de lista, detalhe, criação, edição e exclusão das três entidades.

### Modified Capabilities

- `administracao-usuarios`: consulta, edição, mudança de perfil/Loja e exclusão segura, preservando a criação existente.
- `autorizacao-perfis`: autorização administrativa específica e abertura manual global do Administrador.
- `chamados-abertura-manual`: abertura manual por Administrador e atribuição histórica de Loja após transferência de Totem.
- `chamados-acompanhamento-gerente`: preservar o escopo histórico do Gerente após transferência de Totem.
- `chamados-fila-atribuicao-tecnica`: preservar Loja histórica de chamado nas consultas e filtros globais.
- `monitoramento-disponibilidade-totens`: manter eventos de disponibilidade e leitura histórica coerentes após transferência, sem alterar fatos anteriores.

## Impact

- Xano: contratos específicos em `mira_administracao`, validações e consultas do Service Desk, schemas de Loja/Totem e estrutura temporal de vínculo Totem–Loja aprovada. Os CRUDs genéricos continuam bloqueados.
- Reflex: página administrativa, cliente Xano, estados, rotas e navegação; reutilização da autenticação e da criação de usuários.
- Testes: autorização positiva e negativa, integridade de exclusão, transferências, preservação de histórico, sessão pendente e fluxos Reflex. A compatibilidade dos recursos básicos com o plano Free foi investigada; validar os XanoScripts e o comportamento funcional durante o Apply.

## Fora do escopo

- Reset administrativo, recuperação ou envio de senha; exclusão em cascata; backfill ou reescrita de dados históricos; alteração de responsabilidades do Simulator ou Fiscal; mudanças em changes arquivadas; liberação de CRUD genérico.
- Interrupção de monitoramento, abertura ou tratativa por situação cadastral `Inativa`; novas restrições operacionais para Lojas Inativas.

## Decisões humanas consolidadas

1. **Histórico temporal:** registrar vínculos de Totem com Loja e resolver fatos pelo instante funcional; não reescrever fatos nem inventar Loja legada sem evidência.
2. **Loja `Inativa`:** a situação cadastral não suspende Gerentes, Totens, monitoramento, abertura, tratativa ou acompanhamento existentes; somente impede novos vínculos até reativação.
3. **Último Administrador:** exclusão e mudança de perfil que deixem o sistema sem Administrador são proibidas no Xano, inclusive edição da própria conta, sem efeitos parciais.
4. **Totem nunca usado:** sua exclusão explícita pode remover o único vínculo temporal inicial junto do cadastro, desde que não existam transferências nem fatos operacionais; nenhum outro histórico é apagado.

## Prontidão técnica para o Apply acadêmico

Banco, APIs e lógica de servidor constam do Xano Free; a sintaxe necessária para tabelas, consultas temporais, verificações de dependência e transações foi analisada via Xano Developer MCP. Isso permite iniciar o desenvolvimento funcional. As garantias runtime de concorrência avançada e rollback em falha provocada não foram demonstradas nesta etapa; o Design registra os riscos residuais. Nenhuma regra de negócio aprovada é relaxada, e validação não executada não será declarada aprovada.
