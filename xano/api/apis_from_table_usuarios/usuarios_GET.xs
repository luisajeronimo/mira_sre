// Query all usuarios records
query usuarios verb=GET {
  api_group = "APIS from table usuarios"

  input {
  }

  stack {
    db.query usuarios {
      return = {type: "list"}
    } as $usuarios
  }

  response = $usuarios
  guid = "blh5xYoTaTXrXx_b5bOn7XJ7ATs"
}