// Add verificar_falhas record
query verificar_falhas verb=POST {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    dblink {
      table = ""
    }
  }

  stack {
    db.add "" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $verificar_falhas
  }

  response = $verificar_falhas
  guid = "7pQSb76sHq5KQHcthc0rKY9rH7A"
}