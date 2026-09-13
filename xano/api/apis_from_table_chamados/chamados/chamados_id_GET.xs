// Get chamados record
query "chamados/{chamados_id}" verb=GET {
  api_group = "APIS from table chamados"
  auth = "usuarios"

  input {
    int chamados_id? filters=min:1
  }

  stack {
    db.get chamados {
      field_name = "id"
      field_value = $input.chamados_id
    } as $chamados

    db.get ativos_referencia {
      field_name = "id"
      field_value = $chamados.ativos_referencia_id
    } as $ativo

    function.run "autorizacao/exigir_escopo_loja" {
      input = {
        usuarios_id: $auth.id,
        lojas_id: $ativo.lojas_id,
        tecnico: true,
        diretoria: true
      }
    } as $usuario
  
    precondition ($chamados != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $chamados
  guid = "Cc3u4r37SpYIW9K2cInDHic_4Yk"
}
