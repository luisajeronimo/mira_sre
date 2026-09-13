// Query all interacoes_chamado records
query interacoes_chamado verb=GET {
  api_group = "APIS from table interacoes_chamado"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id: $auth.id,
        gerente: true,
        tecnico: true
      }
    } as $usuario

    precondition ($usuario.role != "gerente" || $usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query interacoes_chamado {
      join = {
        chamado: {
          table: "chamados",
          type: "left",
          where: $db.interacoes_chamado.chamados_id == $db.chamado.id
        },
        ativo: {
          table: "ativos_referencia",
          type: "left",
          where: $db.chamado.ativos_referencia_id == $db.ativo.id
        }
      }
      where = $usuario.role == "tecnico" || ($usuario.role == "gerente" && $db.ativo.lojas_id == $usuario.lojas_id)
      return = {type: "list"}
    } as $interacoes_chamado
  }

  response = $interacoes_chamado
  guid = "bbRu7Q_w0WeX7uVSaEK7PtlYCuY"
}
