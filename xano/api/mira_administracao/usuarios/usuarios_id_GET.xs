// Projeção explícita impede exposição de senha, hash ou token.
query "administracao/usuarios/{usuarios_id}" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int usuarios_id filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador
    db.get usuarios {
      field_name = "id"
      field_value = $input.usuarios_id
    } as $usuario
    precondition ($usuario != null) {
      error_type = "notfound"
      error = "Usuário não encontrado."
    }
    var $resposta {
      value = {
        id: $usuario.id
        nome: $usuario.nome
        email: $usuario.email
        role: $usuario.role
        lojas_id: $usuario.lojas_id
      }
    }
  }

  response = $resposta
  guid = "admin-usuarios-detalhe-2ca0e18e"
}
