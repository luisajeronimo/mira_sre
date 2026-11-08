// Edição cadastral e transferência temporal em uma unidade de escrita.
query "administracao/totens/{ativos_referencia_id}" verb=PATCH {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int ativos_referencia_id filters=min:1
    text identificacao filters=trim|min:1
    text nome filters=trim|min:1
    int lojas_id filters=min:1
  }

  stack {
    function.run "administracao/transferir_totem" {
      input = {
        usuarios_id         : $auth.id
        ativos_referencia_id: $input.ativos_referencia_id
        loja_destino_id     : $input.lojas_id
        identificacao       : $input.identificacao
        nome                : $input.nome
      }
    } as $transferencia

    db.get ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
    } as $totem

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
  guid = "admin-totens-editar-9f7dbe5b"
}