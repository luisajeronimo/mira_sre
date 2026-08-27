// Get categorias_servico record
query "categorias_servico/{categorias_servico_id}" verb=GET {
  api_group = "APIS from table categorias_servico"

  input {
    int categorias_servico_id? filters=min:1
  }

  stack {
    db.get categorias_servico {
      field_name = "id"
      field_value = $input.categorias_servico_id
    } as $categorias_servico
  
    precondition ($categorias_servico != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $categorias_servico
  guid = "Ih-YKBTJXfP_wVWkrsP-BWmfSS4"
}