// Query all lojas records
query lojas verb=GET {
  api_group = "APIS from table lojas"

  input {
  }

  stack {
    db.query lojas {
      return = {type: "list"}
    } as $lojas
  }

  response = $lojas
  guid = "tjXvE1GDHDlMsCcWmGpgU2WU6Po"
}