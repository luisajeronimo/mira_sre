// Get ativos_referencia record
query "ativos_referencia/{ativos_referencia_id}" verb=GET {
  api_group = "APIS from table ativos_referencia"

  input {
    int ativos_referencia_id? filters=min:1
  }

  stack {
    db.get ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
    } as $ativos_referencia
  
    precondition ($ativos_referencia != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $ativos_referencia
  guid = "qN60Yhr682-GcRCaoA5sqUX11yk"
}