// Edit lojas record
query "lojas/{lojas_id}" verb=PATCH {
  api_group = "APIS from table lojas"

  input {
    int lojas_id? filters=min:1
    dblink {
      table = "lojas"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch lojas {
      field_name = "id"
      field_value = $input.lojas_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $lojas
  }

  response = $lojas
  guid = "u0HyzAOqzdvRM2TVUYhad9BD1wM"
}