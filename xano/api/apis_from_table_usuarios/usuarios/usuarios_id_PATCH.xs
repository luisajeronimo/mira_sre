// Edit usuarios record
query "usuarios/{usuarios_id}" verb=PATCH {
  api_group = "APIS from table usuarios"

  input {
    int usuarios_id? filters=min:1
    dblink {
      table = "usuarios"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch usuarios {
      field_name = "id"
      field_value = $input.usuarios_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $usuarios
  }

  response = $usuarios
  guid = "ON5uA97eONLsjv2PrupvC0ZghNY"
}