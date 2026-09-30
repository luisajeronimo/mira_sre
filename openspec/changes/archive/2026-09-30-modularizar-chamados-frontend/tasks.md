## 1. Preparação estrutural

- [x] 1.1 Inventariar páginas, States, helpers, guards, handlers e referências de importação das jornadas de Gerente e Técnico, preservando `app/services/service_desk.py` fora do escopo.
- [x] 1.2 Definir e criar a estrutura física mínima compatível com as convenções atuais, sem mover contratos HTTP, criar camadas artificiais ou remover legado.
- [x] 1.3 Verificar importação e compilação Reflex após a preparação, registrando qualquer decisão não coberta para revisão antes de prosseguir.

## 2. Migração da jornada de Gerente

- [x] 2.1 Mover para a área da jornada de Gerente suas páginas, State, handlers, guards e helpers específicos, sem alterar comportamento observável.
- [x] 2.2 Extrair para compartilhamento somente componentes apresentacionais ou helpers puramente determinísticos realmente usados por mais de uma jornada, com dados e callbacks explícitos.
- [x] 2.3 Ajustar imports da jornada de Gerente e verificar que suas rotas continuam resolvendo para os mesmos destinos.
- [x] 2.4 Executar testes existentes relevantes à jornada de Gerente e validar importação/compilação Reflex, equivalência de guards e chamadas backend, registrando os resultados reais.

## 3. Migração da jornada de Técnico

- [x] 3.1 Mover para a área da jornada de Técnico suas páginas, State, handlers, guards e helpers específicos, sem alterar comportamento observável.
- [x] 3.2 Reutilizar somente os elementos compartilhados que não conheçam perfil, escopo de Loja, autorização ou regras de negócio.
- [x] 3.3 Ajustar imports da jornada de Técnico e verificar que suas rotas continuam resolvendo para os mesmos destinos.
- [x] 3.4 Executar testes existentes relevantes à jornada de Técnico e validar importação/compilação Reflex, equivalência de guards e chamadas backend, registrando os resultados reais.

## 4. Consolidação de referências e remoção segura do legado

- [x] 4.1 Atualizar todas as referências e imports afetados, sem alterar `app/services/service_desk.py`, rotas, contratos HTTP, payloads ou autenticação.
- [x] 4.2 Inspecionar referências remanescentes aos módulos legados e remover cada trecho somente depois de comprovar que não há consumidor.
- [x] 4.3 Confirmar que componentes compartilhados não inferem perfil nem implementam autorização e que a autorização continua sob responsabilidade do Xano.

## 5. Validação final

- [x] 5.1 Executar os testes existentes relevantes e a importação/compilação Reflex, distinguindo resultados executados, falhas e bloqueios de ambiente.
- [x] 5.2 Verificar a resolução das rotas de Gerente e Técnico e a equivalência de guards, handlers e chamadas backend em relação ao comportamento anterior.
- [x] 5.3 Executar `git diff --check` e inspecionar o diff para confirmar ausência de alteração inesperada em rotas, permissões, autenticação, autorização, isolamento por Loja, status, prioridades, SLA, atribuição, fila, textos funcionais, payloads e contratos Xano.
- [x] 5.4 Executar a validação OpenSpec strict da change e registrar as evidências antes de solicitar revisão para Apply.
