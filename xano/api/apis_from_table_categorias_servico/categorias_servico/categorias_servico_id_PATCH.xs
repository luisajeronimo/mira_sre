// Edit categorias_servico record
query "categorias_servico/{categorias_servico_id}" verb=PATCH {
  api_group = "APIS from table categorias_servico"

  input {
    int categorias_servico_id? filters=min:1
    dblink {
      table = "categorias_servico"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch categorias_servico {
      field_name = "id"
      field_value = $input.categorias_servico_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $categorias_servico
  }

  response = $categorias_servico
  guid = "fXGLGyyiDM4PEiFsF6j6rvdxCeA"
}