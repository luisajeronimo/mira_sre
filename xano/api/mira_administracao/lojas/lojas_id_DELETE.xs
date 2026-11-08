// Exclui apenas Loja sem referência atual ou histórica.
query "administracao/lojas/{lojas_id}" verb=DELETE {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int lojas_id filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    db.transaction {
      stack {
        db.get lojas {
          field_name = "id"
          field_value = $input.lojas_id
          lock = true
        } as $loja
        precondition ($loja != null) {
          error_type = "notfound"
          error = "Loja não encontrada."
        }

        db.query usuarios {
          where = $db.usuarios.lojas_id == $input.lojas_id
          return = {type: "exists"}
        } as $tem_gerente
        db.query ativos_referencia {
          where = $db.ativos_referencia.lojas_id == $input.lojas_id
          return = {type: "exists"}
        } as $tem_totem
        db.query preferencias_fila_chamados {
          where = $db.preferencias_fila_chamados.lojas_id == $input.lojas_id
          return = {type: "exists"}
        } as $tem_preferencia
        db.query historico_vinculos_totem_loja {
          where = $db.historico_vinculos_totem_loja.loja_origem_id == $input.lojas_id || $db.historico_vinculos_totem_loja.loja_destino_id == $input.lojas_id
          return = {type: "exists"}
        } as $tem_historico

        precondition (!$tem_gerente && !$tem_totem && !$tem_preferencia && !$tem_historico) {
          error_type = "inputerror"
          error = "Loja possui vínculos ou histórico impeditivos."
        }
        db.del lojas {
          field_name = "id"
          field_value = $input.lojas_id
        }
      }
    }
  }

  response = {success: true}
  guid = "admin-lojas-excluir-9e5f8f1b"
}
