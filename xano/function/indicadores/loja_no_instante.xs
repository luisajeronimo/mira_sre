// Resolve a Loja de um fato sem recorrer ao vínculo atual.
function "indicadores/loja_no_instante" {
  input {
    timestamp instante
    json[] vinculos
  }

  stack {
    var $lojas_id { value = null }
    foreach ($input.vinculos) {
      each as $vinculo {
        conditional {
          if ($vinculo.efetivado_em <= $input.instante) {
            var.update $lojas_id { value = $vinculo.loja_destino_id }
          }
        }
      }
    }
  }

  response = {lojas_id: $lojas_id}

  test "antes do primeiro vinculo" {
    input = {instante: 1000, vinculos: [{efetivado_em: 2000, loja_destino_id: 1}]}
    expect.to_be_null ($response.lojas_id)
  }

  test "na transferencia" {
    input = {instante: 3500, vinculos: [{efetivado_em: 2000, loja_destino_id: 1}, {efetivado_em: 3500, loja_destino_id: 2}]}
    expect.to_equal ($response.lojas_id) { value = 2 }
  }
  guid = "EEMcl-2SpqHwcY7FqIPGi69enEs"
}
