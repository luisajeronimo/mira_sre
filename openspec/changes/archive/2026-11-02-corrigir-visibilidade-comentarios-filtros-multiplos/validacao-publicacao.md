# Preparação de validação e publicação

Revisão de 2026-11-02. Nenhuma publicação ou teste remoto mutável autorizado/executado nesta rodada. Este roteiro não comprova os resultados esperados.

## Estado das tasks abertas

| Tasks | Implementação local | Evidência ainda necessária |
|---|---|---|
| 1.1, 1.2, 1.4 | Escrita operacional sem visibilidade, DTO normalizado e consulta pública restrita implementados | Testes Xano com mocks completos e execução da versão nova; agrupamento visual já possui cobertura Python |
| 2.2, 2.4 | Snapshot completo, fallback exclusivo de JSON nulo, neutralização escalar e autorização implementados | Preparar testes Xano determinísticos de preferência; executar os casos abaixo na versão publicada, com usuários de teste autorizados |
| 2.3 | Cinco arrays, OR/AND, booleano separado, validação e ordenação implementados; sem defeito funcional identificado nesta inspeção | Completar mocks dos testes Xano existentes e novos casos múltiplos; confirmar no endpoint a desserialização de GET repetido e os resultados reais |
| 2.5 | Validação sintática anterior passou | Execução dos testes focados da versão nova, depois de completar a cobertura local; CLI remoto antes da publicação testa a versão anterior |
| 3.2 | Componente compila e possui guardas estruturais | Teste local em navegador de Tab, Espaço, Escape, retorno de foco e desabilitação; independe da publicação Xano |

Portanto, nenhuma task aberta depende **exclusivamente** de publicar e rodar os testes remotos atuais. Há preparação local de testes Xano e validação de teclado ainda pendentes. Não foram identificadas correções adicionais no código funcional nesta rodada.

## Inspeção específica da 2.3

- Endpoint autenticado transmite arrays tipados e deriva `usuarios_id` de `$auth.id`.
- Função exige Técnico/Diretoria/Administrador; `somente_atribuidos_a_mim` exige Técnico e restringe a query ao usuário autenticado.
- Status é normalizado por trim/lowercase para literal canônico e deduplicado. Prioridades exigem literal canônico. IDs são deduplicados, positivos, existentes; responsáveis exigem perfil Técnico.
- Cada coleção filtra por pertencimento; o resultado alimenta o próximo filtro, formando AND. Responsável usa IDs OR ausência quando o booleano é verdadeiro. Ausência de responsável inclui a representação interna legada zero; zero não é aceito no array público.
- Query mantém número, abertura e escopo rápido; atualização é filtrada depois. Ordenação e desempate são feitos antes dos filtros, sem reordenação posterior; total vem da lista final.
- A desserialização de parâmetros repetidos no servidor permanece sem evidência HTTP da versão nova. O cliente já tem teste local dessa serialização.
- Testes antigos `combina prioridade e responsável após query ordenada` e `filtra responsável sem predicado search dinâmico` informam ID 10, mas a nova leitura `db.get usuarios` não possui mock para esses cenários. Completar esses mocks antes de tratar a suíte Xano como determinística. Os getters/savers também precisam de cenários novos com mocks das leituras/escritas; guardas Python não substituem esses testes.

## Casos remotos preparados

Usar IDs reais de fixtures autorizadas: dois Técnicos T1/T2, dois usuários globais U1/U2 e Gerentes G1/G2 em Lojas L1/L2, Totens A1/A2 de L1 e A3 de L2. Nunca alterar usuários/roles ou histórico existente para preparar os testes. Fixtures persistentes ou writes de preferência/comentário exigem autorização específica para contas/dados de teste. Sem ela, executar apenas leituras e testes com mocks.

Para a listagem, selecionar registros estáveis conhecidos e registrar antes de testar: C1=(Novo,A1,L1,Alta,T1), C2=(Resolvido,A2,L1,Média,T2), C3=(Novo,A3,L2,Alta,sem responsável), C4=(Encerrado,A1,L1,Baixa,T2). Se não existirem, casos ficam bloqueados por fixture; não criar ou alterar chamados implicitamente.

