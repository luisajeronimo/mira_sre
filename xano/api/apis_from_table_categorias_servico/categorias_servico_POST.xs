// Add categorias_servico record
query categorias_servico verb=POST {
  api_group = "APIS from table categorias_servico"

  input {
    dblink {
      table = "categorias_servico"
    }
  }

  stack {
    db.add categorias_servico {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $categorias_servico
  }

  response = $categorias_servico
  guid = "xy4RJm5BqhyQTw0JFpQ5EqMzOB0"
}