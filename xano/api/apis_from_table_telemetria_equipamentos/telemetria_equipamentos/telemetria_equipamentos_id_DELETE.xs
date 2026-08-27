// Delete telemetria_equipamentos record.
query "telemetria_equipamentos/{telemetria_equipamentos_id}" verb=DELETE {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    int telemetria_equipamentos_id? filters=min:1
  }

  stack {
    db.del telemetria_equipamentos {
      field_name = "id"
      field_value = $input.telemetria_equipamentos_id
    }
  }

  response = null
  guid = "0ssO-pETKMsmUDL7tgQYoqW1jwY"
}