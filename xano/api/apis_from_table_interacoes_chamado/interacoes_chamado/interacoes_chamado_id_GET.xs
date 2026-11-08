// Get interacoes_chamado record
query "interacoes_chamado/{interacoes_chamado_id}" verb=GET {
  api_group = "APIS from table interacoes_chamado"
  auth = "usuarios"

  input {
    int interacoes_chamado_id? filters=min:1
  }

  stack {
    // Autoriza antes de qualquer leitura. O Gerente lê interações somente
    // pelos contratos funcionais filtrados; esta consulta não filtra visibilidade.
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, tecnico: true}
    } as $usuario

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
