// Delete ativos_referencia record.
query "ativos_referencia/{ativos_referencia_id}" verb=DELETE {
  api_group = "APIS from table ativos_referencia"
  auth = "usuarios"

  input {
    int ativos_referencia_id? filters=min:1
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.del ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
    }
  }

  response = null
  guid = "YL2KKomfKtmvSwR8SxlV2XnjXIo"
}
