// Query all chamados records
query chamados verb=GET {
  api_group = "APIS from table chamados"
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

    db.query chamados {
      join = {
        ativo: {
          table: "ativos_referencia",
          type: "left",
          where: $db.chamados.ativos_referencia_id == $db.ativo.id
        }
      }
      where = $usuario.role == "tecnico" || $usuario.role == "diretoria" || ($usuario.role == "gerente" && $db.ativo.lojas_id == $usuario.lojas_id)
      return = {type: "list"}
    } as $chamados
  }

  response = $chamados
  guid = "u-rXekZDzjuS0QJmk1HgpZt9N9w"
}
