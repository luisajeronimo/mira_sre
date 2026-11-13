// Duração de um intervalo atribuível à Loja por vínculo histórico comprovado.
function "indicadores/duracao_loja_intervalo" {
  input {
    timestamp inicio
    timestamp fim
    int? lojas_id?
    json[] vinculos
  }

  stack {
    var $duracao { value = 0 }
    conditional {
      if ($input.fim > $input.inicio) {
        conditional {
          if ($input.lojas_id == null) {
            var.update $duracao { value = $input.fim - $input.inicio }
          }
          else {
            var $segmento_inicio { value = null }
            var $segmento_loja { value = null }
            foreach ($input.vinculos) {
              each as $vinculo {
                conditional {
                  if ($segmento_inicio != null && $segmento_loja == $input.lojas_id) {
                    var $trecho_inicio { value = $segmento_inicio|max:$input.inicio }
                    var $trecho_fim { value = $vinculo.efetivado_em|min:$input.fim }
                    conditional {
                      if ($trecho_fim > $trecho_inicio) {
                        var.update $duracao { value = $duracao + $trecho_fim - $trecho_inicio }
                      }
                    }
                  }
                }
                var.update $segmento_inicio { value = $vinculo.efetivado_em }
                var.update $segmento_loja { value = $vinculo.loja_destino_id }
              }
            }
            conditional {
              if ($segmento_inicio != null && $segmento_loja == $input.lojas_id) {
                var $trecho_inicio_final { value = $segmento_inicio|max:$input.inicio }
                conditional {
                  if ($input.fim > $trecho_inicio_final) {
                    var.update $duracao { value = $duracao + $input.fim - $trecho_inicio_final }
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  response = {duracao_ms: $duracao}

  test "rede conserva intervalo" {
    input = {inicio: 1000, fim: 5000, lojas_id: null, vinculos: []}
    expect.to_equal ($response.duracao_ms) { value = 4000 }
  }

  test "lojas repartem intervalo" {
    input = {inicio: 1000, fim: 5000, lojas_id: 1, vinculos: [{efetivado_em: 2000, loja_destino_id: 1}, {efetivado_em: 3500, loja_destino_id: 2}]}
    expect.to_equal ($response.duracao_ms) { value = 1500 }
  }

  test "trecho sem vinculo fica fora da loja" {
    input = {inicio: 1000, fim: 5000, lojas_id: 2, vinculos: [{efetivado_em: 2000, loja_destino_id: 1}, {efetivado_em: 3500, loja_destino_id: 2}]}
    expect.to_equal ($response.duracao_ms) { value = 1500 }
  }

  test "loja antiga nao cruza periodo apos transferencia" {
    input = {inicio: 4000, fim: 5000, lojas_id: 1, vinculos: [{efetivado_em: 1000, loja_destino_id: 1}, {efetivado_em: 3500, loja_destino_id: 2}]}
    expect.to_equal ($response.duracao_ms) { value = 0 }
  }
  guid = "tZ_SyRvKKbLsvsimRitCBUdIKlE"
}
