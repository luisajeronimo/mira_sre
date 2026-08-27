// Get verificar_falhas record
query "verificar_falhas/{verificar_falhas_id}" verb=GET {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    int verificar_falhas_id? filters=min:1
  }

  stack {
    db.get "" {
      field_name = "id"
      field_value = $input.verificar_falhas_id
    } as $verificar_falhas
  
    precondition ($verificar_falhas != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $verificar_falhas
  guid = "00WthoIZ69Z4KMADqLXrFXAyg50"
}