// Grava vínculo temporal e vínculo atual como uma única unidade.
function "administracao/transferir_totem" {
  input {
    int usuarios_id { table = "usuarios" }
    int ativos_referencia_id { table = "ativos_referencia" }
    int loja_destino_id { table = "lojas" }
    text identificacao filters=trim|min:1
    text nome filters=trim|min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, administrador: true}
      mock = {
        "transfere para loja ativa": {id: 12, role: "administrador"}
        "rejeita loja inativa": {id: 12, role: "administrador"}
      }
    } as $administrador

    db.transaction {
      stack {
        db.get ativos_referencia {
          field_name = "id"
          field_value = $input.ativos_referencia_id
          lock = true
          mock = {
            "transfere para loja ativa": {id: 1, lojas_id: 1}
            "rejeita loja inativa": {id: 1, lojas_id: 1}
          }
        } as $totem
        precondition ($totem != null) {
          error_type = "notfound"
          error = "Totem não encontrado."
        }
        var $efetivado_em { value = null }
        conditional {
          if ($totem.lojas_id != $input.loja_destino_id) {
            db.get lojas {
              field_name = "id"
              field_value = $input.loja_destino_id
              lock = true
              mock = {
                "transfere para loja ativa": {id: 2, status: "Ativa"}
                "rejeita loja inativa": {id: 2, status: "Inativa"}
              }
            } as $destino
            precondition ($destino != null && ($destino.status == "Ativa" || $destino.status == "ativa" || $destino.status == "Ativo")) {
              error_type = "inputerror"
              error = "Loja de destino inexistente ou Inativa."
            }

            var.update $efetivado_em { value = now }
            db.add historico_vinculos_totem_loja {
              data = {
                ativos_referencia_id: $totem.id
                loja_origem_id: $totem.lojas_id
                loja_destino_id: $destino.id
                tipo: "transferencia"
                efetivado_em: $efetivado_em
              }
              mock = {
                "transfere para loja ativa": {id: 10, ativos_referencia_id: 1, loja_origem_id: 1, loja_destino_id: 2, tipo: "transferencia", efetivado_em: 1780000000000}
              }
            } as $evento
          }
        }
        db.edit ativos_referencia {
          field_name = "id"
          field_value = $totem.id
          data = {
            identificacao: $input.identificacao
            nome_ativo: $input.nome
            lojas_id: $input.loja_destino_id
          }
          mock = {
            "transfere para loja ativa": {id: 1, lojas_id: 2, identificacao: "T-01", nome_ativo: "Totem 01"}
          }
        } as $atualizado
        precondition ($atualizado != null && $atualizado.lojas_id == $input.loja_destino_id) {
          error_type = "inputerror"
          error = "Transferência não concluída."
        }
      }
    }
  }

  response = {
    id: $atualizado.id
    lojas_id: $atualizado.lojas_id
    efetivado_em: $efetivado_em
  }

  test "transfere para loja ativa" {
    input = {usuarios_id: 12, ativos_referencia_id: 1, loja_destino_id: 2, identificacao: "T-01", nome: "Totem 01"}
    expect.to_equal ($response.id) { value = 1 }
    expect.to_equal ($response.lojas_id) { value = 2 }
    expect.to_not_be_null ($response.efetivado_em)
  }

  test "rejeita loja inativa" {
    input = {usuarios_id: 12, ativos_referencia_id: 1, loja_destino_id: 2, identificacao: "T-01", nome: "Totem 01"}
    expect.to_throw { exception = "" }
  }
  guid = "miraTransferirTotem01"
}
