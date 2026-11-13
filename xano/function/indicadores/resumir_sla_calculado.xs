// Resume consumos individuais já calculados pela função consolidada do Service Desk.
function "indicadores/resumir_sla_calculado" {
  input {
    json[] paradas
    json[] riscos
    int cancelados
    int status_nao_canonicos
  }

  stack {
    var $elegiveis { value = 0 }
    var $cumpriram { value = 0 }
    var $paradas_nao_calculaveis { value = 0 }
    foreach ($input.paradas) {
      each as $parada {
        conditional {
          if ($parada.calculavel && ($parada.estado_contagem == "pausada" || $parada.estado_contagem == "encerrada") && $parada.consumo_ms != null && $parada.sla_horas_aplicado != null && $parada.sla_horas_aplicado > 0) {
            var.update $elegiveis { value = $elegiveis + 1 }
            conditional {
              if ($parada.consumo_ms <= $parada.sla_horas_aplicado * 3600000) {
                var.update $cumpriram { value = $cumpriram + 1 }
              }
            }
          }
          else {
            var.update $paradas_nao_calculaveis { value = $paradas_nao_calculaveis + 1 }
          }
        }
      }
    }
    var $percentual { value = null }
    conditional {
      if ($elegiveis > 0) {
        var.update $percentual { value = ($cumpriram * 100 / $elegiveis)|round:2 }
      }
    }

    var $normal { value = 0 }
    var $risco { value = 0 }
    var $critico { value = 0 }
    var $violado { value = 0 }
    var $risco_nao_calculaveis { value = 0 }
    foreach ($input.riscos) {
      each as $item {
        conditional {
          if ($item.calculavel && $item.estado_contagem == "em_contagem") {
            conditional {
              if ($item.faixa == "normal") {
                var.update $normal { value = $normal + 1 }
              }
              elseif ($item.faixa == "risco") {
                var.update $risco { value = $risco + 1 }
              }
              elseif ($item.faixa == "critico") {
                var.update $critico { value = $critico + 1 }
              }
              elseif ($item.faixa == "violado") {
                var.update $violado { value = $violado + 1 }
              }
              else {
                var.update $risco_nao_calculaveis { value = $risco_nao_calculaveis + 1 }
              }
            }
          }
          else {
            var.update $risco_nao_calculaveis { value = $risco_nao_calculaveis + 1 }
          }
        }
      }
    }
  }

  response = {
    conformidade: {percentual: $percentual, cumpriram: $cumpriram, elegiveis: $elegiveis, cancelados: $input.cancelados, nao_calculaveis: $paradas_nao_calculaveis},
    risco: {normal: $normal, risco: $risco, critico: $critico, violado: $violado, nao_calculaveis: $risco_nao_calculaveis, status_nao_canonicos: $input.status_nao_canonicos}
  }

  test "oito de dez com dois cancelados" {
    input = {
      paradas: [
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 3600000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "pausada", consumo_ms: 10800000, sla_horas_aplicado: 2},
        {calculavel: true, estado_contagem: "encerrada", consumo_ms: 10800000, sla_horas_aplicado: 2}
      ],
      riscos: [], cancelados: 2, status_nao_canonicos: 0
    }
    expect.to_equal ($response.conformidade.percentual) { value = 80 }
    expect.to_equal ($response.conformidade.elegiveis) { value = 10 }
    expect.to_equal ($response.conformidade.cumpriram) { value = 8 }
    expect.to_equal ($response.conformidade.cancelados) { value = 2 }
  }

  test "faixas e nao calculaveis" {
    input = {
      paradas: [{calculavel: false, motivo: "transicao_desencadeada"}],
      riscos: [
        {calculavel: true, estado_contagem: "em_contagem", faixa: "normal"},
        {calculavel: true, estado_contagem: "em_contagem", faixa: "risco"},
        {calculavel: true, estado_contagem: "em_contagem", faixa: "critico"},
        {calculavel: true, estado_contagem: "em_contagem", faixa: "violado"},
        {calculavel: false, motivo: "sem_sla_aplicado"}
      ],
      cancelados: 0, status_nao_canonicos: 1
    }
    expect.to_be_null ($response.conformidade.percentual)
    expect.to_equal ($response.conformidade.nao_calculaveis) { value = 1 }
    expect.to_equal ($response.risco.normal) { value = 1 }
    expect.to_equal ($response.risco.risco) { value = 1 }
    expect.to_equal ($response.risco.critico) { value = 1 }
    expect.to_equal ($response.risco.violado) { value = 1 }
    expect.to_equal ($response.risco.nao_calculaveis) { value = 1 }
    expect.to_equal ($response.risco.status_nao_canonicos) { value = 1 }
  }
  guid = "V4AuKuZk_FPoQCckYXKk1HHooEw"
}
