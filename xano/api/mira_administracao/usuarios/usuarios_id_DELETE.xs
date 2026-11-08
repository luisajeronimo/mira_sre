// Exclusão física somente quando nenhuma referência operacional permanece.
query "administracao/usuarios/{usuarios_id}" verb=DELETE {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int usuarios_id filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    precondition ($input.usuarios_id != $auth.id) {
      error_type = "inputerror"
      error = "Não é permitido excluir a própria conta."
    }

    db.transaction {
      stack {
        db.get usuarios {
          field_name = "id"
          field_value = $input.usuarios_id
          lock = true
        } as $usuario
        precondition ($usuario != null) {
          error_type = "notfound"
          error = "Usuário não encontrado."
        }

        conditional {
          if ($usuario.role == "administrador") {
            db.query usuarios {
              where = $db.usuarios.role == "administrador"
              lock = true
              return = {type: "list"}
            } as $administradores
            precondition (($administradores|count) > 1) {
              error_type = "inputerror"
              error = "O último Administrador deve permanecer."
            }
          }
        }

        db.query chamados {
          where = $db.chamados.solicitante_id == $usuario.id || $db.chamados.tecnico_id == $usuario.id
          return = {type: "exists"}
        } as $tem_chamado
        db.query interacoes_chamado {
          where = $db.interacoes_chamado.usuarios_id == $usuario.id || $db.interacoes_chamado.tecnico_anterior_id == $usuario.id || $db.interacoes_chamado.tecnico_novo_id == $usuario.id
          return = {type: "exists"}
        } as $tem_interacao
        db.query preferencias_fila_chamados {
          where = $db.preferencias_fila_chamados.usuarios_id == $usuario.id || $db.preferencias_fila_chamados.responsavel_id == $usuario.id
          return = {type: "exists"}
        } as $tem_preferencia
        precondition (!$tem_chamado && !$tem_interacao && !$tem_preferencia) {
          error_type = "inputerror"
          error = "Usuário possui vínculos ou histórico impeditivos."
        }

        db.del usuarios {
          field_name = "id"
          field_value = $usuario.id
        }
      }
    }
  }

  response = {success: true}
  guid = "admin-usuarios-excluir-4ec203a0"
}
