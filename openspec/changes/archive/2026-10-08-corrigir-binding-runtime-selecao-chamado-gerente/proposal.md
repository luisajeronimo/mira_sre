# Proposal

## Why

Na abertura manual de chamados pelo Gerente, o handler `abrir_chamado` recebia o payload do evento de clique do DOM (`_e`, contendo propriedades de mouse como `button`, `buttons`, `clientX`, etc.) no parâmetro `form_data`. Como `form_data` chegava preenchido com esse dicionário do clique, a verificação `form_data or {...}` avaliava para o dicionário do clique em vez de ler as variáveis do State (`self.ativo_formulario` e `self.categoria_formulario`). Como consequência, o salvamento no navegador sempre rejeitava a submissão com a mensagem "Selecione um ativo e uma categoria.", mesmo com o Ativo e a Categoria visualmente selecionados e sincronizados no State.

## What Changes

- Ajustar o handler `abrir_chamado` e a invocação do botão "Salvar" para que a submissão consuma estritamente as propriedades de seleção mantidas no State do formulário, desconsiderando payloads de evento de clique.
- Garantir que `abrir_chamado` leia `self.ativo_formulario`, `self.categoria_formulario`, `self.prioridade_formulario`, `self.titulo_formulario` e `self.descricao_formulario` ao ser acionado pelo clique do botão de salvar.
- Adicionar teste automatizado de regressão que valide o comportamento quando um payload de evento de clique for entregue ao handler, comprovando que o State prevalece e o payload numérico de domínio é montado com sucesso.
- Validar o fluxo ponta a ponta no navegador autenticado antes de qualquer consolidação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `chamados-abertura-manual`: o salvamento manual por clique de botão deve consumir os identificadores selecionados no State e não interpretar eventos de clique do DOM como dados de formulário.

## Impact

- `app/chamados/gerente/state.py`: handler `abrir_chamado` consome o State e ignora payloads de clique.
- `app/chamados/gerente/pages.py`: ligação do botão "Salvar".
- `tests/test_gerente_lista_state.py`: testes de regressão com clique e dados do State.
- Nenhuma alteração em Xano, schema, records, banco ou APIs remotas.
