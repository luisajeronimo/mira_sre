// Get interacoes_chamado record
query "interacoes_chamado/{interacoes_chamado_id}" verb=GET {
  api_group = "APIS from table interacoes_chamado"

  input {
    int interacoes_chamado_id? filters=min:1
  }

  stack {
    db.get interacoes_chamado {
      field_name = "id"
      field_value = $input.interacoes_chamado_id
    } as $interacoes_chamado
  
    precondition ($interacoes_chamado != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $interacoes_chamado
  guid = "Pki3MuDqlBBcukgmk1VTRNq_V2w"
}