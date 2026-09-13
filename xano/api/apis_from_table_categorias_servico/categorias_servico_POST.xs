// Add categorias_servico record
query categorias_servico verb=POST {
  api_group = "APIS from table categorias_servico"
  auth = "usuarios"

  input {
    dblink {
      table = "categorias_servico"
    }
  }

  stack {
    function.run "autorizacao/negar_mutacao_generica" {
      input = {usuarios_id: $auth.id}
    } as $negado

    db.add categorias_servico {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $categorias_servico
  }

  response = $categorias_servico
  guid = "xy4RJm5BqhyQTw0JFpQ5EqMzOB0"
}
