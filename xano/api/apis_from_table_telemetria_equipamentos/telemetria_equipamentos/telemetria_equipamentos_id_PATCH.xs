// Edit telemetria_equipamentos record
query "telemetria_equipamentos/{telemetria_equipamentos_id}" verb=PATCH {
  api_group = "APIS from table telemetria_equipamentos"
  auth = "usuarios"

  input {
    int telemetria_equipamentos_id? filters=min:1
    dblink {
      table = "telemetria_equipamentos"
    }
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch telemetria_equipamentos {
      field_name = "id"
      field_value = $input.telemetria_equipamentos_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $telemetria_equipamentos
  }

  response = $telemetria_equipamentos
  guid = "6vCFZLHAV5zIGP-sIV_lPtqKtlc"
}
