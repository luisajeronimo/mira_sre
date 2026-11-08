// Lista cadastral completa, separada do catálogo mínimo existente.
query "administracao/lojas/registros" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    db.query lojas {
      sort = {lojas.nome: "asc"}
      return = {type: "list"}
    } as $lojas

    var $items {
      value = $lojas|map:{
        id: $$.id,
        nome: $$.nome,
        endereco: $$.endereco,
        regiao: $$.regiao,
        status: $$.status
      }
    }
  }

  response = {items: $items}
  guid = "admin-lojas-listar-6b2f5c8e"
}
