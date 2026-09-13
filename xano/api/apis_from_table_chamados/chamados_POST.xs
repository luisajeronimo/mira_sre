// Add chamados record
query chamados verb=POST {
  api_group = "APIS from table chamados"
  auth = "usuarios"

  input {
    dblink {
      table = "chamados"
    }
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.add chamados {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $chamados
  }

  response = $chamados
  guid = "VZv2Xl7zlHXzFUhRxVjfw9_6lw4"
}
