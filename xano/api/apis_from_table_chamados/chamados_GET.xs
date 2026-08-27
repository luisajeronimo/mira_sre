// Query all chamados records
query chamados verb=GET {
  api_group = "APIS from table chamados"

  input {
  }

  stack {
    db.query chamados {
      return = {type: "list"}
    } as $chamados
  }

  response = $chamados
  guid = "u-rXekZDzjuS0QJmk1HgpZt9N9w"
}