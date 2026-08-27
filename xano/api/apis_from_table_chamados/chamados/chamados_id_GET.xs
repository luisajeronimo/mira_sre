// Get chamados record
query "chamados/{chamados_id}" verb=GET {
  api_group = "APIS from table chamados"

  input {
    int chamados_id? filters=min:1
  }

  stack {
    db.get chamados {
      field_name = "id"
      field_value = $input.chamados_id
    } as $chamados
  
    precondition ($chamados != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $chamados
  guid = "Cc3u4r37SpYIW9K2cInDHic_4Yk"
}