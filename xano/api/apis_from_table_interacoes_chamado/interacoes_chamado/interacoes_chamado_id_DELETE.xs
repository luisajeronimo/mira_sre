// Delete interacoes_chamado record.
query "interacoes_chamado/{interacoes_chamado_id}" verb=DELETE {
  api_group = "APIS from table interacoes_chamado"

  input {
    int interacoes_chamado_id? filters=min:1
  }

  stack {
    db.del interacoes_chamado {
      field_name = "id"
      field_value = $input.interacoes_chamado_id
    }
  }

  response = null
  guid = "sgF6Gw09v2Y5IG1t2G6JbKt4194"
}