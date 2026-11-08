// Query all interacoes_chamado records
query interacoes_chamado verb=GET {
  api_group = "APIS from table interacoes_chamado"
  auth = "usuarios"

  input {
  }

  stack {
    // O Gerente lê interações somente pelos contratos funcionais filtrados;
    // esta consulta genérica não filtra visibilidade nem tipo de evento.
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, tecnico: true}
    } as $usuario

    db.query interacoes_chamado {
      return = {type: "list"}
    } as $interacoes_chamado
  }

  response = $interacoes_chamado
  guid = "bbRu7Q_w0WeX7uVSaEK7PtlYCuY"
}
