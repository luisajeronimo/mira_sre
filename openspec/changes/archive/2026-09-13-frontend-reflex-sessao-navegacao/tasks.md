## 1. Preparação da aplicação Reflex

- [x] 1.1 Confirmar no snapshot local os contratos de `POST /login` e `GET /me` consumidos pela change e verificar que seus campos, autenticação e respostas correspondem às specs consolidadas sem editar arquivos XanoScript.
- [x] 1.2 Criar o módulo de entrada e os arquivos de pacote da aplicação Reflex nas pastas `app/components`, `app/pages`, `app/services` e `app/states`, verificando que a aplicação pode ser importada pelo Python sem módulos ausentes.
- [x] 1.3 Adicionar a configuração mínima do projeto Reflex e as dependências diretas do cliente HTTP assíncrono e dos testes, verificando que a instalação resolve versões compatíveis com `reflex==0.9.7`.
- [x] 1.4 Documentar em `.env.example` `XANO_AUTH_BASE_URL` separadamente de `XANO_BASE_URL` e o timeout do cliente Xano com valores não sensíveis, verificando que nenhuma credencial ou token foi versionado e que a base operacional existente foi preservada.

## 2. Cliente HTTP centralizado do Xano

- [x] 2.1 Definir os modelos de resposta e os erros diferenciados de credenciais, autenticação, autorização, contrato inválido e indisponibilidade, verificando por testes que cada categoria pode ser tratada sem expor o corpo sensível da resposta.
- [x] 2.2 Implementar a criação centralizada do cliente assíncrono com `XANO_AUTH_BASE_URL` normalizada e timeout, verificando que configuração ausente falha explicitamente, que `XANO_BASE_URL` não é reutilizada para autenticação e que nenhuma URL específica fica embutida no código.
- [x] 2.3 Implementar as operações de login e identidade atual, verificando com cliente simulado que `POST /login` envia somente `email` e `senha`, que `GET /me` usa o cabeçalho de autenticação esperado e que nenhuma resposta publica senha ou token fora do retorno interno do serviço.
- [x] 2.4 Implementar a classificação uniforme dos status e falhas de transporte, verificando por testes que rejeição de autenticação, rejeição de autorização, timeout, conexão e erro temporário de servidor resultam em erros distintos.

## 3. Estado e ciclo de vida da sessão

- [x] 3.1 Criar o State de autenticação com token em variável backend-only, identidade pública tipada e estados apresentáveis de carregamento e erro, configurando o gerenciador de State em memória e verificando na compilação e por introspecção que o token não é uma Var sincronizada com o frontend, não é gravado em `.states` e não usa `LocalStorage`, `SessionStorage`, cookie próprio ou refresh token.
- [x] 3.2 Implementar o evento de login com bloqueio de envio concorrente e confirmação obrigatória por `/me`, verificando por testes que a sessão só é publicada após identidade oficial válida e que credenciais rejeitadas produzem uma mensagem genérica.
- [x] 3.3 Implementar a revalidação da sessão por `/me`, verificando por testes que token ausente, inválido ou expirado limpa a sessão, que a perda ou reinício do State exige nova autenticação mesmo antes de oito horas e que indisponibilidade temporária preserva uma sessão já existente sem apresentar conteúdo não revalidado.
- [x] 3.4 Implementar o tratamento compartilhado de negação de autorização, verificando que uma resposta não autorizada mantém token e identidade e não é apresentada como expiração.
- [x] 3.5 Implementar a resolução do destino inicial para `gerente`, `tecnico` e `diretoria`, verificando por testes que cada perfil resulta respectivamente em `/gerente`, `/tecnico` e `/diretoria` e que qualquer identidade fora do contrato falha de forma fechada.
- [x] 3.6 Implementar logout local, verificando que token, identidade e estado transitório são descartados antes do redirecionamento para `/login` e não reaparecem em um carregamento protegido subsequente.

## 4. Páginas, componentes e navegação

- [x] 4.1 Implementar a tela pública de login com formulário de e-mail e senha, indicador de processamento e mensagem de erro, verificando no navegador que a senha não é preservada após a tentativa e que o formulário não pode ser reenviado enquanto estiver carregando.
- [x] 4.2 Implementar os componentes reutilizáveis da casca autenticada com identidade pública, rótulo do perfil, destino de início e logout, verificando que nenhum componente recebe ou renderiza token.
- [x] 4.3 Criar as páginas neutras `/gerente`, `/tecnico` e `/diretoria`, verificando que não contêm links, consultas ou ações de Service Desk, fila, tratativa, dashboards ou indicadores.
- [x] 4.4 Criar a rota `/` e registrar todas as páginas no aplicativo Reflex, verificando na compilação que `/`, `/login`, `/gerente`, `/tecnico` e `/diretoria` estão disponíveis sem rotas duplicadas.
- [x] 4.5 Aplicar o guard compartilhado aos eventos de carregamento das páginas protegidas, verificando que visitante anônimo vai para `/login`, perfil correto permanece em sua página, perfil diferente volta ao próprio início e o conteúdo autenticado fica oculto durante a revalidação.
- [x] 4.6 Aplicar a resolução de sessão ao carregamento de `/` e `/login`, verificando que a raiz escolhe login ou início por perfil e que um usuário já autenticado não permanece na tela de login.

## 5. Verificação integrada e revisão de escopo

- [x] 5.1 Executar a suíte automatizada do cliente, State e roteamento e verificar que todos os cenários da spec possuem cobertura de sucesso, erro, expiração máxima de oito horas, perda de State, ausência de persistência, indisponibilidade, logout e perfil indevido.
- [x] 5.2 Compilar a aplicação Reflex em modo de teste e verificar que não há erros de Vars, eventos, imports, páginas ou configuração.
- [x] 5.3 Executar uma validação manual com cliente simulado para os três perfis, credenciais inválidas, token expirado e Xano indisponível, verificando os estados visuais e redirecionamentos esperados sem depender de segredos reais.
- [x] 5.4 Com URL e credencial de teste disponibilizadas fora do repositório, validar login e `/me` contra o ambiente Xano alvo, confirmar o histórico do grupo `mira-auth` e verificar o destino do perfil sem registrar credenciais, tokens ou respostas sensíveis.
- [x] 5.5 Revisar o diff final e verificar que nenhum arquivo XanoScript, regra de autenticação/autorização, recurso de Service Desk, dashboard, indicador, Simulator ou Fiscal foi alterado e que nenhum segredo foi adicionado.
