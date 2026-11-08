// Remove Totem livre; somente vínculo inicial pode ser removido explicitamente.
query "administracao/totens/{ativos_referencia_id}" verb=DELETE {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    int ativos_referencia_id filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador

    db.transaction {
      stack {
        db.get ativos_referencia {
          field_name = "id"
          field_value = $input.ativos_referencia_id
          lock = true
        } as $totem
        precondition ($totem != null) {
          error_type = "notfound"
          error = "Totem não encontrado."
        }

        db.query chamados {
          where = $db.chamados.ativos_referencia_id == $totem.id
          return = {type: "exists"}
        } as $tem_chamado
        db.query telemetria_equipamentos {
          where = $db.telemetria_equipamentos.ativos_referencia_id == $totem.id
          return = {type: "exists"}
        } as $tem_telemetria
        db.query historico_disponibilidade_totens {
          where = $db.historico_disponibilidade_totens.ativos_referencia_id == $totem.id
          return = {type: "exists"}
        } as $tem_disponibilidade
        db.query preferencias_fila_chamados {
          where = $db.preferencias_fila_chamados.ativos_referencia_id == $totem.id
          return = {type: "exists"}
        } as $tem_preferencia
        db.query historico_vinculos_totem_loja {
          where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $totem.id
          sort = {historico_vinculos_totem_loja.efetivado_em: "asc"}
          return = {type: "list"}
        } as $vinculos

        precondition (!$tem_chamado && !$tem_telemetria && !$tem_disponibilidade && !$tem_preferencia) {
          error_type = "inputerror"
          error = "Totem possui vínculos ou histórico impeditivos."
        }
        precondition (($vinculos|count) == 0 || (($vinculos|count) == 1 && $vinculos[0].tipo == "criacao")) {
          error_type = "inputerror"
          error = "Totem possui transferência histórica."
        }

        conditional {
          if (($vinculos|count) == 1) {
            db.del historico_vinculos_totem_loja {
              field_name = "id"
              field_value = $vinculos[0].id
            }
          }
        }
        db.del ativos_referencia {
          field_name = "id"
          field_value = $totem.id
        }
      }
    }
  }

  response = {success: true}
  guid = "admin-totens-excluir-0a8ecf6c"
}