| Caso | Estímulo | Resultado esperado |
|---|---|---|
| OR | GET global `status=Novo&status=Resolvido` | C1,C2,C3 entre as fixtures; sem duplicatas |
| AND | Acrescentar `loja_ids=L1&prioridades=Alta` | Apenas C1 entre as fixtures |
| Totens múltiplos | `ativo_ids=A1&ativo_ids=A2` | C1,C2,C4 entre as fixtures |
| Responsável misto | `responsavel_ids=T1&incluir_nao_atribuido=true` | C1,C3 entre as fixtures |
| Responsável vazio | Sem IDs, booleano true / false | Só não atribuídos / nenhuma restrição de responsável |
| Normalização | `status=%20novo%20&status=Novo` | Mesmo conjunto de Novo, sem duplicação |
| Valores inválidos | ID zero/negativo/inexistente; responsável Gerente; Status/Prioridade inválido | 422, sem consulta livre |
| Autorização | Gerente chama global; Diretoria pede atribuídos a mim; sem sessão | 403, 403, 401 respectivamente |
| Escopo rápido | Técnico T1 pede atribuídos a mim com responsável misto | Somente chamados de T1; o OR não amplia o escopo |
| Número/datas | Combinar múltiplos com número, limites de abertura e atualização | Interseção; fim semiaberto; intervalo invertido rejeitado |
| Ordenação | Para cada campo permitido, ASC/DESC, com e sem filtros | Sequência filtrada é subsequência da base na mesma ordem e desempate; total correto |
| Preferência completa | PUT global com todos arrays e booleano; GET; nova sessão | Mesmo snapshot canônico; rascunho não altera GET |
| Limpar | PUT listas vazias/false e demais critérios vazios; GET após login | Filtros vazios; escalares neutralizados; nada reaparece |
| Legado | Fixture com JSON null e escalares válidos | GET converte valores em listas unitárias; primeiro save grava JSON completo |
| JSON inválido | Mock de registro com JSON não nulo malformado | Erro de contrato; nenhum fallback escalar |
| Isolamento | U1 Todos, U1 Atribuídos a mim e U2 Todos com snapshots diferentes | Nenhum cruzamento; Diretoria/Admin não acessam escopo técnico |
| Gerente | PUT/GET Status e Totens múltiplos; Totem de L2 por G1 | Snapshot local; Totem externo 403 inclusive restauração |
| Filtro proibido | Gerente envia Loja/Prioridade/Responsável, inclusive array vazio | 422; Loja continua derivada da sessão |
| Visibilidade | Comentário público/interno; evento legado público/interno/sem visibilidade | Global: comentário conserva classificação, evento tem null; Gerente recebe só comentário explicitamente público |
| Eventos novos | Atribuir/reatribuir/liberar/Save em fixture autorizada | Evento sem visibilidade; comentário correlacionado conserva classificação; nenhum histórico reescrito |

Exemplo de consulta HTTP, com valores substituídos pelas fixtures, sem gravar credenciais em evidências:

```text
GET /tecnico/chamados?status=Novo&status=Resolvido&ativo_ids=A1&ativo_ids=A2&responsavel_ids=T1&incluir_nao_atribuido=true&ordenar_por=numero&direcao=DESC
```

Guardar por caso: versão/branch e hash local publicado, IDs das fixtures, request sem token, status HTTP, IDs retornados na ordem, resultado esperado/obtido. Classificar passou/falhou/bloqueado/não executado separadamente. Para testes CLI, confirmar que o script publicado corresponde ao local antes de atribuir evidência à change.

## Sequência segura proposta — depende de autorização futura

1. Completar testes Xano determinísticos e validar os scripts modificados no MCP. Validar teclado local. Conferir novamente diff e dry-run seletivo, branch `v1`, workspace `152692`, sem dados, variáveis de ambiente ou exclusões remotas.
2. Coordenar frontend e backend: arrays substituem contratos escalares. Impedir tráfego da aplicação durante a transição ou usar uma janela de manutenção; não presumir compatibilidade do frontend antigo com endpoints novos.
3. Publicar **primeiro somente** a tabela `preferencias_fila_chamados`, adicionando `filtros_multiplos` opcional, sem conversão/backfill. Usar seleção explícita do arquivo e dry-run correspondente antes do push. Confirmar campo remoto e preservação das colunas/índices atuais; fazer novo dry-run. Se falhar, não publicar funções dependentes.
4. Publicar as 10 funções e os 4 endpoints previstos em um lote seletivo com transação padrão, após dry-run revisado. Não publicar individualmente getter/save/listagem enquanto contratos estiverem inconsistentes. Endpoints GET de preferência já delegam às funções e não têm diff próprio.
5. Fazer novo dry-run completo; esperar zero alterações pendentes aprovadas e nenhuma alteração inesperada. Executar primeiro leituras/autorização/arrays/ordenação e testes com mocks; só depois, com fixtures autorizadas, persistência, Limpar e eventos/comentários. Liberar frontend correspondente e validar navegação, login, Aplicar/Limpar e teclado antes de retomar uso.
6. Se houver falha, suspender liberação e corrigir adiante. Não apagar JSON, remover campo, reverter schema ou restaurar dados históricos automaticamente. Não aceitar limitação nem marcar tasks sem evidência.

