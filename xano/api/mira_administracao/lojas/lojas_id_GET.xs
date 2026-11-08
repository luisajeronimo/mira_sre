// Detalhe cadastral de Loja.
query "administracao/lojas/{lojas_id}" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int lojas_id filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    db.get lojas {
      field_name = "id"
      field_value = $input.lojas_id
    } as $loja

    precondition ($loja != null) {
      error_type = "notfound"
      error = "Loja não encontrada."
    }

    var $resposta {
      value = {
        id: $loja.id
        nome: $loja.nome
        endereco: $loja.endereco
        regiao: $loja.regiao
        status: $loja.status
      }
    }
  }

  response = $resposta
  guid = "admin-lojas-detalhe-7c3f6d9f"
}
