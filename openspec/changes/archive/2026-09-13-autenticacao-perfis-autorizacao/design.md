## Context

Ver `proposal.md` para a motivação. O snapshot local possui a tabela `usuarios` com `auth = false`, perfis que não correspondem ao domínio oficial e CRUDs de entidades sem verificações locais de identidade ou perfil. O frontend Reflex ainda não está implementado, de modo que esta change deve estabilizar primeiro o contrato de segurança no Xano.

As capacidades `autenticacao-usuarios` e `autorizacao-perfis` exigem uma mudança de modelo, endpoints de autenticação e proteção transversal das APIs destinadas aos usuários. Os endpoints usados pelo Simulator e pelo Fiscal não serão alterados.

## Goals / Non-Goals

**Goals:**

- Usar a autenticação nativa do Xano sobre a identidade de usuário do MIRA.
- Representar somente Gerente, Técnico e Diretoria como perfis oficiais.
- Fornecer ao Reflex um contrato mínimo de login e identidade atual.
- Aplicar no backend uma política de negação por padrão e escopo por unidade para o Gerente.
- Impedir que CRUDs genéricos ampliem as permissões documentadas dos perfis.
- Planejar uma migração limitada ao mapeamento de perfis explicitamente aprovado.

**Non-Goals:**

- Implementar a tela de login, navegação ou proteção de rotas no Reflex.
- Criar cadastro público, signup, fluxo público de recuperação/reset de senha ou administração geral de usuários.
- Implementar provisionamento ou alteração de senha como funcionalidade do MIRA; a preparação das credenciais pertence à administração do ambiente Xano.
- Criar perfil administrador ou níveis de Técnico.
- Definir estados, transições ou regras de chamado.
- Alterar heartbeat, SLA, telemetria, dashboards, Simulator ou Fiscal.
- Escolher uma política de autenticação para processos automatizados.

## Decisions

### 1. Usar a tabela `usuarios` como identidade autenticável do Xano

A tabela existente será habilitada para o mecanismo nativo de autenticação do Xano. O material de credencial será armazenado e validado pelo próprio Xano; ele não será retornado pelas APIs nem manipulado como atributo de negócio pelo Reflex.

O contrato mínimo destinado ao Reflex será composto por:

- uma operação de login que recebe as credenciais aceitas pelo Xano e retorna o token de autenticação;
- uma operação de identidade atual que valida o token e retorna `id`, `nome`, `email`, perfil oficial e, para Gerente, a identificação da unidade associada;
- erros de autenticação que não distinguem publicamente usuário inexistente de senha incorreta.

O token emitido pelo login terá expiração de 8 horas, configurada no mecanismo nativo do Xano. Esta change não introduz refresh token, renovação automática nem qualquer outra política de sessão.

Não haverá autorregistro. A preparação das credenciais dos usuários já existentes será realizada administrativamente no ambiente Xano e permanece fora das funcionalidades do MIRA; criação de usuários e administração geral continuam fora do escopo.

**Alternativas consideradas:**

- Criar uma tabela de autenticação separada: rejeitada porque duplicaria a identidade já representada por `usuarios` e exigiria sincronização adicional.
- Implementar credenciais no Reflex: rejeitada porque viola a divisão de responsabilidades do projeto.
- Introduzir refresh token ou renovação automática: rejeitada porque não faz parte da política de sessão aprovada para esta change.

### 2. Normalizar os três perfis oficiais pelo mapeamento aprovado

O modelo persistirá somente os valores canônicos `gerente`, `tecnico` e `diretoria`, correspondentes diretamente aos três perfis do domínio. A revisão humana aprovou o seguinte mapeamento dos registros existentes:

- `tecnico_n1`, `tecnico_n2` e `tecnico_n3` para `tecnico`;
- `diretor` para `diretoria`;
- `gerente` permanece `gerente`.

