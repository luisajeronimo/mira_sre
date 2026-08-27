// Edit ativos_referencia record
query "ativos_referencia/{ativos_referencia_id}" verb=PATCH {
  api_group = "APIS from table ativos_referencia"

  input {
    int ativos_referencia_id? filters=min:1
    dblink {
      table = "ativos_referencia"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $ativos_referencia
  }

  response = $ativos_referencia
  guid = "JdNZMHCMkyb_aj4yyNCDBLYXqSU"
}