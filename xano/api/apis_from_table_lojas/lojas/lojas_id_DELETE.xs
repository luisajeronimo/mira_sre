// Delete lojas record.
query "lojas/{lojas_id}" verb=DELETE {
  api_group = "APIS from table lojas"

  input {
    int lojas_id? filters=min:1
  }

  stack {
    db.del lojas {
      field_name = "id"
      field_value = $input.lojas_id
    }
  }

  response = null
  guid = "wQ0HgBM2xXrmnFEaO1e5AW7LSU4"
}