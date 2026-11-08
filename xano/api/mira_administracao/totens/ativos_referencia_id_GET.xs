// Detalhe administrativo de Totem.
query "administracao/totens/{ativos_referencia_id}" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int ativos_referencia_id filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    db.get ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
    } as $totem

    precondition ($totem != null) {
      error_type = "notfound"
      error = "Totem não encontrado."
    }

    var $resposta {
      value = {
        id           : $totem.id
        identificacao: $totem.identificacao
        nome         : $totem.nome_ativo
        lojas_id     : $totem.lojas_id
        status_atual : $totem.status_atual
      }
    }
  }

  response = $resposta
  guid = "admin-totens-detalhe-8e6cad4a"
}