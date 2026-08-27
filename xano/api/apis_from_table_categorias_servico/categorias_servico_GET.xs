// Query all categorias_servico records
query categorias_servico verb=GET {
  api_group = "APIS from table categorias_servico"

  input {
  }

  stack {
    db.query categorias_servico {
      return = {type: "list"}
    } as $categorias_servico
  }

  response = $categorias_servico
  guid = "xtpxlWfQ5gwivdLzWZXkqnP7cFQ"
}