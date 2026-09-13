// Delete chamados record.
query "chamados/{chamados_id}" verb=DELETE {
  api_group = "APIS from table chamados"
  auth = "usuarios"

  input {
    int chamados_id? filters=min:1
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.del chamados {
      field_name = "id"
      field_value = $input.chamados_id
    }
  }

  response = null
  guid = "E6LUvpPOezGmN0hcHPGxxkDoauY"
}
