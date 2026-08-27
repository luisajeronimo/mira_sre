// Edit interacoes_chamado record
query "interacoes_chamado/{interacoes_chamado_id}" verb=PATCH {
  api_group = "APIS from table interacoes_chamado"

  input {
    int interacoes_chamado_id? filters=min:1
    dblink {
      table = "interacoes_chamado"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch interacoes_chamado {
      field_name = "id"
      field_value = $input.interacoes_chamado_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $interacoes_chamado
  }

  response = $interacoes_chamado
  guid = "l5TFshKKsX8xZDtrNuNn9J-k3Uc"
}