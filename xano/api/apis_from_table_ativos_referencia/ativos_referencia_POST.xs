// Add ativos_referencia record
query ativos_referencia verb=POST {
  api_group = "APIS from table ativos_referencia"
  auth = "usuarios"

  input {
    dblink {
      table = "ativos_referencia"
    }
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.add ativos_referencia {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $ativos_referencia
  }

  response = $ativos_referencia
  guid = "VEX4SSXWxwi5-MdZoc0sJLCmJNY"
}
