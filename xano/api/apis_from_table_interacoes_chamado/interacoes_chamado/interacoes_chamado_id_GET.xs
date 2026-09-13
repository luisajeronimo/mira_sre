// Get interacoes_chamado record
query "interacoes_chamado/{interacoes_chamado_id}" verb=GET {
  api_group = "APIS from table interacoes_chamado"
  auth = "usuarios"

  input {
    int interacoes_chamado_id? filters=min:1
  }

  stack {
    db.get interacoes_chamado {
      field_name = "id"
      field_value = $input.interacoes_chamado_id
    } as $interacoes_chamado

    db.get chamados {
      field_name = "id"
      field_value = $interacoes_chamado.chamados_id
    } as $chamado

    db.get ativos_referencia {
      field_name = "id"
      field_value = $chamado.ativos_referencia_id
    } as $ativo

    function.run "autorizacao/exigir_escopo_loja" {
      input = {
        usuarios_id: $auth.id,
        lojas_id: $ativo.lojas_id,
        tecnico: true
      }
    } as $usuario
  
    precondition ($interacoes_chamado != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $interacoes_chamado
  guid = "Pki3MuDqlBBcukgmk1VTRNq_V2w"
}
