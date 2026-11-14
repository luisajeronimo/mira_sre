// Agregação executiva sob demanda a partir de fatos persistidos.
function "indicadores/consultar_disponibilidade_confiabilidade" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    timestamp t0
    timestamp t1
    text? visao?
    int? lojas_id?
    int? ativos_referencia_id?
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "diretoria sem eventos": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "medias conhecidas": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "online sem timestamp na serie": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "rede pondera tempo observado": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "total nao usa media de medias diarias": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "historico invalido impede percentual": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "hoje sem eventos": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "hoje medias conhecidas": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "hoje transferencia de loja": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "hoje historico invalido localizado": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "hoje intervalo incompleto": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "hoje fora do dia atual": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "visao invalida": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "futuro fora de hoje": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "gerente negado": {id: 8, role: "gerente", deve_trocar_senha: false}
        "tecnico autorizado": {id: 3, role: "tecnico", deve_trocar_senha: false}
        "administrador autorizado": {id: 2, role: "administrador", deve_trocar_senha: false}
        "troca pendente negada": {id: 4, role: "diretoria", deve_trocar_senha: true}
        "periodo invalido": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "loja invalida": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "totem invalido": {id: 4, role: "diretoria", deve_trocar_senha: false}
      }
    } as $diretoria
    precondition (($diretoria.role == "tecnico" || $diretoria.role == "diretoria" || $diretoria.role == "administrador") && $diretoria.deve_trocar_senha == false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    var $agora {
      value = now
      mock = {"hoje sem eventos": 1791999000000, "hoje medias conhecidas": 1792020600000, "hoje transferencia de loja": 1792008000000, "hoje historico invalido localizado": 1792020600000, "hoje intervalo incompleto": 1791999000000, "hoje fora do dia atual": 1791999000000, "visao invalida": 1791999000000, "futuro fora de hoje": 1791999000000}
    }
    var $visao_hoje { value = $input.visao == "hoje" }
    precondition ($input.visao == null || $visao_hoje) {
      error_type = "inputerror"
      error = "Visão inválida."
    }
    precondition ($input.t0 < $input.t1) {
      error_type = "inputerror"
      error = "Período inválido."
    }
    conditional {
      if ($visao_hoje) {
        var $hoje_local { value = $agora|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
        var $amanha_local { value = ($agora|transform_timestamp:"+1 day":"America/Sao_Paulo")|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
        var $inicio_local { value = $input.t0|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo" }
        var $fim_local { value = $input.t1|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo" }
        precondition ($inicio_local == ($hoje_local ~ " 00:00:00") && $fim_local == ($amanha_local ~ " 00:00:00") && $input.t1 - $input.t0 == 86400000 && $input.t0 < $agora) {
          error_type = "inputerror"
          error = "Período inválido para Hoje."
        }
      }
      else {
        precondition ($input.t1 <= $agora) {
          error_type = "inputerror"
          error = "Período inválido."
        }
      }
    }
    var $observado_ate { value = $visao_hoje ? $agora : $input.t1 }
    conditional {
      if ($input.lojas_id != null) {
        precondition ($input.lojas_id > 0) {
          error_type = "inputerror"
          error = "Loja inválida."
        }
        db.get lojas {
          field_name = "id"
          field_value = $input.lojas_id
          mock = {"loja invalida": null, "hoje transferencia de loja": {id: 1}}
        } as $loja
        precondition ($loja != null) {
          error_type = "inputerror"
          error = "Loja inválida."
        }
      }
    }
    conditional {
      if ($input.ativos_referencia_id != null) {
        precondition ($input.ativos_referencia_id > 0) {
          error_type = "inputerror"
          error = "Totem inválido."
        }
        db.get ativos_referencia {
          field_name = "id"
          field_value = $input.ativos_referencia_id
          mock = {"totem invalido": null}
        } as $ativo_filtrado
        precondition ($ativo_filtrado != null) {
          error_type = "inputerror"
          error = "Totem inválido."
        }
      }
    }

    db.query ativos_referencia {
      where = $db.ativos_referencia.id ==? $input.ativos_referencia_id
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "diretoria sem eventos": [],
        "hoje sem eventos": [],
        "medias conhecidas": [{id: 17}],
        "hoje medias conhecidas": [{id: 17}],
        "hoje transferencia de loja": [{id: 17}],
        "hoje historico invalido localizado": [{id: 17}],
        "online sem timestamp na serie": [{id: 17}],
        "rede pondera tempo observado": [],
        "total nao usa media de medias diarias": [],
        "historico invalido impede percentual": [{id: 17}],
        "administrador autorizado": [],
        "tecnico autorizado": []
      }
    } as $ativos

    var $observado_ms {
      value = 0
      mock = {"rede pondera tempo observado": 93600000}
    }
    var $indisponivel_ms {
      value = 0
      mock = {"rede pondera tempo observado": 5520000}
    }
    var $totens_incluidos { value = 0 }
    var $totens_sem_observacao { value = 0 }
    var $totens_invalidos { value = 0 }
    var $mttd_todos {
      value = []
      mock = {"total nao usa media de medias diarias": [{dia: "2026-10-14", duracao_ms: 600000}, {dia: "2026-10-14", duracao_ms: 1200000}, {dia: "2026-10-15", duracao_ms: 3600000}]}
    }
    var $mttr_todos { value = [] }
    var $mttd_erros_por_dia { value = [] }
    var $mttr_erros_por_dia { value = [] }
    var $mttd_inconsistentes { value = 0 }
    var $mttr_inconsistentes { value = 0 }
    var $abertas { value = 0 }
    var $horas_totens { value = [] }

    foreach ($ativos) {
      each as $ativo {
        db.query historico_vinculos_totem_loja {
          where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $ativo.id
          sort = {historico_vinculos_totem_loja.efetivado_em: "asc"}
          return = {type: "list"}
          mock = {
        "medias conhecidas": [],
        "hoje medias conhecidas": [],
        "hoje transferencia de loja": [{efetivado_em: 1791997200000, loja_destino_id: 1}, {efetivado_em: 1792002600000, loja_destino_id: 2}],
        "hoje historico invalido localizado": [],
        "online sem timestamp na serie": [],
        "historico invalido impede percentual": [],
        "administrador autorizado": [],
        "tecnico autorizado": []
      }
        } as $vinculos

        var $loja_relacionada { value = true }
        conditional {
          if ($input.lojas_id != null) {
            function.run "indicadores/duracao_loja_intervalo" {
              input = {inicio: $input.t0, fim: $observado_ate, lojas_id: $input.lojas_id, vinculos: $vinculos}
            } as $vinculo_no_periodo
            var.update $loja_relacionada { value = $vinculo_no_periodo.duracao_ms > 0 }
          }
        }
        conditional {
          if (!$loja_relacionada) {
            continue
          }
        }

        db.query telemetria_equipamentos {
          where = $db.telemetria_equipamentos.ativos_referencia_id == $ativo.id && $db.telemetria_equipamentos.evento_timestamp != null
          sort = {telemetria_equipamentos.evento_timestamp: "asc"}
          return = {type: "single"}
          mock = {
        "medias conhecidas": {evento_timestamp: 1792000000000},
        "hoje medias conhecidas": {evento_timestamp: 1792000000000},
        "hoje transferencia de loja": {evento_timestamp: 1791997200000},
        "hoje historico invalido localizado": {evento_timestamp: 1792000000000},
        "online sem timestamp na serie": {evento_timestamp: 1792000000000},
        "historico invalido impede percentual": {evento_timestamp: 1792000000000},
        "administrador autorizado": [],
        "tecnico autorizado": []
      }
        } as $primeira_telemetria

        db.query historico_disponibilidade_totens {
          join = {
            telemetria: {
              table: "telemetria_equipamentos"
              type: "left"
              where: $db.historico_disponibilidade_totens.telemetria_referencia_id == $db.telemetria.id
            }
          }
          eval = {telemetria_timestamp: $db.telemetria.evento_timestamp}
          where = $db.historico_disponibilidade_totens.ativos_referencia_id == $ativo.id
          sort = {historico_disponibilidade_totens.detectado_em: "asc"}
          return = {type: "list"}
          mock = {
        "medias conhecidas": [
            {status: "offline", detectado_em: 1792004680000, telemetria_timestamp: 1792003600000},
            {status: "online", detectado_em: 1792007380000, telemetria_timestamp: 1792007320000},
            {status: "offline", detectado_em: 1792015600000, telemetria_timestamp: 1792014400000},
            {status: "online", detectado_em: 1792016860000, telemetria_timestamp: 1792016800000}
          ],
        "hoje medias conhecidas": [
            {status: "offline", detectado_em: 1792004680000, telemetria_timestamp: 1792003600000},
            {status: "online", detectado_em: 1792007380000, telemetria_timestamp: 1792007320000},
            {status: "offline", detectado_em: 1792015600000, telemetria_timestamp: 1792014400000},
            {status: "online", detectado_em: 1792016860000, telemetria_timestamp: 1792016800000}
          ],
        "hoje transferencia de loja": [
            {status: "offline", detectado_em: 1791999600000, telemetria_timestamp: 1791999000000},
            {status: "online", detectado_em: 1792006800000, telemetria_timestamp: 1792006200000}
          ],
        "hoje historico invalido localizado": [
            {status: "offline", detectado_em: 1792000600000, telemetria_timestamp: null},
            {status: "online", detectado_em: 1792001210000, telemetria_timestamp: 1792001200000}
          ],
        "online sem timestamp na serie": [
            {status: "offline", detectado_em: 1792000600000, telemetria_timestamp: 1792000000000},
            {status: "online", detectado_em: 1792001210000, telemetria_timestamp: null}
          ],
        "historico invalido impede percentual": [
            {status: "offline", detectado_em: 1792000600000, telemetria_timestamp: null},
            {status: "online", detectado_em: 1792001210000, telemetria_timestamp: 1792001200000}
          ],
        "administrador autorizado": [],
        "tecnico autorizado": []
      }
        } as $eventos

        function.run "indicadores/calcular_totem_confiabilidade" {
          input = {
            t0: $input.t0,
            t1: $observado_ate,
            lojas_id: $input.lojas_id,
            primeira_telemetria: $primeira_telemetria != null ? $primeira_telemetria.evento_timestamp : null,
            eventos: $eventos,
            vinculos: $vinculos
          }
        } as $calculado

        conditional {
          if ($visao_hoje) {
            for (24) {
              each as $hora_indice {
                var $hora_inicio { value = $input.t0 + $hora_indice * 3600000 }
                var $hora_fim { value = ($hora_inicio + 3600000)|min:$observado_ate }
                conditional {
                  if ($hora_fim > $hora_inicio) {
                    function.run "indicadores/calcular_totem_confiabilidade" {
                      input = {
                        t0: $hora_inicio,
                        t1: $hora_fim,
                        lojas_id: $input.lojas_id,
                        primeira_telemetria: $primeira_telemetria != null ? $primeira_telemetria.evento_timestamp : null,
                        eventos: $eventos,
                        vinculos: $vinculos
                      }
                    } as $hora_calculada
                    conditional {
                      if (!$hora_calculada.sem_observacao) {
                        array.push $horas_totens {
                          value = {indice: $hora_indice, observado_ms: $hora_calculada.observado_ms, indisponivel_ms: $hora_calculada.indisponivel_ms, invalido: $hora_calculada.disponibilidade_invalida}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }

        conditional {
          if ($calculado.sem_observacao) {
            var.update $totens_sem_observacao { value = $totens_sem_observacao + 1 }
          }
          else {
            var.update $totens_incluidos { value = $totens_incluidos + 1 }
            var.update $observado_ms { value = $observado_ms + $calculado.observado_ms }
            var.update $indisponivel_ms { value = $indisponivel_ms + $calculado.indisponivel_ms }
            conditional {
              if ($calculado.disponibilidade_invalida) {
                var.update $totens_invalidos { value = $totens_invalidos + 1 }
              }
            }
          }
        }
        foreach ($calculado.mttd_eventos) {
          each as $deteccao {
            array.push $mttd_todos { value = $deteccao }
          }
        }
        foreach ($calculado.mttr_eventos) {
          each as $recuperacao {
            array.push $mttr_todos { value = $recuperacao }
          }
        }
        foreach ($calculado.mttd_erros_por_dia) {
          each as $dia_erro_mttd {
            array.push $mttd_erros_por_dia { value = $dia_erro_mttd }
          }
        }
        foreach ($calculado.mttr_erros_por_dia) {
          each as $dia_erro_mttr {
            array.push $mttr_erros_por_dia { value = $dia_erro_mttr }
          }
        }
        var.update $mttd_inconsistentes { value = $mttd_inconsistentes + $calculado.mttd_inconsistentes }
        var.update $mttr_inconsistentes { value = $mttr_inconsistentes + $calculado.mttr_inconsistentes }
        var.update $abertas { value = $abertas + $calculado.abertas }
      }
    }

    var $disponibilidade_percentual { value = null }
    conditional {
      if ($observado_ms > 0 && $totens_invalidos == 0) {
        var.update $disponibilidade_percentual { value = ((1 - ($indisponivel_ms / $observado_ms)) * 100)|round:2 }
      }
    }

    var $pontos_horarios { value = [] }
    conditional {
      if ($visao_hoje) {
        for (24) {
          each as $indice_hora {
            var $hora_observado_ms { value = 0 }
            var $hora_indisponivel_ms { value = 0 }
            var $hora_invalidos { value = 0 }
            foreach ($horas_totens) {
              each as $totem_hora {
                conditional {
                  if ($totem_hora.indice == $indice_hora) {
                    var.update $hora_observado_ms { value = $hora_observado_ms + $totem_hora.observado_ms }
                    var.update $hora_indisponivel_ms { value = $hora_indisponivel_ms + $totem_hora.indisponivel_ms }
                    conditional {
                      if ($totem_hora.invalido) {
                        var.update $hora_invalidos { value = $hora_invalidos + 1 }
                      }
                    }
                  }
                }
              }
            }
            var $hora_percentual { value = null }
            conditional {
              if ($hora_observado_ms > 0 && $hora_invalidos == 0) {
                var.update $hora_percentual { value = ((1 - ($hora_indisponivel_ms / $hora_observado_ms)) * 100)|round:2 }
              }
            }
            array.push $pontos_horarios {
              value = {inicio: ($input.t0 + $indice_hora * 3600000), fim: ($input.t0 + ($indice_hora + 1) * 3600000), percentual: $hora_percentual, observado_ms: $hora_observado_ms, indisponivel_ms: $hora_indisponivel_ms, totens_invalidos: $hora_invalidos}
            }
          }
        }
      }
    }

    var $mttd_soma { value = 0 }
    foreach ($mttd_todos) {
      each as $evento_mttd {
        var.update $mttd_soma { value = $mttd_soma + $evento_mttd.duracao_ms }
      }
    }
    var $mttr_soma { value = 0 }
    foreach ($mttr_todos) {
      each as $evento_mttr {
        var.update $mttr_soma { value = $mttr_soma + $evento_mttr.duracao_ms }
      }
    }
    var $mttd_minutos { value = null }
    var $mttr_minutos { value = null }
    conditional {
      if (($mttd_todos|count) > 0) {
        var.update $mttd_minutos { value = ($mttd_soma / ($mttd_todos|count) / 60000)|round:2 }
      }
    }
    conditional {
      if (($mttr_todos|count) > 0) {
        var.update $mttr_minutos { value = ($mttr_soma / ($mttr_todos|count) / 60000)|round:2 }
      }
    }

    var $serie { value = [] }
    var $dia_inicio { value = $input.t0|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
    var $dia_limite { value = ($observado_ate - 1)|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
    while ($dia_inicio <= $dia_limite) {
      each {
        var $dia_texto { value = $dia_inicio }
        var $mttd_dia_soma { value = 0 }
        var $mttd_dia_contagem { value = 0 }
        var $mttd_dia_erros { value = 0 }
        var $mttr_dia_soma { value = 0 }
        var $mttr_dia_contagem { value = 0 }
        var $mttr_dia_erros { value = 0 }
        foreach ($mttd_todos) {
          each as $ponto_mttd {
            conditional {
              if ($ponto_mttd.dia == $dia_texto) {
                var.update $mttd_dia_soma { value = $mttd_dia_soma + $ponto_mttd.duracao_ms }
                var.update $mttd_dia_contagem { value = $mttd_dia_contagem + 1 }
              }
            }
          }
        }
        foreach ($mttr_todos) {
          each as $ponto_mttr {
            conditional {
              if ($ponto_mttr.dia == $dia_texto) {
                var.update $mttr_dia_soma { value = $mttr_dia_soma + $ponto_mttr.duracao_ms }
                var.update $mttr_dia_contagem { value = $mttr_dia_contagem + 1 }
              }
            }
          }
        }
        foreach ($mttd_erros_por_dia) {
          each as $erro_mttd {
            conditional {
              if ($erro_mttd == $dia_texto) {
                var.update $mttd_dia_erros { value = $mttd_dia_erros + 1 }
              }
            }
          }
        }
        foreach ($mttr_erros_por_dia) {
          each as $erro_mttr {
            conditional {
              if ($erro_mttr == $dia_texto) {
                var.update $mttr_dia_erros { value = $mttr_dia_erros + 1 }
              }
            }
          }
        }
        var $mttd_dia_minutos { value = null }
        var $mttr_dia_minutos { value = null }
        conditional {
          if ($mttd_dia_contagem > 0) {
            var.update $mttd_dia_minutos { value = ($mttd_dia_soma / $mttd_dia_contagem / 60000)|round:2 }
          }
        }
        conditional {
          if ($mttr_dia_contagem > 0) {
            var.update $mttr_dia_minutos { value = ($mttr_dia_soma / $mttr_dia_contagem / 60000)|round:2 }
          }
        }
        array.push $serie {
          value = {dia: $dia_texto, mttd_minutos: $mttd_dia_minutos, mttr_minutos: $mttr_dia_minutos, mttd_eventos: $mttd_dia_contagem, mttd_inconsistentes: $mttd_dia_erros, mttr_recuperacoes: $mttr_dia_contagem, mttr_inconsistentes: $mttr_dia_erros}
        }
        var.update $dia_inicio { value = ($dia_inicio|transform_timestamp:"+1 day":"America/Sao_Paulo")|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
      }
    }
    var $resultado {
      value = {
        periodo: {t0: $input.t0, t1: $input.t1, fuso: "America/Sao_Paulo"},
        filtros: {lojas_id: $input.lojas_id, ativos_referencia_id: $input.ativos_referencia_id},
        disponibilidade: {percentual: $disponibilidade_percentual, observado_ms: $observado_ms, indisponivel_ms: $indisponivel_ms, totens_incluidos: $totens_incluidos, totens_sem_observacao: $totens_sem_observacao, totens_invalidos: $totens_invalidos},
        mttd: {minutos: $mttd_minutos, eventos: ($mttd_todos|count), inconsistentes: $mttd_inconsistentes},
        mttr: {minutos: $mttr_minutos, recuperacoes: ($mttr_todos|count), inconsistentes: $mttr_inconsistentes, abertas: $abertas},
        serie: $serie
      }
    }
    conditional {
      if ($visao_hoje) {
        var.update $resultado { value = $resultado|set:"disponibilidade_horaria":{observado_ate: $observado_ate, pontos: $pontos_horarios} }
      }
    }
  }

  response = $resultado

  test "diretoria sem eventos" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000}
    expect.to_be_null ($response.disponibilidade.percentual)
    expect.to_be_null ($response.mttd.minutos)
    expect.to_be_null ($response.mttr.minutos)
    expect.to_equal ($response.serie) { value = [{dia: "2026-10-14", mttd_minutos: null, mttr_minutos: null, mttd_eventos: 0, mttd_inconsistentes: 0, mttr_recuperacoes: 0, mttr_inconsistentes: 0}] }
  }

  test "medias conhecidas" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792086400000}
    expect.to_equal ($response.mttd.minutos) { value = 19 }
    expect.to_equal ($response.mttr.minutos) { value = 51 }
    expect.to_equal ($response.disponibilidade.observado_ms) { value = 86400000 }
    expect.to_equal ($response.disponibilidade.indisponivel_ms) { value = 6120000 }
  }

  test "online sem timestamp na serie" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000}
    expect.to_be_null ($response.mttr.minutos)
    expect.to_equal ($response.mttr.inconsistentes) { value = 1 }
    expect.to_equal ($response.serie) { value = [{dia: "2026-10-14", mttd_minutos: 10, mttr_minutos: null, mttd_eventos: 1, mttd_inconsistentes: 0, mttr_recuperacoes: 0, mttr_inconsistentes: 1}] }
  }

  test "rede pondera tempo observado" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000}
    expect.to_equal ($response.disponibilidade.observado_ms) { value = 93600000 }
    expect.to_equal ($response.disponibilidade.indisponivel_ms) { value = 5520000 }
    expect.to_equal ($response.disponibilidade.percentual) { value = 94.10 }
  }

  test "total nao usa media de medias diarias" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792086400000}
    expect.to_equal ($response.mttd.minutos) { value = 30 }
    expect.to_equal ($response.mttd.eventos) { value = 3 }
    expect.to_equal ($response.serie) {
      value = [
        {dia: "2026-10-14", mttd_minutos: 15, mttr_minutos: null, mttd_eventos: 2, mttd_inconsistentes: 0, mttr_recuperacoes: 0, mttr_inconsistentes: 0},
        {dia: "2026-10-15", mttd_minutos: 60, mttr_minutos: null, mttd_eventos: 1, mttd_inconsistentes: 0, mttr_recuperacoes: 0, mttr_inconsistentes: 0}
      ]
    }
  }

  test "historico invalido impede percentual" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000}
    expect.to_be_null ($response.disponibilidade.percentual)
    expect.to_equal ($response.disponibilidade.totens_invalidos) { value = 1 }
    expect.to_equal ($response.disponibilidade.totens_incluidos) { value = 1 }
  }

  test "hoje sem eventos" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.disponibilidade_horaria.observado_ate) { value = 1791999000000 }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1791946800000, fim: 1791950400000, percentual: null, observado_ms: 0, indisponivel_ms: 0, totens_invalidos: 0} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792029600000, fim: 1792033200000, percentual: null, observado_ms: 0, indisponivel_ms: 0, totens_invalidos: 0} }
  }

  test "hoje medias conhecidas" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.disponibilidade_horaria.observado_ate) { value = 1792020600000 }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792000800000, fim: 1792004400000, percentual: 77.78, observado_ms: 3600000, indisponivel_ms: 800000, totens_invalidos: 0} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792004400000, fim: 1792008000000, percentual: 18.89, observado_ms: 3600000, indisponivel_ms: 2920000, totens_invalidos: 0} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792018800000, fim: 1792022400000, percentual: 100, observado_ms: 1800000, indisponivel_ms: 0, totens_invalidos: 0} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792022400000, fim: 1792026000000, percentual: null, observado_ms: 0, indisponivel_ms: 0, totens_invalidos: 0} }
  }

  test "hoje transferencia de loja" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje", lojas_id: 1}
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1791997200000, fim: 1792000800000, percentual: 50, observado_ms: 3600000, indisponivel_ms: 1800000, totens_invalidos: 0} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792000800000, fim: 1792004400000, percentual: 0, observado_ms: 1800000, indisponivel_ms: 1800000, totens_invalidos: 0} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792004400000, fim: 1792008000000, percentual: null, observado_ms: 0, indisponivel_ms: 0, totens_invalidos: 0} }
  }

  test "hoje historico invalido localizado" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1791997200000, fim: 1792000800000, percentual: null, observado_ms: 800000, indisponivel_ms: 0, totens_invalidos: 1} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792000800000, fim: 1792004400000, percentual: null, observado_ms: 3600000, indisponivel_ms: 0, totens_invalidos: 1} }
    expect.to_contain ($response.disponibilidade_horaria.pontos) { value = {inicio: 1792004400000, fim: 1792008000000, percentual: 100, observado_ms: 3600000, indisponivel_ms: 0, totens_invalidos: 0} }
  }

  test "hoje intervalo incompleto" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000, visao: "hoje"}
    expect.to_throw { exception = "Período inválido para Hoje." }
  }

  test "hoje fora do dia atual" {
    input = {usuarios_id: 4, t0: 1791860400000, t1: 1791946800000, visao: "hoje"}
    expect.to_throw { exception = "Período inválido para Hoje." }
  }

  test "visao invalida" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000, visao: "semana"}
    expect.to_throw { exception = "Visão inválida." }
  }

  test "futuro fora de hoje" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000}
    expect.to_throw { exception = "Período inválido." }
  }

  test "gerente negado" {
    input = {usuarios_id: 8, t0: 1792000000000, t1: 1792003600000}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "tecnico autorizado" {
    input = {usuarios_id: 3, t0: 1792000000000, t1: 1792003600000}
    expect.to_equal ($response.disponibilidade.totens_incluidos) { value = 0 }
  }


  test "administrador autorizado" {
    input = {usuarios_id: 2, t0: 1792000000000, t1: 1792003600000}
    expect.to_equal ($response.disponibilidade.totens_incluidos) { value = 0 }
  }


  test "troca pendente negada" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "periodo invalido" {
    input = {usuarios_id: 4, t0: 1792003600000, t1: 1792000000000}
    expect.to_throw { exception = "Período inválido." }
  }

  test "loja invalida" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000, lojas_id: 999999}
    expect.to_throw { exception = "Loja inválida." }
  }

  test "totem invalido" {
    input = {usuarios_id: 4, t0: 1792000000000, t1: 1792003600000, ativos_referencia_id: 999999}
    expect.to_throw { exception = "Totem inválido." }
  }
  guid = "ZIF8dz6xu61ztGD_IjXtTHWA2lw"
}
