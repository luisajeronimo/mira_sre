// Query all lojas records
query lojas verb=GET {
  api_group = "APIS from table lojas"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id: $auth.id,
        gerente: true,
        diretoria: true
      }
    } as $usuario

    precondition ($usuario.role != "gerente" || $usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query lojas {
      where = $usuario.role == "diretoria" || ($usuario.role == "gerente" && $db.lojas.id == $usuario.lojas_id)
      return = {type: "list"}
    } as $lojas
  }

  response = $lojas
  guid = "tjXvE1GDHDlMsCcWmGpgU2WU6Po"
}
