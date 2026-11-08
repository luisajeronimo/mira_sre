// Edição cadastral de Loja sem alterar seus vínculos ou fatos operacionais.
query "administracao/lojas/{lojas_id}" verb=PATCH {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int lojas_id filters=min:1
    text nome filters=trim|min:1
    text endereco filters=trim|min:1
    text regiao filters=trim|min:1
    text status filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    precondition ($input.status == "Ativa" || $input.status == "Inativa") {
      error_type = "inputerror"
      error = "Situação inválida."
    }

    db.get lojas {
      field_name = "id"
      field_value = $input.lojas_id
    } as $existente

    precondition ($existente != null) {
      error_type = "notfound"
      error = "Loja não encontrada."
    }

    db.edit lojas {
      field_name = "id"
      field_value = $input.lojas_id
      data = {
        nome: $input.nome
        endereco: $input.endereco
        regiao: $input.regiao
        status: $input.status
      }
    } as $loja

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
  guid = "admin-lojas-editar-8d4f7e0a"
}
