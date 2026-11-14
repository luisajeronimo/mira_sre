// Get chamados record
// Correção C-1: para o Gerente, a autorização pela Loja histórica do chamado
// (obter_chamado_gerente_autorizado) ocorre antes da leitura do registro;
// a Loja atual do Totem não concede acesso. Técnico e Diretoria mantêm a
// consulta global; Administrador e demais perfis continuam negados.
query "chamados/{chamados_id}" verb=GET {
  api_group = "APIS from table chamados"
  auth = "usuarios"

  input {
    int chamados_id? filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id: $auth.id,
        gerente: true,
        tecnico: true,
        diretoria: true,
        administrador: true
      }
    } as $usuario

    conditional {
      if ($usuario.role == "gerente") {
        function.run "service_desk/obter_chamado_gerente_autorizado" {
          input = {
            usuarios_id: $auth.id,
            chamados_id: $input.chamados_id
          }
        } as $autorizado
      }
    }

    db.get chamados {
      field_name = "id"
      field_value = $input.chamados_id
    } as $chamados

    precondition ($chamados != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $chamados
  guid = "Cc3u4r37SpYIW9K2cInDHic_4Yk"
}
