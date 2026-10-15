// Lista todos os ativos disponíveis para a fila global.
function "service_desk/listar_ativos_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "lista ativos globais": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "lista ativos globais": ```
          [
            {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"},
            {id: 2, nome_ativo: "Totem 02", tipo: "Totem", status_atual: "offline"}
          ]
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

  test "lista ativos globais" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [
        {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online"},
        {id: 2, nome_ativo: "Totem 02", tipo: "Totem", status_atual: "offline"}
      ]
    }
  }
  guid = "_iFF-HFbhNF5n3wR-HKLyDPchJk"
}
