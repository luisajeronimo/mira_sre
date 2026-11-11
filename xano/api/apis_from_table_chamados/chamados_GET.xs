// Query all chamados records
// Correção C-1: o Gerente recebe somente chamados cuja Loja comprovada na
// abertura (vínculo histórico) é a sua; a Loja atual do Totem não concede
// acesso. Técnico e Diretoria mantêm a consulta global; Administrador e
// demais perfis continuam negados por exigir_perfil.
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

    var $chamados {
      value = []
    }

    conditional {
      if ($usuario.role == "gerente") {
        function.run "service_desk/listar_chamados_loja_historica_gerente" {
          input = {usuarios_id: $auth.id}
        } as $autorizados

        var.update $chamados {
          value = $autorizados
        }
      }

      else {
        db.query chamados {
          return = {type: "list"}
        } as $todos

        var.update $chamados {
          value = $todos
        }
      }
    }
  }

  response = $chamados
  guid = "u-rXekZDzjuS0QJmk1HgpZt9N9w"
}
