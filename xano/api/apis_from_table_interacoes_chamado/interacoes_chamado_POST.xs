// Add interacoes_chamado record
query interacoes_chamado verb=POST {
  api_group = "APIS from table interacoes_chamado"

  input {
    dblink {
      table = "interacoes_chamado"
    }
  }

  stack {
    db.add interacoes_chamado {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $interacoes_chamado
  }

  response = $interacoes_chamado
  guid = "5wsSx-AOP20XQ9WvW4kFORKf_5s"
}