// Coleção global de Totens para a jornada autorizada de monitoramento.
function "service_desk/listar_ativos_monitoramento" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "tecnico consulta monitoramento": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null, deve_trocar_senha: false}
          ```
        "diretoria consulta monitoramento": ```
          {id: 13, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null, deve_trocar_senha: false}
          ```
        "administrador consulta monitoramento": ```
          {id: 14, nome: "Administrador", email: "administrador@example.test", role: "administrador", lojas_id: null, deve_trocar_senha: false}
          ```
        "gerente nao consulta monitoramento": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1, deve_trocar_senha: false}
          ```
      }
    } as $usuario

    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "tecnico consulta monitoramento": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
          ```
        "diretoria consulta monitoramento": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
          ```
        "administrador consulta monitoramento": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
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

  test "tecnico consulta monitoramento" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
    }
  }

  test "diretoria consulta monitoramento" {
    input = {usuarios_id: 13}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
    }
  }

  test "administrador consulta monitoramento" {
    input = {usuarios_id: 14}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"}]
    }
  }

  test "gerente nao consulta monitoramento" {
    input = {usuarios_id: 8}
    expect.to_throw {
      exception = ""
    }
  }
  guid = "Yd84hQh-Bb7WP_h_93GqsR6mrYo"
}