Esse mapeamento é uma migração de dados, não a preservação de aliases ou níveis técnicos. Depois da migração, somente os três valores canônicos serão aceitos. `admin` e qualquer valor não incluído no mapeamento continuam sem conversão e exigem decisão humana antes da continuidade.

**Alternativas consideradas:**

- Preservar níveis técnicos ou `diretor` como aliases permanentes: rejeitada porque manteria perfis não oficiais no mecanismo de autorização.
- Manter os valores legados como aliases: rejeitada porque manteria perfis não oficiais no mecanismo de autorização.

### 3. Representar a unidade do Gerente com uma referência direta para Loja

**Decisão proposta para aprovação humana:** adicionar `lojas_id` à identidade `usuarios` como referência opcional à tabela `lojas`, exigida pelas operações dependentes de unidade quando o perfil for Gerente. Técnico e Diretoria não usarão esse campo para determinar seu escopo.

Esta proposta representa uma associação de um Gerente com uma Loja. Ela é a opção mais simples compatível com a formulação atual “Gerente da Loja” e com o escopo acadêmico. Um Gerente sem referência válida falha de forma fechada: não recebe acesso a nenhuma unidade.

Esta decisão deve ser aceita na revisão da change antes do Apply. Caso o requisito real seja permitir múltiplas unidades por Gerente, a proposta, as specs e as tarefas devem ser revisadas antes da implementação.

**Alternativas consideradas:**

- Tabela associativa Gerente-Loja: permite múltiplas unidades, mas adiciona uma cardinalidade que não está definida no domínio atual.
- Unidade informada pelo Reflex ou armazenada apenas no token: rejeitada como fonte de autorização, pois permitiria divergência em relação aos dados persistidos no Xano.

### 4. Centralizar autenticação e autorização no Xano

As APIs destinadas a usuários terão autenticação obrigatória e reutilizarão verificações centralizadas para:

1. validar o token e obter o usuário;
2. rejeitar perfis não oficiais;
3. verificar se a operação está permitida ao perfil;
4. aplicar o escopo de Loja quando o perfil for Gerente;
5. retornar somente depois dessas verificações.

Filtros enviados pelo cliente nunca serão usados como prova de autorização. Para o Gerente, o identificador da Loja será obtido da identidade autenticada, e consultas relacionadas a Ativo ou Chamado validarão sua relação com essa Loja no Xano.

**Alternativas consideradas:**

- Repetir verificações independentes em cada endpoint: rejeitada pelo risco de divergência e omissão.
- Aplicar autorização somente no Reflex: rejeitada porque a chamada direta à API continuaria possível.

### 5. Adotar uma matriz mínima de acesso derivada do domínio

| Perfil | Consultas autorizáveis nesta fundação | Alterações autorizáveis nesta fundação |
|---|---|---|
| Gerente | própria Loja, seus Ativos e dados relacionados que contratos funcionais permitirem acompanhar | nenhuma mutação genérica; a abertura manual será definida em change própria |
| Técnico | fila de Chamados e informações de Ativo e Telemetria necessárias à tratativa | nenhuma mutação genérica; assumir, tratar e resolver serão definidos em change própria |
| Diretoria | consultas globais previstas para acompanhamento e indicadores | nenhuma alteração operacional |

A matriz define limites de autorização, mas não cria endpoints funcionais ainda inexistentes. Quando uma operação de negócio for introduzida por outra change, ela deverá declarar qual célula da matriz a autoriza.

Os endpoints genéricos de criação, alteração e exclusão não serão tratados como permissões implícitas. Enquanto não houver uma operação funcional aprovada, serão protegidos de modo que nenhum dos três perfis os utilize para administrar dados arbitrariamente.

### 6. Diferenciar falhas de autenticação e autorização

Uma requisição sem identidade válida será rejeitada como não autenticada. Uma identidade válida que não possua permissão ou escopo será rejeitada como não autorizada. Em ambos os casos, a resposta não deverá revelar dados protegidos nem executar parcialmente a operação.

