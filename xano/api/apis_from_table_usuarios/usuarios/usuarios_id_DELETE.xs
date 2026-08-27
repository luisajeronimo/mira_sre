// Delete usuarios record.
query "usuarios/{usuarios_id}" verb=DELETE {
  api_group = "APIS from table usuarios"

  input {
    int usuarios_id? filters=min:1
  }

  stack {
    db.del usuarios {
      field_name = "id"
      field_value = $input.usuarios_id
    }
  }

  response = null
  guid = "z2vPp3LyPl4aeQZoB10WvcTp_TY"
}