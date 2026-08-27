// Query all ativos_referencia records
query ativos_referencia verb=GET {
  api_group = "APIS from table ativos_referencia"

  input {
  }

  stack {
    db.query ativos_referencia {
      return = {type: "list"}
    } as $ativos_referencia
  }

  response = $ativos_referencia
  guid = "5Rmw9qaVmmvK3vh1tY8CTLT6cEk"
}