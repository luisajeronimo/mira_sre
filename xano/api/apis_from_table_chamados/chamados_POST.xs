// Add chamados record
query chamados verb=POST {
  api_group = "APIS from table chamados"

  input {
    dblink {
      table = "chamados"
    }
  }

  stack {
    db.add chamados {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $chamados
  }

  response = $chamados
  guid = "VZv2Xl7zlHXzFUhRxVjfw9_6lw4"
}