Essa distinção permite ao Reflex tratar expiração de sessão separadamente de falta de permissão, sem deslocar a decisão de acesso para o frontend.

### 7. Preservar explicitamente os contratos das automações

A proteção será aplicada por uma lista explícita de APIs destinadas a usuários, não por uma alteração indiscriminada de todo o grupo de APIs. O POST de telemetria usado pelo Simulator e a verificação de heartbeat disparada pelo Fiscal permanecerão com seus contratos atuais.

Essa preservação não afirma que os endpoints das automações sejam seguros de forma definitiva; apenas evita ampliar esta change sem requisito aprovado. Uma futura avaliação poderá propor autenticação de máquina separadamente.

## Risks / Trade-offs

- **[Bloqueio de usuários existentes]** Valores fora do mapeamento aprovado ou credenciais não preparadas podem impedir login -> auditar os registros, aplicar somente o mapeamento aprovado e interromper diante de qualquer outro valor.
- **[Gerente associado incorretamente]** Uma Loja errada amplia ou reduz acesso -> exigir referência válida, testar isolamento entre duas Lojas e revisar os vínculos antes de habilitar as APIs.
- **[Proteção incompleta]** Um CRUD genérico esquecido pode contornar a política -> manter inventário explícito de endpoints e testes negativos para acesso anônimo, perfil indevido e outra unidade.
- **[Regressão nas automações]** Proteção aplicada ao grupo inteiro pode interromper Simulator ou Fiscal -> preservar por rota e verbo os contratos automatizados e verificá-los sem alterar seus comportamentos.
- **[Divergência entre repositório e Xano]** O workspace remoto pode conter configurações ou dados ausentes localmente -> comparar o estado remoto antes do Apply e revisar o diff antes de sincronizar.
- **[Escopo de uma única Loja]** A referência direta não atende múltiplas unidades por Gerente -> revisar esta decisão agora; uma necessidade futura de múltiplas Lojas exigirá nova change.
- **[Ausência inicial de interface]** A autenticação poderá ser validada por API antes de existir Reflex -> documentar claramente o contrato e deixar a integração visual para a change de frontend.

## Migration Plan

1. Consultar o estado remoto do Xano e produzir um inventário dos usuários, perfis e endpoints afetados, sem alterar dados.
2. Confirmar na revisão humana a referência direta `usuarios.lojas_id` e a cardinalidade de uma Loja por Gerente.
3. Criar um ponto de recuperação do estado Xano antes de alterações de modelo ou endpoints.
4. Auditar valores de perfil existentes e preparar a normalização aprovada: níveis `tecnico_n1`, `tecnico_n2` e `tecnico_n3` para `tecnico`, `diretor` para `diretoria` e manutenção de `gerente`; interromper diante de qualquer outro valor.
5. Adicionar e preencher a associação de Loja dos Gerentes antes de ativar a restrição de escopo.
6. Habilitar a autenticação nativa da tabela, sem registrar segredos no repositório; a preparação das credenciais será feita administrativamente no ambiente Xano, fora das funcionalidades desta change.
7. Criar e validar os contratos de login e identidade atual.
8. Aplicar as verificações centralizadas às APIs destinadas a usuários e bloquear mutações genéricas não autorizadas.
9. Executar cenários de autenticação, dos três perfis, de isolamento entre Lojas e de acesso direto indevido após a confirmação administrativa das credenciais no datasource `live`.
10. Confirmar que o POST do Simulator e o disparo do Fiscal mantêm seus contratos anteriores.
11. Apresentar o plano de alteração e o diff para revisão humana antes de qualquer alteração remota.
12. Revisar e sincronizar o Xano somente após validação do XanoScript e aprovação explícita do diff.

Em caso de rollback, restaurar o snapshot dos recursos Xano afetados e reverter a proteção dos endpoints como um conjunto. Dados de associação adicionados não devem ser apagados automaticamente; devem permanecer disponíveis para uma nova tentativa ou ser tratados por uma decisão operacional explícita.
