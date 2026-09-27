// Lista chamados associados aos ativos da Loja do Gerente.
function "service_desk/listar_chamados_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "lista chamados da loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "lista vazio": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "preserva nulos legados": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita gerente sem loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: null}
          ```
      }
    } as $usuario

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query chamados {
      join = {
        ativo: {
          table: "ativos_referencia"
          type: "inner"
          where: $db.chamados.ativos_referencia_id == $db.ativo.id
        }
        categoria: {
          table: "categorias_servico"
          type: "left"
          where: $db.chamados.categorias_servico_id == $db.categoria.id
        }
      }
      eval = {
        ativo_id: $db.ativo.id
        ativo_nome: $db.ativo.nome_ativo
        categoria_id: $db.categoria.id
        categoria_nome: $db.categoria.nome
      }
      where = $db.ativo.lojas_id == $usuario.lojas_id
      sort = {chamados.id: "desc"}
      return = {type: "list"}
      mock = {
        "lista chamados da loja": ```
          [{id: 101, titulo: "Falha", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede"}]
          ```
        "lista vazio": []
        "preserva nulos legados": ```
          [{id: 16, titulo: "Legado", status: "Novo", prioridade: "Urgente", origem: null, criado_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 1, categoria_nome: "Totem Offline / Sem Heartbeat"}]
          ```
      }
    } as $chamados

    var $items {
      value = $chamados|map:{
        id: $$.id,
        titulo: $$.titulo,
        status: $$.status,
        prioridade: $$.prioridade,
        origem: $$.origem,
        criado_em: $$.criado_em,
        ativo: {id: $$.ativo_id, nome_ativo: $$.ativo_nome},
        categoria: {id: $$.categoria_id, nome: $$.categoria_nome}
      }
    }
  }

  response = {items: $items}

  test "lista chamados da loja" {
    input = {usuarios_id: 8}
    expect.to_equal ($response.items) {
      value = [{id: 101, titulo: "Falha", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Falha de Rede"}}]
    }
  }

  test "lista vazio" {
    input = {usuarios_id: 8}
    expect.to_be_empty ($response.items)
  }

  test "preserva nulos legados" {
    input = {usuarios_id: 8}
    expect.to_equal ($response.items) {
      value = [{id: 16, titulo: "Legado", status: "Novo", prioridade: "Urgente", origem: null, criado_em: null, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 1, nome: "Totem Offline / Sem Heartbeat"}}]
    }
  }

  test "rejeita gerente sem loja" {
    input = {usuarios_id: 8}
    expect.to_throw { exception = "" }
  }
  guid = "bsjXDAqhCr8qGwBABqPGX2sXVD8"
}
