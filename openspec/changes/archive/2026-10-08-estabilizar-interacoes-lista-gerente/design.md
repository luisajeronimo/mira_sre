# Design

## Diagnóstico

O caminho de uma interação é:

`alternar_ordenacao/aplicar_filtros → carregar_lista → cliente Service Desk`.

`_garantir_gerente` reutiliza a sessão já confirmada e não chama `/me` em cada
ordenação. O cliente centralizado transforma timeout, conexão e 5xx em
indisponibilidade; antes desta change, 429 caía no erro genérico de contrato.
Os logs locais disponíveis mostram falhas do websocket do Reflex e uma
asserção do `StaticFiles`; não há registro confiável de 429 HTTP. A solução,
portanto, corrige a fronteira de tratamento sem afirmar que 429 foi observado
em produção.

## Decisões

### 1. Limite HTTP explícito

`XanoRateLimitado` herda de `XanoIndisponivel`, mantém a mensagem sanitizada e
expõe somente um número opcional derivado de `Retry-After`. A camada de State
trata-o como falha transitória, não como autenticação e não inicia retry
automático.

### 2. Uma carga por vez, intenção mais recente

`carregar_lista` usa `carregando_chamados` como exclusão mútua. Uma chamada
concorrente marca `consulta_chamados_pendente`; quando a carga atual termina
com sucesso, somente uma nova consulta com os critérios atuais é executada.
Se a carga falhar, o pending não provoca retry imediato: a próxima ação
explícita recupera a lista, evitando request storm e loops de 429.

### 3. Catálogo de ativos independente

`GET /gerente/ativos` é carregado apenas quando o State ainda não possui o
catálogo. Ordenações e filtros posteriores consultam somente
`GET /gerente/chamados`. Se a carga inicial do catálogo falhar, a lista de
chamados bem-sucedida permanece utilizável e a falha é sanitizada.

### 4. Segurança da sessão

401 continua limpando a sessão e redirecionando ao login. 403, 429, timeout,
conexão, 5xx e contrato incompatível preservam token, identidade e perfil já
confirmados. O loading sempre é encerrado em `finally`.

## Limitações observadas

O conector de navegador disponível durante a investigação não ofereceu uma
aba ativa para correlacionar requests HTTP reais. A evidência de status é,
portanto, automatizada: 429 é classificado explicitamente e os logs locais
registram falha de websocket, sem atribuí-la a Xano.
