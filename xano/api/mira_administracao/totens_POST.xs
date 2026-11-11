// Totem nasce com vínculo temporal inicial e sem estado operacional presumido.
query "administracao/totens" verb=POST {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
    text identificacao filters=trim|min:1
    text nome filters=trim|min:1
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

        precondition ($loja != null && ($loja.status == "Ativa" || $loja.status == "ativa" || $loja.status == "Ativo")) {
          error_type = "inputerror"
          error = "Loja inexistente ou Inativa."
        }

        var $efetivado_em {
          value = now
        }

        db.add ativos_referencia {
          data = {
            identificacao: $input.identificacao
            nome_ativo   : $input.nome
            tipo         : "Totem"
            lojas_id     : $loja.id
          }
        } as $totem

        db.add historico_vinculos_totem_loja {
          data = {
            ativos_referencia_id: $totem.id
            loja_origem_id      : null
            loja_destino_id     : $loja.id
            tipo                : "criacao"
            efetivado_em        : $efetivado_em
          }
        } as $vinculo
      }
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
  guid = "admin-totens-criar-6c4a8b2e"
}