Os 15 recursos esperados são a tabela acima, as funções `assumir_chamado_tecnico`, `listar_chamados_gerente`, `listar_chamados_tecnico`, `listar_comentarios_publicos_gerente`, `obter_chamado_tecnico`, `obter_preferencia_fila_tecnica`, `obter_preferencia_filtros_gerente`, `salvar_preferencia_fila_tecnica`, `salvar_preferencia_filtros_gerente`, `validar_save_tratativa_chamado` (todas em `service_desk/`) e os endpoints `gerente/chamados GET`, `gerente/preferencias-fila PUT`, `tecnico/chamados GET`, `tecnico/preferencias-fila PUT`. UPDATE e ADD_FIELD da tabela contam como um recurso.


## Execução autorizada — 2026-11-02

O usuário autorizou explicitamente a publicação e as correções nos 15 recursos. Esta seção substitui o estado de preparação acima quanto à execução.

- Publicação: tabela primeiro (1 documento); verificação seletiva sem diferenças; depois lote de 10 funções/4 endpoints (14 documentos), transação padrão. Sem exclusões, records, env, backfill ou mudanças fora dos 15 recursos.
- Teclado real: seis checks passaram em Chrome headless/Playwright sobre harness Reflex prod importando `dropdown_multisselecao` original: Tab, abertura por Espaço, seleção, múltiplas seleções, Escape/retorno de foco e desabilitação.
- Leituras reais: Técnico 2, 18 chamados base; OR Novo/Resolvido retornou 15; AND Urgente retornou 12; responsável 2 OR nulo retornou 17; escopo atribuído ao Técnico 2 retornou 1; Gerente 9 no contrato global negado. Arrays de IDs comparados à base na mesma ordem, sem depender apenas das contagens.
- Persistência real: Técnico 2/Todos salvo com dois Status e relido; Limpar relido com coleções vazias; Técnico 2/Atribuídos a mim e Técnico 14/Todos permaneceram iguais. Snapshot original de Técnico 2/Todos restaurado e relido com igualdade.
- Gerente 9: gravação/leitura de dois Status, Limpar e restauração do snapshot original passaram.
- Visibilidade real: chamado 52/Loja 2 contém comentário Interno, Público e evento legado. Contrato global preservou as classificações dos comentários e retornou null no evento. Gerente 9 recebeu somente comentário Público; Gerente 13 de Loja externa foi negado. Histórico apenas lido.
- Validação local após alterações de testes: 54 testes focados passaram; OpenSpec strict e diff-check passaram. Não se repetiu a suíte extensa já aprovada.
- Primeiro lote remoto: 64/68 testes passaram; quatro falhas antigas no detalhe eram fixtures (chave mock de timeline divergente e campos Loja ausentes). Fixtures corrigidas no mesmo recurso autorizado e republicadas para repetição focada.
- Diferenças de serialização pós-push: quatro arquivos alinhados localmente às descrições/defaults omitidos pelo servidor; dry-run ficou sem diferenças antes da correção posterior das fixtures de detalhe.
- Não há credencial de login/sessão HTTP de usuário disponível no ambiente. Chamadas reais foram pelo debugger de funções autorizado do CLI; isso não comprova a desserialização HTTP de GET repetido nem as respostas HTTP autenticadas 422 dos endpoints Gerente. Esses critérios permanecem pendentes até validação com sessão no Reflex/API; não confundir com os testes do cliente e das funções.

- Resultado consolidado final: **68/68 testes remotos focados, 113 asserções**, com rerun 4/4 após corrigir fixtures. Dry-run final **sem diferenças**. MIRA Reviewer: **aprovado**, mantendo explicitamente a validação HTTP pendente. Tasks concluídas 14/16.
