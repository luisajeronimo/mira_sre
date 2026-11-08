# Corrigir a autorização do Gerente nos GETs genéricos de chamados (C-1)

## Por quê

A auditoria do PR #26 (2026-11-08) confirmou a vulnerabilidade C-1, presente no workspace publicado: `GET /chamados` e `GET /chamados/{chamados_id}` (grupo `APIS from table chamados`) autorizam o Gerente pela **Loja atual** do Totem (`$db.ativo.lojas_id == $usuario.lojas_id` na lista; `exigir_escopo_loja` com `$ativo.lojas_id` no detalhe). Depois de uma transferência, o Gerente da Loja de destino lê pelos contratos genéricos chamados abertos quando o Totem pertencia a outra Loja, embora os contratos funcionais do Gerente já apliquem a Loja histórica.

O comportamento viola o requisito consolidado "Gerente usa Loja histórica comprovada do chamado" (`openspec/specs/autorizacao-perfis/spec.md`). Não há regra nova: a change alinha os contratos genéricos ao requisito vigente e registra cenários explícitos para eles.

Esta change é independente da change local `negar-gerente-gets-genericos-chamados` (A1), que não é usada, copiada nem publicada. A A1 propõe negar o Gerente nos contratos genéricos; esta change preserva o acesso do Gerente, restrito à Loja histórica.

## O que muda

- `GET /chamados`: para o Gerente, a lista vem de uma função nova, `service_desk/listar_chamados_loja_historica_gerente`, que não lê a Loja atual do Totem e mantém somente chamados cuja Loja resolvida em `criado_em` é a do Gerente. Técnico e Diretoria mantêm a consulta global.
- `GET /chamados/{chamados_id}`: para o Gerente, `service_desk/obter_chamado_gerente_autorizado` (autorizador histórico já publicado e testado) é executado antes da leitura do registro. Técnico e Diretoria mantêm a consulta global.
- Administrador e perfis não oficiais continuam negados por `exigir_perfil`; requisições sem token continuam rejeitadas pela autenticação da rota.
- Nenhum backfill, inferência pela Loja atual, alteração de dados ou mudança em `exigir_escopo_loja` (usada corretamente por rotas de dados atuais).

## Impacto

- Xano: 1 função nova e 2 endpoints alterados (publicação pendente de autorização; ver `pacote-publicacao.md`).
- Contrato: o formato das respostas não muda. Para o Gerente, chamado inexistente no detalhe passa de 403 para 404 (comportamento do autorizador histórico, igual ao contrato funcional `gerente/chamados/{id}`).
- Desempenho: a lista do Gerente percorre os chamados e resolve a Loja histórica de cada um (mesmo custo de `listar_chamados_gerente`; ver `design.md`, D4).
