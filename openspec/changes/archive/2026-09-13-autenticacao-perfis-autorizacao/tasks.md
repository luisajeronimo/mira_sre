## 1. Preparação e segurança da migração

- [x] 1.1 Consultar o estado remoto do Xano e comparar tabela `usuarios`, grupos de API e endpoints com o snapshot local, verificando que o inventário das diferenças foi revisado antes de qualquer sincronização.
- [x] 1.2 Auditar os valores de perfil existentes no Xano e registrar o mapeamento aprovado de `tecnico_n1`, `tecnico_n2` e `tecnico_n3` para `tecnico`, de `diretor` para `diretoria` e a manutenção de `gerente`, verificando que nenhum outro valor será convertido sem decisão humana.
- [x] 1.3 Confirmar que a decisão revisada continua sendo uma referência direta de um Gerente para uma Loja e verificar que qualquer mudança de cardinalidade foi incorporada à proposta, às specs e ao design antes de editar o modelo.
- [x] 1.4 Registrar um ponto de recuperação dos recursos Xano afetados e verificar que tabela, endpoints e funções de autorização podem ser restaurados antes de iniciar a migração.

## 2. Modelo de identidade no Xano

- [x] 2.1 Consultar e validar com o Xano Developer MCP a forma suportada de habilitar autenticação nativa e armazenar credenciais na tabela existente `usuarios`, verificando que a solução não expõe senha nas respostas.
- [x] 2.2 Atualizar a definição local de `usuarios` para autenticação nativa do Xano e verificar que somente `gerente`, `tecnico` e `diretoria` são aceitos como valores oficiais de perfil.
- [x] 2.3 Adicionar a referência `usuarios.lojas_id` para `lojas` e verificar que um vínculo válido pode ser persistido para Gerente sem tornar esse campo fonte de escopo para Técnico ou Diretoria.
- [x] 2.4 Preparar localmente o plano de normalização dos usuários e dos vínculos de Loja para revisão, verificando que nenhuma alteração remota foi aplicada e que nenhum valor específico de ambiente foi gravado em arquivo versionado.

## 3. Contratos de autenticação

- [x] 3.1 Implementar no Xano a operação de login com token válido por 8 horas e verificar os cenários de credenciais válidas, credenciais inválidas e perfil não oficial sem distinguir publicamente usuário inexistente de senha incorreta nem introduzir refresh token ou renovação automática.
- [x] 3.2 Implementar no Xano a operação de identidade atual e verificar que token válido retorna apenas `id`, `nome`, `email`, perfil oficial e a Loja aplicável, enquanto token ausente ou inválido é rejeitado.
- [x] 3.3 Verificar por teste de resposta que login e identidade atual nunca retornam senha, representação reversível da senha ou material interno de autenticação.
- [x] 3.4 Documentar o contrato mínimo de login e identidade atual para consumo futuro pelo Reflex e verificar que nenhuma validação de credencial ou autorização foi atribuída ao frontend.

## 4. Autorização por perfil no Xano

- [x] 4.1 Implementar verificações reutilizáveis de identidade, perfil oficial e negação por padrão no Xano, validando o XanoScript com o Xano Developer MCP.
- [x] 4.2 Inventariar e classificar explicitamente as rotas destinadas a usuários e as rotas existentes do Simulator e do Fiscal, verificando que a proteção não será aplicada indiscriminadamente ao grupo inteiro.
- [x] 4.3 Proteger as APIs destinadas a usuários contra acesso anônimo e verificar que requisições sem sessão não retornam dados nem executam alterações.
- [x] 4.4 Aplicar o escopo da Loja às consultas do Gerente e verificar, com Gerentes vinculados a duas Lojas diferentes, que cada um acessa somente sua Loja, seus Ativos e os dados relacionados permitidos.
- [x] 4.5 Implementar falha fechada para Gerente sem Loja válida e verificar que ele não obtém acesso global nem acesso a uma Loja informada pelo cliente.
- [x] 4.6 Aplicar ao Técnico o acesso de consulta necessário à fila, aos Ativos e à Telemetria da tratativa, sem níveis técnicos, e verificar que operações administrativas ou destrutivas são rejeitadas.
- [x] 4.7 Aplicar à Diretoria acesso global de consulta e verificar que alterações operacionais continuam rejeitadas.
- [x] 4.8 Proteger os CRUDs genéricos existentes com as mesmas verificações de perfil e escopo, verificando que nenhuma criação, alteração, exclusão ou consulta fora de escopo contorna a autorização.
- [x] 4.9 Verificar que `admin`, `tecnico_n1`, `tecnico_n2`, `tecnico_n3`, `diretor` e qualquer perfil desconhecido não recebem permissões de Gerente, Técnico ou Diretoria.

## 5. Regressão das automações e validação integrada

- [x] 5.1 Confirmar por diff que não houve alteração em Simulator, Fiscal, regras de heartbeat, SLA, chamados, telemetria ou dashboards além da aplicação de autorização às consultas destinadas a usuários.
- [x] 5.2 Executar teste de regressão do contrato de POST de telemetria usado pelo Simulator e verificar que o comportamento anterior à change foi preservado.
- [x] 5.3 Executar teste de regressão do contrato de verificação de heartbeat chamado pelo Fiscal e verificar que o comportamento anterior à change foi preservado.
- [x] 5.4 Executar a matriz completa de cenários das specs para acesso autenticado, anônimo, perfil indevido, operação indevida e isolamento entre Lojas, verificando os resultados esperados sem alteração parcial de dados.

## 6. Revisão e sincronização

- [x] 6.1 Validar todos os arquivos XanoScript alterados com o Xano Developer MCP e verificar que não restam erros de sintaxe ou referências inválidas.
- [x] 6.2 Revisar o diff final contra esta change e verificar que nenhum perfil, entidade, regra de negócio ou mecanismo de autenticação de automação fora do escopo foi introduzido.
- [x] 6.3 Após aprovação explícita do diff, sincronizar os recursos e a normalização dos usuários aprovados com o workspace Xano usando o Xano CLI, verificando que apenas os recursos e registros revisados foram alterados.
- [x] 6.4 Após confirmação administrativa das credenciais de teste no datasource `live`, executar os cenários de runtime e verificar login, identidade atual, negação por padrão, escopo do Gerente e preservação de Simulator e Fiscal no ambiente alvo.
