// Retorna somente Loja comprovada por evento anterior ou igual ao fato.
function "administracao/resolver_loja_totem_no_instante" {
  input {
    int ativos_referencia_id
    timestamp? instante?
  }

  stack {
    var $lojas_id {
      value = null
    }

    conditional {
      if ($input.instante != null) {
        db.query historico_vinculos_totem_loja {
          where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $input.ativos_referencia_id && $db.historico_vinculos_totem_loja.efetivado_em <= $input.instante
          sort = {historico_vinculos_totem_loja.efetivado_em: "desc"}
          return = {type: "single"}
          mock = {
            "antes do primeiro vínculo"    : null
            "na fronteira da transferência": {loja_destino_id: 2, efetivado_em: 1780000000000}
            "depois da transferência"      : {loja_destino_id: 2, efetivado_em: 1780000000000}
          }
        } as $vinculo

        conditional {
          if ($vinculo != null) {
            var.update $lojas_id {
              value = $vinculo.loja_destino_id
            }
          }
        }
      }
    }
  }

  response = {lojas_id: $lojas_id}

  test "antes do primeiro vínculo" {
    input = {ativos_referencia_id: 1, instante: 1779999999999}

    expect.to_be_null ($response.lojas_id)
  }

  test "na fronteira da transferência" {
    input = {ativos_referencia_id: 1, instante: 1780000000000}

    expect.to_equal ($response.lojas_id) {
      value = 2
    }
  }

  test "depois da transferência" {
    input = {ativos_referencia_id: 1, instante: 1780000000001}

    expect.to_equal ($response.lojas_id) {
      value = 2
    }
  }

  guid = "miraResolverLojaTotemNoInstante01"
}