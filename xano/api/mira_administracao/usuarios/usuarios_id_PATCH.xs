// Edição cadastral com validação de papel, Loja e responsabilidades.
query "administracao/usuarios/{usuarios_id}" verb=PATCH {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int usuarios_id filters=min:1
    text nome filters=trim|min:1
    email email filters=trim|lower
    text role filters=trim
    int? lojas_id? filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

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

        precondition ($input.role == "gerente" || $input.role == "tecnico" || $input.role == "diretoria" || $input.role == "administrador") {
          error_type = "inputerror"
          error = "Perfil inválido."
        }
        precondition (($input.role == "gerente" && $input.lojas_id != null) || ($input.role != "gerente" && $input.lojas_id == null)) {
          error_type = "inputerror"
          error = "Loja incompatível com o perfil."
        }

        db.query usuarios {
          where = $db.usuarios.email == $input.email && $db.usuarios.id != $usuario.id
          return = {type: "exists"}
        } as $email_usado
        precondition (!$email_usado) {
          error_type = "inputerror"
          error = "E-mail já cadastrado."
        }

        conditional {
          if ($input.role == "gerente") {
            db.get lojas {
              field_name = "id"
              field_value = $input.lojas_id
            } as $loja
            precondition ($loja != null && (($usuario.role == "gerente" && $usuario.lojas_id == $input.lojas_id) || $loja.status == "Ativa" || $loja.status == "ativa" || $loja.status == "Ativo")) {
              error_type = "inputerror"
              error = "Loja inexistente ou Inativa para novo vínculo."
            }
          }
        }

        conditional {
          if ($usuario.role == "tecnico" && $input.role != "tecnico") {
            db.query chamados {
              where = $db.chamados.tecnico_id == $usuario.id
              return = {type: "exists"}
            } as $tem_responsabilidade
            precondition (!$tem_responsabilidade) {
              error_type = "inputerror"
              error = "Técnico possui chamado atribuído."
            }
          }
        }

        conditional {
          if ($usuario.role == "administrador" && $input.role != "administrador") {
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

        db.patch usuarios {
          field_name = "id"
          field_value = $usuario.id
          data = {
            nome: $input.nome
            email: $input.email
            role: $input.role
            lojas_id: $input.lojas_id
          }
        } as $atualizado
      }
    }

    var $resposta {
      value = {
        id: $atualizado.id
        nome: $atualizado.nome
        email: $atualizado.email
        role: $atualizado.role
        lojas_id: $atualizado.lojas_id
      }
    }
  }

  response = $resposta
  guid = "admin-usuarios-editar-3db1f29f"
}
