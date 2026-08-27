// Delete verificar_falhas record.
query "verificar_falhas/{verificar_falhas_id}" verb=DELETE {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    int verificar_falhas_id? filters=min:1
  }

  stack {
    db.del "" {
      field_name = "id"
      field_value = $input.verificar_falhas_id
    }
  }

  response = null
  guid = "Z6sphwq94FKRDWKMB2y24QZcHlM"
}