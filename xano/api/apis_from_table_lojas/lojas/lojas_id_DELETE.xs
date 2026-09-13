// Delete lojas record.
query "lojas/{lojas_id}" verb=DELETE {
  api_group = "APIS from table lojas"
  auth = "usuarios"

  input {
    int lojas_id? filters=min:1
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.del lojas {
      field_name = "id"
      field_value = $input.lojas_id
    }
  }

  response = null
  guid = "wQ0HgBM2xXrmnFEaO1e5AW7LSU4"
}
