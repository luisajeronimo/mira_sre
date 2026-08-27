// Edit chamados record
query "chamados/{chamados_id}" verb=PATCH {
  api_group = "APIS from table chamados"

  input {
    int chamados_id? filters=min:1
    dblink {
      table = "chamados"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch chamados {
      field_name = "id"
      field_value = $input.chamados_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $chamados
  }

  response = $chamados
  guid = "uOzbwb2Mp-PH6mmzbxh4mdwvo7E"
}