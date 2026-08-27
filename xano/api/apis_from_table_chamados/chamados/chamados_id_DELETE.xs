// Delete chamados record.
query "chamados/{chamados_id}" verb=DELETE {
  api_group = "APIS from table chamados"

  input {
    int chamados_id? filters=min:1
  }

  stack {
    db.del chamados {
      field_name = "id"
      field_value = $input.chamados_id
    }
  }

  response = null
  guid = "E6LUvpPOezGmN0hcHPGxxkDoauY"
}