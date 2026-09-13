// Add usuarios record
query usuarios verb=POST {
  api_group = "APIS from table usuarios"
  auth = "usuarios"

  input {
    dblink {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.add usuarios {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $usuarios
  }

  response = $usuarios
  guid = "Bypyn8jGxfNQ7Ox4HOHxLtl9t4A"
}
