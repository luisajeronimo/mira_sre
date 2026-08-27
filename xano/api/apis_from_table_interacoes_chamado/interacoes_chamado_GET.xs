// Query all interacoes_chamado records
query interacoes_chamado verb=GET {
  api_group = "APIS from table interacoes_chamado"

  input {
  }

  stack {
    db.query interacoes_chamado {
      return = {type: "list"}
    } as $interacoes_chamado
  }

  response = $interacoes_chamado
  guid = "bbRu7Q_w0WeX7uVSaEK7PtlYCuY"
}