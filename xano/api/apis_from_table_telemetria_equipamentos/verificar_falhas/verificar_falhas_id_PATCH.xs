// Edit verificar_falhas record
query "verificar_falhas/{verificar_falhas_id}" verb=PATCH {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    int verificar_falhas_id? filters=min:1
    dblink {
      table = ""
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch "" {
      field_name = "id"
      field_value = $input.verificar_falhas_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $verificar_falhas
  }

  response = $verificar_falhas
  guid = "07w1mVA1Fo2QaFeovPa0PR807cE"
}