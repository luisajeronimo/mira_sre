# Limitação observada no XanoScript Language Server

## Objetivo

Registrar o comportamento observado na extensão XanoScript Language Server
0.3.3 ao resolver aliases de `JOIN` em expressões `$db`.

## Evidências observadas

Foram reproduzidos avisos `Unknown table` em referências a aliases de `JOIN`,
incluindo:

- `ativo`;
- `loja`;
- `categoria`;
- `solicitante`;
- `tecnico`.

Esses nomes são aliases de `JOIN`, não tabelas físicas. Na reprodução local, o
parser não identificou erros de sintaxe, mas o scanner de referências tratou
os aliases como nomes de tabelas reais. O comportamento apareceu, entre
outras, nas funções:

- `xano/function/service_desk/obter_chamado_solicitante.xs`;
- `xano/function/service_desk/obter_chamado_tecnico.xs`;
- `xano/function/service_desk/obter_chamado_gerente.xs`.

Esta evidência descreve a versão e a reprodução local examinadas; não afirma
que toda versão da extensão ou todo analisador Xano tenha a mesma limitação.

## Decisão técnica

1. Preservar os `JOIN`s e aliases existentes quando estiverem corretos segundo
   o contrato e os padrões utilizados pelo projeto.
2. Não substituir `JOIN`s por consultas `db.get` apenas para eliminar esses
   avisos.
3. Não renomear aliases sem justificativa funcional ou evidência de que a
   sintaxe está incorreta.
4. Não alterar a lógica de resolução histórica da Loja para contornar avisos
   do analisador.
5. Não interpretar esses avisos isoladamente como prova de erro de sintaxe,
   referência inválida no Xano ou falha em runtime.
6. Reavaliar a limitação após atualização da extensão ou quando uma validação
   oficial demonstrar que é necessária uma mudança.

## Cuidados na validação

- Distinguir avisos do scanner de referências de erros de sintaxe reportados
  pelo parser.
- Confirmar localmente que os nomes referenciados são aliases declarados nos
  respectivos `JOIN`s e que as tabelas físicas e os campos correspondentes
  existem no workspace local.
- Tratar a inspeção da extensão como evidência sobre o editor, não como
  validação de compatibilidade com o workspace remoto nem como teste de
  execução.
- Quando necessário, validar sintaxe, referências e comportamento por meio
  dos mecanismos oficiais e autorizados do Xano. A validação remota não deve
  ser substituída por inferência a partir dos avisos do editor.
- Não publicar alterações no Xano apenas para testar se os avisos
  desaparecem.

## Exceção registrada: alias `tecnico_usuario` em `obter_chamado_tecnico`

- **O que mudou:** o alias do `JOIN` com `usuarios` passou de `tecnico` para `tecnico_usuario`. A troca foi feita em uma sessão de agente em 2026-11-08 (checkpoint `082bda0`), depois deste documento, sem justificativa registrada, e publicada no Xano com autorização no mesmo dia.
- **Efeito sobre os avisos:** nenhum. `tecnico_usuario` também não é tabela, e a função usa outros aliases (`ativo`, `autor`, `categoria`, `loja`, `solicitante`, `tecnico_anterior`, `tecnico_novo`) que geram o mesmo aviso.
- **Contrato:** inalterado. O `eval` continua produzindo `tecnico_usuario_id` e `tecnico_nome`, que `construir_dto_chamado_tecnico` transforma em `tecnico: {id, nome}`; nenhum consumidor depende do nome interno do alias.
- **Evidência de runtime (2026-11-08):** E2E somente leitura `test_detalhe_tecnico_com_responsavel_preenche_dto_tecnico` aprovado: o detalhe de chamado com Técnico atribuído devolve `tecnico {id, nome}` igual ao da fila.
- **Decisão:** manter como publicado. Não reverter apenas por causa dos avisos do Language Server nem publicar só para renomear; a regra 3 deste documento continua valendo para novas alterações.
