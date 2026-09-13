// Query all ativos_referencia records
query ativos_referencia verb=GET {
  api_group = "APIS from table ativos_referencia"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id: $auth.id,
        gerente: true,
        tecnico: true,
        diretoria: true
      }
    } as $usuario

    precondition ($usuario.role != "gerente" || $usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query ativos_referencia {
      where = $usuario.role == "tecnico" || $usuario.role == "diretoria" || ($usuario.role == "gerente" && $db.ativos_referencia.lojas_id == $usuario.lojas_id)
      return = {type: "list"}
    } as $ativos_referencia
  }

  response = $ativos_referencia
  guid = "5Rmw9qaVmmvK3vh1tY8CTLT6cEk"
}
