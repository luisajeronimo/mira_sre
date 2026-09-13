// Get telemetria_equipamentos record
query "telemetria_equipamentos/{telemetria_equipamentos_id}" verb=GET {
  api_group = "APIS from table telemetria_equipamentos"
  auth = "usuarios"

  input {
    int telemetria_equipamentos_id? filters=min:1
  }

  stack {
    db.get telemetria_equipamentos {
      field_name = "id"
      field_value = $input.telemetria_equipamentos_id
    } as $telemetria_equipamentos

    db.get ativos_referencia {
      field_name = "id"
      field_value = $telemetria_equipamentos.ativos_referencia_id
    } as $ativo

    function.run "autorizacao/exigir_escopo_loja" {
      input = {
        usuarios_id: $auth.id,
        lojas_id: $ativo.lojas_id,
        tecnico: true,
        diretoria: true
      }
    } as $usuario
  
    precondition ($telemetria_equipamentos != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $telemetria_equipamentos
  guid = "jEpdk77kmHs0cWfLkzYM02UiwnQ"
}
