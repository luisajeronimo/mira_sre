// Delete categorias_servico record.
query "categorias_servico/{categorias_servico_id}" verb=DELETE {
  api_group = "APIS from table categorias_servico"

  input {
    int categorias_servico_id? filters=min:1
  }

  stack {
    db.del categorias_servico {
      field_name = "id"
      field_value = $input.categorias_servico_id
    }
  }

  response = null
  guid = "l2pZrz5EmmpY2LqpArFh_wxQ8lU"
}