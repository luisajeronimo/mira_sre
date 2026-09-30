## Why

`app/states/chamados.py` e `app/pages/chamados.py` concentram hoje as jornadas de Chamados de Gerente e Técnico, além de helpers, guards e tratamento de falhas. Essa concentração torna a evolução e a revisão das duas jornadas mais difíceis, pois uma mudança estrutural em uma delas pode afetar referências da outra sem que isso fique evidente.

## What Changes

- Reorganizar incrementalmente o frontend de Chamados por capacidade e jornada, separando a implementação de Gerente da implementação de Técnico.
- Manter páginas, State, componentes compartilhados e helpers puros com responsabilidades explícitas e dependências direcionadas.
- Preservar o adaptador HTTP existente em `app/services/service_desk.py` e todos os seus contratos.
- Migrar e validar uma jornada por vez, removendo código legado somente depois de não haver referências a ele.

Esta é uma change exclusivamente estrutural. Ela não altera requisitos funcionais, rotas, permissões, autenticação, autorização, isolamento por Loja, status, prioridades, SLA, atribuição, fila, textos funcionais, payloads nem contratos Xano. Portanto, não há delta specs: as specs consolidadas vigentes permanecem preservadas.

## Scope

- Estrutura interna do frontend Reflex relacionada às jornadas de Chamados de Gerente e Técnico.
- Responsabilidades e imports entre páginas, State, componentes compartilhados e helpers puros já existentes.
- Testes e verificações de regressão necessários para demonstrar preservação comportamental durante a migração.

## Out of Scope

- Alterar `app/services/service_desk.py`, contratos HTTP, rotas ou payloads.
- Alterar regras de negócio, autenticação, autorização ou qualquer recurso Xano.
- Criar funcionalidades, perfis, telas, redesign, dashboards, administração, Bot de Fiscalização, comentários, histórico ou alterações de SLA.
- Alterar testes, documentação global ou código fora do necessário para a futura implementação aprovada.

## Impact

- **Reflex:** organização interna das jornadas de Chamados, preservando a interface pública e a resolução atual das rotas.
- **Xano e Service Desk:** nenhum impacto planejado; continuam como autoridade para contratos, autenticação, autorização e regras de negócio.
- **Compatibilidade:** chamadas ao backend, guards, estados de carregamento e erro, textos funcionais e comportamento observável devem permanecer equivalentes.

## Risks

- [Referência incompleta] Um import ou handler pode continuar apontando para estrutura antiga → migrar por jornada, inspecionar referências e só remover legado sem consumidores.
- [Regressão de guarda] Uma extração pode alterar inadvertidamente a ordem ou a aplicação de guards → validar equivalência de guards, handlers, rotas e chamadas backend por jornada.
- [Acoplamento novo] Componentes compartilhados podem passar a conhecer perfil ou autorização → limitar seu papel à apresentação e dados recebidos; decisões de acesso permanecem no Xano e nas jornadas existentes.
- [Mudança funcional acidental] Uma reorganização pode modificar texto, payload ou estado observável → usar testes existentes, compilação/importação Reflex e inspeção explícita do diff antes de concluir cada etapa.

## Estratégia incremental

1. Preparar o alvo estrutural mínimo, sem remover a implementação atual.
2. Migrar a jornada de Gerente e validar que rotas, guards e chamadas continuam equivalentes.
3. Migrar a jornada de Técnico e repetir a validação de equivalência.
4. Ajustar imports e referências entre os módulos resultantes.
5. Remover o legado somente quando a inspeção confirmar ausência de referências.
6. Executar as validações finais e revisar o diff quanto à ausência de mudança funcional inesperada.

## Decisões pendentes

Não há decisão funcional, de contrato, autorização ou modelo de dados nesta Propose. A passagem para Apply exige revisão humana dos artefatos e da estratégia estrutural descrita.
