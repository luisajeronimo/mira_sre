// Reconstrói os tempos de um Totem a partir de fatos persistidos já consultados.
function "indicadores/calcular_totem_confiabilidade" {
  input {
    timestamp t0
    timestamp t1
    int? lojas_id?
    timestamp? primeira_telemetria?
    json[] eventos
    json[] vinculos
  }

  stack {
    var $inicio_observavel { value = $input.t0|max:1791169200000 }
    var $sem_observacao { value = $input.primeira_telemetria == null }
    conditional {
      if ($input.primeira_telemetria != null) {
        var.update $inicio_observavel { value = $inicio_observavel|max:$input.primeira_telemetria }
      }
    }

    var $observado_ms { value = 0 }
    conditional {
      if (!$sem_observacao && $input.t1 > $inicio_observavel) {
        function.run "indicadores/duracao_loja_intervalo" {
          input = {inicio: $inicio_observavel, fim: $input.t1, lojas_id: $input.lojas_id, vinculos: $input.vinculos}
        } as $observacao
        var.update $observado_ms { value = $observacao.duracao_ms }
      }
    }
    conditional {
      if ($observado_ms == 0) {
        var.update $sem_observacao { value = true }
      }
    }

    var $indisponivel_ms { value = 0 }
    var $disponibilidade_invalida { value = false }
    var $mttd_eventos { value = [] }
    var $mttr_eventos { value = [] }
    var $mttd_erros_por_dia { value = [] }
    var $mttr_erros_por_dia { value = [] }
    var $mttd_inconsistentes { value = 0 }
    var $mttr_inconsistentes { value = 0 }
    var $abertas { value = 0 }
    var $estado_anterior { value = null }
    var $offline_inicio { value = null }
    var $par_invalido { value = false }

    foreach ($input.eventos) {
      each as $evento {
        conditional {
          if ($evento.status == "offline") {
            var $loja_mttd { value = true }
            conditional {
              if ($input.lojas_id != null) {
                function.run "indicadores/loja_no_instante" {
                  input = {instante: $evento.detectado_em, vinculos: $input.vinculos}
                } as $loja_deteccao
                var.update $loja_mttd { value = $loja_deteccao.lojas_id == $input.lojas_id }
              }
            }
            conditional {
              if ($loja_mttd && $evento.detectado_em >= $input.t0 && $evento.detectado_em < $input.t1) {
                conditional {
                  if ($evento.telemetria_timestamp != null && $evento.detectado_em >= $evento.telemetria_timestamp) {
                    var $duracao_mttd_ms { value = $evento.detectado_em - $evento.telemetria_timestamp }
                    var $dia_mttd { value = $evento.detectado_em|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
                    array.push $mttd_eventos {
                      value = {dia: $dia_mttd, duracao_ms: $duracao_mttd_ms}
                    }
                  }
                  else {
                    var.update $mttd_inconsistentes { value = $mttd_inconsistentes + 1 }
                    array.push $mttd_erros_por_dia { value = $evento.detectado_em|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
                  }
                }
              }
            }

            conditional {
              if ($estado_anterior == "offline") {
                var.update $par_invalido { value = true }
                conditional {
                  if (!$sem_observacao && $evento.detectado_em >= $inicio_observavel && $evento.detectado_em < $input.t1) {
                    var.update $disponibilidade_invalida { value = true }
                  }
                }
              }
              else {
                var.update $offline_inicio { value = $evento.telemetria_timestamp }
                var.update $par_invalido { value = $evento.telemetria_timestamp == null }
                conditional {
                  if ($par_invalido && !$sem_observacao && $evento.detectado_em >= $inicio_observavel && $evento.detectado_em < $input.t1) {
                    var.update $disponibilidade_invalida { value = true }
                  }
                }
              }
            }
            var.update $estado_anterior { value = "offline" }
          }
          elseif ($evento.status == "online") {
            conditional {
              if ($estado_anterior == "offline") {
                var $fim_online { value = $evento.telemetria_timestamp }
                var $par_valido { value = !$par_invalido && $offline_inicio != null && $fim_online != null && $fim_online >= $offline_inicio }
                var $marco_contagem_mttr { value = $fim_online != null ? $fim_online : $evento.detectado_em }
                var $loja_mttr { value = true }
                conditional {
                  if ($input.lojas_id != null) {
                    function.run "indicadores/loja_no_instante" {
                      input = {instante: $marco_contagem_mttr, vinculos: $input.vinculos}
                    } as $loja_recuperacao
                    var.update $loja_mttr { value = $loja_recuperacao.lojas_id == $input.lojas_id }
                  }
                }
                conditional {
                  if ($marco_contagem_mttr >= $input.t0 && $marco_contagem_mttr < $input.t1 && $loja_mttr) {
                    conditional {
                      if ($par_valido) {
                        var $duracao_mttr_ms { value = $fim_online - $offline_inicio }
                        var $dia_mttr { value = $fim_online|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
                        array.push $mttr_eventos {
                          value = {dia: $dia_mttr, duracao_ms: $duracao_mttr_ms}
                        }
                      }
                      else {
                        var.update $mttr_inconsistentes { value = $mttr_inconsistentes + 1 }
                        array.push $mttr_erros_por_dia { value = $marco_contagem_mttr|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
                      }
                    }
                  }
                }
                conditional {
                  if ($par_valido && !$sem_observacao) {
                    var $trecho_inicio { value = $offline_inicio|max:$inicio_observavel }
                    var $trecho_fim { value = $fim_online|min:$input.t1 }
                    conditional {
                      if ($trecho_fim > $trecho_inicio) {
                        function.run "indicadores/duracao_loja_intervalo" {
                          input = {inicio: $trecho_inicio, fim: $trecho_fim, lojas_id: $input.lojas_id, vinculos: $input.vinculos}
                        } as $trecho_indisponivel
                        var.update $indisponivel_ms { value = $indisponivel_ms + $trecho_indisponivel.duracao_ms }
                      }
                    }
                  }
                  elseif (!$sem_observacao && $evento.detectado_em >= $inicio_observavel && $evento.detectado_em < $input.t1) {
                    var.update $disponibilidade_invalida { value = true }
                  }
                }
                conditional {
                  if ($offline_inicio != null && $offline_inicio < $input.t1 && $fim_online != null && $fim_online >= $input.t1) {
                    var $loja_aberta { value = true }
                    conditional {
                      if ($input.lojas_id != null) {
                        function.run "indicadores/loja_no_instante" {
                          input = {instante: $input.t1 - 1, vinculos: $input.vinculos}
                        } as $loja_no_fim
                        var.update $loja_aberta { value = $loja_no_fim.lojas_id == $input.lojas_id }
                      }
                    }
                    conditional {
                      if ($loja_aberta) {
                        var.update $abertas { value = $abertas + 1 }
                      }
                    }
                  }
                }
              }
              elseif ($estado_anterior == "online" && !$sem_observacao && $evento.detectado_em >= $inicio_observavel && $evento.detectado_em < $input.t1) {
                var.update $disponibilidade_invalida { value = true }
              }
            }
            var.update $offline_inicio { value = null }
            var.update $par_invalido { value = false }
            var.update $estado_anterior { value = "online" }
          }
        }
      }
    }

    conditional {
      if ($estado_anterior == "offline" && $offline_inicio != null && $offline_inicio < $input.t1) {
        var $loja_aberta_final { value = true }
        conditional {
          if ($input.lojas_id != null) {
            function.run "indicadores/loja_no_instante" {
              input = {instante: $input.t1 - 1, vinculos: $input.vinculos}
            } as $loja_fim_final
            var.update $loja_aberta_final { value = $loja_fim_final.lojas_id == $input.lojas_id }
          }
        }
        conditional {
          if ($loja_aberta_final) {
            var.update $abertas { value = $abertas + 1 }
          }
        }
        conditional {
          if (!$par_invalido && !$sem_observacao) {
            var $trecho_inicio_aberto { value = $offline_inicio|max:$inicio_observavel }
            conditional {
              if ($input.t1 > $trecho_inicio_aberto) {
                function.run "indicadores/duracao_loja_intervalo" {
                  input = {inicio: $trecho_inicio_aberto, fim: $input.t1, lojas_id: $input.lojas_id, vinculos: $input.vinculos}
                } as $trecho_aberto
                var.update $indisponivel_ms { value = $indisponivel_ms + $trecho_aberto.duracao_ms }
              }
            }
          }
          else {
            var.update $disponibilidade_invalida { value = true }
          }
        }
      }
    }
  }

  response = {
    observado_ms: $observado_ms,
    indisponivel_ms: $indisponivel_ms,
    sem_observacao: $sem_observacao,
    disponibilidade_invalida: $disponibilidade_invalida,
    mttd_eventos: $mttd_eventos,
    mttr_eventos: $mttr_eventos,
    mttd_erros_por_dia: $mttd_erros_por_dia,
    mttr_erros_por_dia: $mttr_erros_por_dia,
    mttd_inconsistentes: $mttd_inconsistentes,
    mttr_inconsistentes: $mttr_inconsistentes,
    abertas: $abertas
  }

  test "intervalo e medias conhecidas" {
    input = {
      t0: 1792000000000,
      t1: 1792086400000,
      lojas_id: null,
      primeira_telemetria: 1792000000000,
      eventos: [
        {status: "online", detectado_em: 1792000000000, telemetria_timestamp: 1792000000000},
        {status: "offline", detectado_em: 1792037080000, telemetria_timestamp: 1792036000000},
        {status: "online", detectado_em: 1792039840000, telemetria_timestamp: 1792039720000}
      ],
      vinculos: []
    }
    expect.to_equal ($response.observado_ms) { value = 86400000 }
    expect.to_equal ($response.indisponivel_ms) { value = 3720000 }
    expect.to_equal ($response.mttd_eventos) { value = [{dia: "2026-10-15", duracao_ms: 1080000}] }
    expect.to_equal ($response.mttr_eventos) { value = [{dia: "2026-10-15", duracao_ms: 3720000}] }
    expect.to_equal ($response.disponibilidade_invalida) { value = false }
  }

  test "intervalo aberto cruza periodo" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: null,
      primeira_telemetria: 1791999000000,
      eventos: [{status: "offline", detectado_em: 1791999700000, telemetria_timestamp: 1791999400000}],
      vinculos: []
    }
    expect.to_equal ($response.observado_ms) { value = 3600000 }
    expect.to_equal ($response.indisponivel_ms) { value = 3600000 }
    expect.to_equal ($response.abertas) { value = 1 }
    expect.to_equal ($response.mttr_eventos) { value = [] }
  }

  test "corte historico limita observacao" {
    input = {t0: 1790996400000, t1: 1791255600000, lojas_id: null, primeira_telemetria: 1790996400000, eventos: [], vinculos: []}
    expect.to_equal ($response.observado_ms) { value = 86400000 }
    expect.to_equal ($response.sem_observacao) { value = false }
  }

  test "primeira telemetria inicia observacao" {
    input = {t0: 1791169200000, t1: 1791342000000, lojas_id: null, primeira_telemetria: 1791255600000, eventos: [], vinculos: []}
    expect.to_equal ($response.observado_ms) { value = 86400000 }
  }

  test "totem sem primeira telemetria nao e observado" {
    input = {t0: 1792000000000, t1: 1792003600000, lojas_id: null, primeira_telemetria: null, eventos: [], vinculos: []}
    expect.to_equal ($response.observado_ms) { value = 0 }
    expect.to_equal ($response.sem_observacao) { value = true }
  }

  test "recuperacao iniciada antes do periodo entra no mttr" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: null,
      primeira_telemetria: 1791996400000,
      eventos: [
        {status: "offline", detectado_em: 1791998800000, telemetria_timestamp: 1791998200000},
        {status: "online", detectado_em: 1792001860000, telemetria_timestamp: 1792001800000}
      ],
      vinculos: []
    }
    expect.to_equal ($response.indisponivel_ms) { value = 1800000 }
    expect.to_equal ($response.mttr_eventos) { value = [{dia: "2026-10-14", duracao_ms: 3600000}] }
  }

  test "loja recebe so trecho comprovado" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: 1,
      primeira_telemetria: 1792000000000,
      eventos: [{status: "offline", detectado_em: 1792000600000, telemetria_timestamp: 1792000000000}],
      vinculos: [{efetivado_em: 1792000000000, loja_destino_id: 1}, {efetivado_em: 1792001800000, loja_destino_id: 2}]
    }
    expect.to_equal ($response.observado_ms) { value = 1800000 }
    expect.to_equal ($response.indisponivel_ms) { value = 1800000 }
  }

  test "estado repetido invalida disponibilidade" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: null,
      primeira_telemetria: 1792000000000,
      eventos: [
        {status: "online", detectado_em: 1792000000000, telemetria_timestamp: 1792000000000},
        {status: "online", detectado_em: 1792001200000, telemetria_timestamp: 1792001200000}
      ],
      vinculos: []
    }
    expect.to_equal ($response.disponibilidade_invalida) { value = true }
  }

  test "marcos ausentes contam erros no dia conhecido" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: null,
      primeira_telemetria: 1792000000000,
      eventos: [
        {status: "offline", detectado_em: 1792000600000, telemetria_timestamp: null},
        {status: "online", detectado_em: 1792001210000, telemetria_timestamp: 1792001200000}
      ],
      vinculos: []
    }
    expect.to_equal ($response.mttd_eventos) { value = [] }
    expect.to_equal ($response.mttr_eventos) { value = [] }
    expect.to_equal ($response.mttd_inconsistentes) { value = 1 }
    expect.to_equal ($response.mttr_inconsistentes) { value = 1 }
    expect.to_equal ($response.mttd_erros_por_dia) { value = ["2026-10-14"] }
    expect.to_equal ($response.mttr_erros_por_dia) { value = ["2026-10-14"] }
    expect.to_equal ($response.disponibilidade_invalida) { value = true }
  }

  test "online sem telemetria conta erro na loja historica da deteccao" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: 1,
      primeira_telemetria: 1792000000000,
      eventos: [
        {status: "offline", detectado_em: 1792000600000, telemetria_timestamp: 1792000000000},
        {status: "online", detectado_em: 1792001210000, telemetria_timestamp: null}
      ],
      vinculos: [{efetivado_em: 1792000000000, loja_destino_id: 1}, {efetivado_em: 1792001800000, loja_destino_id: 2}]
    }
    expect.to_equal ($response.mttr_eventos) { value = [] }
    expect.to_equal ($response.mttr_inconsistentes) { value = 1 }
    expect.to_equal ($response.mttr_erros_por_dia) { value = ["2026-10-14"] }
    expect.to_equal ($response.disponibilidade_invalida) { value = true }
  }

  test "online sem telemetria nao migra erro para loja posterior" {
    input = {
      t0: 1792000000000,
      t1: 1792003600000,
      lojas_id: 2,
      primeira_telemetria: 1792000000000,
      eventos: [
        {status: "offline", detectado_em: 1792000600000, telemetria_timestamp: 1792000000000},
        {status: "online", detectado_em: 1792001210000, telemetria_timestamp: null}
      ],
      vinculos: [{efetivado_em: 1792000000000, loja_destino_id: 1}, {efetivado_em: 1792001800000, loja_destino_id: 2}]
    }
    expect.to_equal ($response.mttr_inconsistentes) { value = 0 }
    expect.to_equal ($response.mttr_erros_por_dia) { value = [] }
  }
  guid = "bqWl85tjPC6cyzSF3pTHGP_e8as"
}
