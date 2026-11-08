// Projeção pública da Loja demonstrada para um fato de Totem.
function "administracao/obter_loja_historica_fato" {
  input {
    int ativos_referencia_id
    timestamp? instante?
  }

  stack {
    function.run "administracao/resolver_loja_totem_no_instante" {
      input = {
        ativos_referencia_id: $input.ativos_referencia_id
        instante            : $input.instante
      }
    } as $vinculo

    var $loja {
      value = null
    }

    conditional {
      if ($vinculo.lojas_id != null) {
        db.get lojas {
          field_name = "id"
          field_value = $vinculo.lojas_id
        } as $registro

        conditional {
          if ($registro != null) {
            var.update $loja {
              value = {id: $registro.id, nome: $registro.nome}
            }
          }
        }
      }
    }
  }

  response = {loja: $loja}
  guid = "miraObterLojaHistoricaFato01"
}