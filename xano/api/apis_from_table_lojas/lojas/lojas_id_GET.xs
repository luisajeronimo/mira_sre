// Get lojas record
query "lojas/{lojas_id}" verb=GET {
  api_group = "APIS from table lojas"

  input {
    int lojas_id? filters=min:1
  }

  stack {
    db.get lojas {
      field_name = "id"
      field_value = $input.lojas_id
    } as $lojas
  
    precondition ($lojas != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $lojas
  guid = "jLjQ6GOu1xraMr5zuBhlGPbFUKg"
}