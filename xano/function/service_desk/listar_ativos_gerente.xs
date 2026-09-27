// Lista somente os ativos da Loja do Gerente autenticado.
function "service_desk/listar_ativos_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "lista ativos da loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita gerente sem loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: null}
          ```
        "isola segunda loja": ```
          {id: 10, nome: "Gerente 2", email: "gerente2@example.test", role: "gerente", lojas_id: 2}
          ```
      }
    } as $usuario

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query ativos_referencia {
      where = $db.ativos_referencia.lojas_id == $usuario.lojas_id
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "lista ativos da loja": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 1}]
          ```
        "isola segunda loja": ```
          [{id: 8, nome_ativo: "Totem 08", tipo: "Totem", status_atual: "offline", lojas_id: 2}]
          ```
      }
    } as $ativos

    var $items {
      value = $ativos|map:{
        id: $$.id,
        nome_ativo: $$.nome_ativo,
        tipo: $$.tipo,
        status_atual: $$.status_atual
      }
    }
  }

  response = {items: $items}

  test "lista ativos da loja" {
    input = {usuarios_id: 8}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
    }
  }

  test "rejeita gerente sem loja" {
    input = {usuarios_id: 8}
    expect.to_throw { exception = "" }
  }

  test "isola segunda loja" {
    input = {usuarios_id: 10}
    expect.to_equal ($response.items) {
      value = [{id: 8, nome_ativo: "Totem 08", tipo: "Totem", status_atual: "offline"}]
    }
  }
  guid = "LiHSZyt0PbGYsZB9CI6AnUQ839U"
}
