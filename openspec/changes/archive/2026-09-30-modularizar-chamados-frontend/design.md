## Contexto

O frontend de Chamados reúne atualmente, nos mesmos módulos, as jornadas de Gerente e Técnico, seus States, helpers de transformação, guards e tratamento de erro. A separação pretendida é interna ao Reflex: o comportamento consolidado, as rotas e o adaptador HTTP já existente devem ser preservados.

As specs consolidadas de Chamados continuam sendo a fonte de comportamento. Esta change não cria delta specs porque não propõe mudança funcional legítima.

## Objetivos e não objetivos

**Objetivos:**

- Organizar o código de Chamados por capacidade e jornada, com fronteiras compreensíveis entre Gerente e Técnico.
- Manter responsabilidades de páginas, State, componentes compartilhados, helpers puros e adaptador HTTP separadas.
- Permitir migração e validação incremental sem alterar contratos ou comportamento observável.

**Não objetivos:**

- Criar uma arquitetura de camadas nova ou uma árvore rígida desvinculada das convenções atuais.
- Alterar `app/services/service_desk.py`, os contratos Xano, rotas, payloads, autenticação, autorização ou regras de negócio.
- Fazer componentes compartilhados inferirem perfil, escopo de Loja ou autorização.

## Decisão técnica

### Módulos por capacidade e jornada

O alvo mínimo seguirá as convenções existentes do projeto e separará os elementos específicos de cada jornada de Chamados:

- páginas de Gerente ficam responsáveis pela composição e navegação da jornada de Gerente;
- páginas de Técnico ficam responsáveis pela composição e navegação da jornada de Técnico;
- cada jornada mantém seu State, handlers, guards e mapeamento de falhas que já lhe pertencem;
- componentes realmente comuns ficam em local compartilhado somente quando recebem dados e callbacks explícitos, sem conhecer perfil ou autorização;
- helpers determinísticos de transformação e formatação ficam como funções puras compartilhadas quando não pertencem a uma jornada;
- `app/services/service_desk.py` continua como adaptador HTTP único e inalterado nesta change.

A estrutura física exata será o menor recorte compatível com essas responsabilidades e com as convenções já presentes no repositório. Ela não deve introduzir camadas artificiais, registries, abstrações genéricas ou duplicação de contratos apenas para atender à organização.

### Dependências permitidas e prevenção de acoplamento

Páginas dependem do State e de componentes de sua própria jornada, além de componentes compartilhados estritamente apresentacionais. States dependem do adaptador HTTP existente e de helpers puros necessários. Helpers puros não dependem de páginas, State, sessão ou I/O.

Dependências cruzadas entre as jornadas devem ser evitadas. Um elemento só será compartilhado quando sua responsabilidade for a mesma para ambas e puder ser expressa sem condicional de perfil, regra de negócio, filtro de dados ou autorização. Autorização permanece no Xano; a proteção visual existente não ganha função autorizadora.

### Preservação de contratos

A migração deve preservar, sem adaptação de semântica:

- rotas e sua resolução atual;
- handlers e guards de cada jornada;
- chamadas ao adaptador HTTP, URL base, token backend-only, payloads e tratamento de falhas;
- dados exibidos, estados de carregamento, vazio e erro, bem como textos funcionais já consolidados.

`app/services/service_desk.py` está explicitamente fora do escopo. Não há evidência nesta Propose para justificar mudança estrutural mínima nele; qualquer necessidade descoberta no Apply deve retornar para revisão antes de alterar esse arquivo.

## Plano de migração

1. Criar a estrutura mínima de destino e mover apenas elementos sem alteração semântica.
2. Migrar primeiro a jornada de Gerente, mantendo temporariamente referências necessárias e validando imports, compilação Reflex, rotas, guards e chamadas.
3. Migrar a jornada de Técnico sob os mesmos critérios.
4. Consolidar imports e referências para os módulos resultantes.
5. Localizar referências remanescentes e remover o legado apenas quando não houver consumidor.
6. Executar validação final de regressão e inspeção do diff para confirmar que a mudança permaneceu estrutural.

## Riscos e mitigação

- Movimentações parciais podem deixar referências quebradas: cada jornada será validada antes da próxima.
- Extrações podem alterar a ordem de handlers ou guards: a equivalência será conferida contra a implementação anterior e testes relevantes.
- Compartilhamento excessivo pode acoplar perfis: componentes comuns serão limitados à apresentação e callbacks explícitos.
- Um diff de refatoração pode ocultar mudança funcional: a revisão final conferirá rotas, contratos, payloads, guards, textos e chamadas backend.
