# Simplificar listagens e histórico dos chamados

## Why

IDs internos expostos nos filtros e seletores aumentam o ruído das listagens. No detalhe do chamado, o seletor de visibilidade ocupa espaço excessivo, e o histórico repete autoria e acumula caixas e bordas que dificultam a leitura.

## What Changes

- Exibir nomes sem IDs de Técnicos na fila de chamados e de Totens e Lojas nas listagens, filtros e seletores onde esses IDs aparecem.
- Preservar os identificadores internos, as preferências e os valores enviados aos contratos, inclusive para nomes repetidos.
- Colocar um seletor compacto de visibilidade acima do comentário, conforme confirmação explícita do usuário, preservando Público obrigatório quando aplicável.
- Simplificar o histórico com Impeccable no modo Operate: cards compactos, diferenças sem caixas internas e metadados com hierarquia clara.
- Apresentar uma única autoria quando evento e comentário correlacionado têm o mesmo autor; preservar autoria distinta e a classificação exclusiva do comentário.

O número do chamado, os nomes de domínio e os códigos de identificação dos equipamentos permanecem como recebidos. Não há mudança em permissões, regras de tratativa, APIs, banco ou histórico persistido. O trabalho ocorre somente no dev local, sem README novo, publicação, Archive, commit ou push antes do teste humano.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `frontend-sessao-navegacao`: nomes legíveis nas listagens e seletores, sem exposição dos IDs internos de Técnico, Totem ou Loja.
- `chamados-fila-atribuicao-tecnica`: composição compacta de comentário e histórico, com autoria sem repetição e preservação dos fatos.

## Impact

Componentes de filtros em `app/components/visual.py`, páginas de chamados, apresentação da timeline em `app/chamados/`, rótulos dos indicadores e estilos locais em `assets/mira.css`. Testes locais preservam IDs nos eventos e contratos e cobrem a correlação da autoria. Validação visual usa os componentes reais em uma prévia isolada com dados fictícios, seguida do dev normal para teste do usuário.

## Decisão humana

O usuário solicitou expressamente os ajustes visuais e confirmou o seletor compacto acima do comentário. O escopo de implementação é essa apresentação, sem nova decisão de domínio ou arquitetura. Archive e commit aguardam novo pedido após o teste.
