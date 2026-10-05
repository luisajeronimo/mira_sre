// Conclui o primeiro acesso da própria sessão autenticada.
query "primeiro-acesso/trocar-senha" verb=POST {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    text nova_senha filters=min:8 {
      sensitive = true
    }
  }

  stack {
    db.get usuarios {
      field_name = "id"
      field_value = $auth.id
    } as $usuario

    precondition ($usuario != null && $usuario.deve_trocar_senha == true) {
      error_type = "accessdenied"
      error = "Troca de senha não está pendente."
    }

    db.transaction {
      stack {
        db.edit usuarios {
          field_name = "id"
          field_value = $auth.id
          data = {
            senha: $input.nova_senha
            deve_trocar_senha: false
          }
        } as $usuario_atualizado
      }
    }
  }

  response = {success: true}
  guid = "eF9gH1jK3mN5pQ7rS2tV4wX6yZ"
}
