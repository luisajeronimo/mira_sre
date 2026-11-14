# Design — Equivalência operacional

## Context

Ver `proposal.md`. A fila, detalhe, tratativa e monitoramento já são compartilhados. O consumo usa contrato com gate Técnico/Administrador; Indicadores usa gates de Diretoria em funções, State e página. A abertura global utiliza os contratos da Gestão, o que impede compartilhá-la sem expor cadastros. Há consultas genéricas de leitura com listas de perfis divergentes e escopo pessoal restrito ao Técnico.

## Goals / Non-Goals

Aplicar a decisão humana por grupos explícitos de perfis nos pontos existentes, com autorização no Xano. Não alterar o perfil persistido, criar uma hierarquia/RBAC nova, mudar regras de SLA ou permitir Diretoria/Administrador como responsáveis. Sem alterar dados para testes ou editar archives.

## Decisions

- Usar o conjunto Técnico/Diretoria/Administrador nas operações compartilhadas. Manter gates administrativos exclusivos em Usuários/Lojas/Totens e nas rotas de Gestão; não tornar todo o prefixo administrativo público.
- Adicionar `GET /chamados/abertura/filtros` e `POST /chamados` no grupo Service Desk para os três perfis. O catálogo projeta apenas IDs/nomes necessários, usando os mesmos critérios de categoria manual vigente. A criação reutiliza a função existente e suas validações; o caminho de Gerente continua com seu escopo. A abertura deixa de depender de catálogos administrativos.
- Reutilizar o formulário global existente e os componentes de consumo de SLA, sem redesign. O State de abertura troca para o cliente operacional; nomes internos legados podem permanecer para evitar refatoração lateral. A navegação usa a mesma lista de destinos operacionais para os três perfis, adicionando Gestão somente para Administrador.
- Permitir `Todos` e `Atribuídos a mim` aos três perfis, com preferências isoladas por identidade/escopo e início em Todos. Consultar esse filtro não cria atribuição nem torna alguém elegível como responsável. Toda escolha de Responsável continua exigindo perfil Técnico.
- Corrigir gates e escopos das leituras genéricas já existentes, inclusive Categoria e interações; nenhuma mutação genérica é habilitada. O helper de escopo de Loja recebe a permissão explícita do Administrador, sem enfraquecer o isolamento de Gerente.
- Reconciliar o delta ainda ativo de causas/recorrência com a decisão humana atual. Suas fórmulas e histórico de evidências permanecem; um registro novo distingue a atualização de autorização.

## Risks / Trade-offs

- Permissão visual divergente do contrato → testes de matriz de três perfis e negação de Gerente/primeiro acesso no backend e frontend.
- Exposição acidental de Gestão → usar contratos operacionais próprios e testar negações administrativas reais sem mutação.
- Testes antigos codificam a matriz substituída → atualizar expectativas, preservar os testes de domínio e isolamento que continuam aprovados.
- Teste de abertura válido alteraria dados reais → usar mocks nativos completos/cliente falso e verificar em runtime apenas caminhos de leitura ou negação antes de qualquer escrita.

## Migration Plan

Validar XanoScript com Developer MCP e as duas changes em strict; executar testes Python e compilação Reflex. Mostrar dry-run seletivo e publicar somente os arquivos desta correção. Conferir leituras reais com os três perfis, negações da Gestão e novo dry-run. Nenhuma alteração de usuário, papel, segredo ou histórico. Archive depende de solicitação própria.
