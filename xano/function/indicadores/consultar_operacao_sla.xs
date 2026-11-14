// Agregação executiva de chamados e SLA sem persistir indicadores.
function "indicadores/consultar_operacao_sla" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    timestamp t0
    timestamp t1
    text? visao?
    int? lojas_id?
    int? categorias_servico_id?
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {"diretoria sem chamados": {id: 4, role: "diretoria", deve_trocar_senha: false}, "volume e risco antigo": {id: 4, role: "diretoria", deve_trocar_senha: false}, "categoria filtra chamados": {id: 4, role: "diretoria", deve_trocar_senha: false}, "conformidade resolvido": {id: 4, role: "diretoria", deve_trocar_senha: false}, "cancelado separado": {id: 4, role: "diretoria", deve_trocar_senha: false}, "rejeicao e nova resolucao": {id: 4, role: "diretoria", deve_trocar_senha: false}, "loja antes da transferencia": {id: 4, role: "diretoria", deve_trocar_senha: false}, "loja depois da transferencia": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao sem vinculo global": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao sem vinculo filtrada": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao gerente negado": {id: 8, role: "gerente", deve_trocar_senha: false}, "operacao tecnico autorizado": {id: 3, role: "tecnico", deve_trocar_senha: false}, "operacao administrador autorizado": {id: 2, role: "administrador", deve_trocar_senha: false}, "operacao troca pendente negada": {id: 4, role: "diretoria", deve_trocar_senha: true}, "operacao periodo invertido": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao visao invalida": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao hoje incompleto": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao futuro fora de hoje": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao loja invalida": {id: 4, role: "diretoria", deve_trocar_senha: false}, "operacao categoria invalida": {id: 4, role: "diretoria", deve_trocar_senha: false}}
    } as $diretoria
    precondition (($diretoria.role == "tecnico" || $diretoria.role == "diretoria" || $diretoria.role == "administrador") && $diretoria.deve_trocar_senha == false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    var $agora {
      value = now
      mock = {"diretoria sem chamados": 1791999000000, "volume e risco antigo": 1791999000000, "categoria filtra chamados": 1791999000000, "conformidade resolvido": 1791999000000, "cancelado separado": 1791999000000, "rejeicao e nova resolucao": 1791999000000, "loja antes da transferencia": 1791999000000, "loja depois da transferencia": 1791999000000, "operacao sem vinculo global": 1791999000000, "operacao sem vinculo filtrada": 1791999000000, "operacao periodo invertido": 1791999000000, "operacao visao invalida": 1791999000000, "operacao hoje incompleto": 1791999000000, "operacao futuro fora de hoje": 1791999000000, "operacao loja invalida": 1791999000000, "operacao categoria invalida": 1791999000000}
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
          mock = {"operacao loja invalida": null, "loja antes da transferencia": {id: 1}, "loja depois da transferencia": {id: 2}, "operacao sem vinculo filtrada": {id: 1}}
        } as $loja
        precondition ($loja != null) {
          error_type = "inputerror"
          error = "Loja inválida."
        }
      }
    }
    conditional {
      if ($input.categorias_servico_id != null) {
        precondition ($input.categorias_servico_id > 0) {
          error_type = "inputerror"
          error = "Categoria inválida."
        }
        db.get categorias_servico {
          field_name = "id"
          field_value = $input.categorias_servico_id
          mock = {"operacao categoria invalida": null, "categoria filtra chamados": {id: 2}}
        } as $categoria
        precondition ($categoria != null) {
          error_type = "inputerror"
          error = "Categoria inválida."
        }
      }
    }

    db.query chamados {
      where = $db.chamados.categorias_servico_id ==? $input.categorias_servico_id
      sort = {chamados.id: "asc"}
      return = {type: "list"}
      mock = {
        "diretoria sem chamados": [],
        "volume e risco antigo": [{id: 1, criado_em: 1791980000000, status: "Em Atendimento", categorias_servico_id: 2}, {id: 2, criado_em: 1791860400000, status: "Novo", categorias_servico_id: 2}, {id: 3, criado_em: 1791983600000, status: "Aguardando Terceiro", categorias_servico_id: 2}, {id: 8, criado_em: 1791985400000, status: null, categorias_servico_id: 2}],
        "categoria filtra chamados": [{id: 9, criado_em: 1791980000000, status: "Aguardando Terceiro", categorias_servico_id: 2}, {id: 10, criado_em: 1791980000000, status: "Aguardando Terceiro", categorias_servico_id: 3}],
        "conformidade resolvido": [{id: 4, criado_em: 1791980000000, status: "Resolvido", categorias_servico_id: 2}],
        "cancelado separado": [{id: 5, criado_em: 1791980000000, status: "Cancelado", categorias_servico_id: 2}],
        "rejeicao e nova resolucao": [{id: 7, criado_em: 1791980000000, status: "Resolvido", categorias_servico_id: 2}],
        "loja antes da transferencia": [{id: 6, criado_em: 1791980000000, status: "Aguardando Terceiro", ativos_referencia_id: 17}],
        "loja depois da transferencia": [{id: 6, criado_em: 1791980000000, status: "Aguardando Terceiro", ativos_referencia_id: 17}],
        "operacao sem vinculo global": [{id: 11, criado_em: 1791980000000, status: "Aguardando Terceiro", ativos_referencia_id: 17}],
        "operacao sem vinculo filtrada": [{id: 11, criado_em: 1791980000000, status: "Aguardando Terceiro", ativos_referencia_id: 17}],
        "operacao administrador autorizado": [],
        "operacao tecnico autorizado": []
      }
    } as $chamados

    var $novo { value = 0 }
    var $em_atendimento { value = 0 }
    var $aguardando_solicitante { value = 0 }
    var $aguardando_mudanca { value = 0 }
    var $resolvido { value = 0 }
    var $solucao_rejeitada { value = 0 }
    var $encerrado { value = 0 }
    var $cancelado { value = 0 }
    var $nao_classificados { value = 0 }
    var $total_volume { value = 0 }
    var $conformidade_cancelados { value = 0 }
    var $risco_status_nao_canonicos { value = 0 }
    var $paradas_calculadas { value = [] }
    var $riscos_calculados { value = [] }
    var $chamados_filtrados { value = 0 }

    foreach ($chamados) {
      each as $chamado {
        conditional {
          if ($input.categorias_servico_id != null && $chamado.categorias_servico_id != $input.categorias_servico_id) {
            continue
          }
        }
        conditional {
          if ($input.lojas_id != null) {
            conditional {
              if ($chamado.ativos_referencia_id == null || $chamado.criado_em == null) {
                continue
              }
            }
            db.query historico_vinculos_totem_loja {
              where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $chamado.ativos_referencia_id
              sort = {historico_vinculos_totem_loja.efetivado_em: "asc"}
              return = {type: "list"}
              mock = {
        "loja antes da transferencia": [{efetivado_em: 1791860400000, loja_destino_id: 1}, {efetivado_em: 1791981800000, loja_destino_id: 2}],
        "loja depois da transferencia": [{efetivado_em: 1791860400000, loja_destino_id: 1}, {efetivado_em: 1791981800000, loja_destino_id: 2}],
        "operacao sem vinculo filtrada": [],
        "operacao administrador autorizado": [],
        "operacao tecnico autorizado": []
      }
            } as $vinculos
            function.run "indicadores/loja_no_instante" {
              input = {instante: $chamado.criado_em, vinculos: $vinculos}
            } as $loja_abertura
            conditional {
              if ($loja_abertura.lojas_id != $input.lojas_id) {
                continue
              }
            }
          }
        }
        var.update $chamados_filtrados { value = $chamados_filtrados + 1 }

        conditional {
          if ($chamado.criado_em != null && $chamado.criado_em >= $input.t0 && $chamado.criado_em < $observado_ate) {
            var.update $total_volume { value = $total_volume + 1 }
            conditional {
              if ($chamado.status == "Novo") {
                var.update $novo { value = $novo + 1 }
              }
              elseif ($chamado.status == "Em Atendimento") {
                var.update $em_atendimento { value = $em_atendimento + 1 }
              }
              elseif ($chamado.status == "Aguardando Solicitante") {
                var.update $aguardando_solicitante { value = $aguardando_solicitante + 1 }
              }
              elseif ($chamado.status == "Aguardando Mudança") {
                var.update $aguardando_mudanca { value = $aguardando_mudanca + 1 }
              }
              elseif ($chamado.status == "Resolvido") {
                var.update $resolvido { value = $resolvido + 1 }
              }
              elseif ($chamado.status == "Solução Rejeitada") {
                var.update $solucao_rejeitada { value = $solucao_rejeitada + 1 }
              }
              elseif ($chamado.status == "Encerrado") {
                var.update $encerrado { value = $encerrado + 1 }
              }
              elseif ($chamado.status == "Cancelado") {
                var.update $cancelado { value = $cancelado + 1 }
              }
              else {
                var.update $nao_classificados { value = $nao_classificados + 1 }
              }
            }
          }
        }

        conditional {
          if ($chamado.status == "Resolvido" || $chamado.status == "Encerrado" || $chamado.status == "Cancelado") {
            db.query interacoes_chamado {
              where = $db.interacoes_chamado.chamados_id == $chamado.id && $db.interacoes_chamado.tipo_evento == "alteracao_chamado"
              sort = {interacoes_chamado.criado_em: "desc", interacoes_chamado.id: "desc"}
              return = {type: "list"}
              mock = {
        "conformidade resolvido": [{id: 1, criado_em: 1791981800000, alteracoes: {status: {anterior: "Novo", resultante: "Resolvido"}}}],
        "cancelado separado": [{id: 1, criado_em: 1791981800000, alteracoes: {status: {anterior: "Novo", resultante: "Cancelado"}}}],
        "rejeicao e nova resolucao": [{id: 3, criado_em: 1791987200000, alteracoes: {status: {anterior: "Solução Rejeitada", resultante: "Resolvido"}}}, {id: 2, criado_em: 1791985400000, alteracoes: {status: {anterior: "Resolvido", resultante: "Solução Rejeitada"}}}, {id: 1, criado_em: 1791981800000, alteracoes: {status: {anterior: "Novo", resultante: "Resolvido"}}}],
        "operacao administrador autorizado": [],
        "operacao tecnico autorizado": []
      }
            } as $transicoes
            var $entrada_vigente { value = null }
            var $encontrou_entrada { value = false }
            foreach ($transicoes) {
              each as $transicao {
                conditional {
                  if (!$encontrou_entrada && ($transicao.alteracoes|is_object)) {
                    var $par_status { value = $transicao.alteracoes|get:"status":null }
                    conditional {
                      if (($par_status|is_object) && ($par_status|get:"resultante":null) == $chamado.status) {
                        var.update $encontrou_entrada { value = true }
                        var.update $entrada_vigente { value = $transicao.criado_em }
                      }
                    }
                  }
                }
              }
            }
            conditional {
              if ($entrada_vigente != null && $entrada_vigente >= $input.t0 && $entrada_vigente < $observado_ate) {
                conditional {
                  if ($chamado.status == "Cancelado") {
                    var.update $conformidade_cancelados { value = $conformidade_cancelados + 1 }
                  }
                  else {
                    function.run "service_desk/calcular_consumo_sla_chamado" {
                      input = {chamados_id: $chamado.id, instante_referencia: $agora}
                      mock = {"conformidade resolvido": {calculavel: true, estado_contagem: "pausada", consumo_ms: 7200000, sla_horas_aplicado: 4}, "rejeicao e nova resolucao": {calculavel: true, estado_contagem: "pausada", consumo_ms: 14400000, sla_horas_aplicado: 4}}
                    } as $consumo_parada
                    array.push $paradas_calculadas { value = $consumo_parada }
                  }
                }
              }
            }
          }
          elseif ($chamado.status == "Novo" || $chamado.status == "Em Atendimento" || $chamado.status == "Aguardando Solicitante" || $chamado.status == "Aguardando Mudança" || $chamado.status == "Solução Rejeitada") {
            conditional {
              if ($chamado.criado_em != null && $chamado.criado_em > $agora) {
                array.push $riscos_calculados { value = {calculavel: false} }
              }
              else {
                function.run "service_desk/calcular_consumo_sla_chamado" {
                  input = {chamados_id: $chamado.id, instante_referencia: $agora}
                  mock = {"volume e risco antigo": {calculavel: true, estado_contagem: "em_contagem", faixa: "risco"}}
                } as $consumo_atual
                array.push $riscos_calculados { value = $consumo_atual }
              }
            }
          }
          else {
            var.update $risco_status_nao_canonicos { value = $risco_status_nao_canonicos + 1 }
          }
        }
      }
    }

    function.run "indicadores/resumir_sla_calculado" {
      input = {paradas: $paradas_calculadas, riscos: $riscos_calculados, cancelados: $conformidade_cancelados, status_nao_canonicos: $risco_status_nao_canonicos}
    } as $sla_resumo
  }

  response = {
    periodo: {t0: $input.t0, t1: $input.t1, observado_ate: $observado_ate, fuso: "America/Sao_Paulo"},
    filtros: {lojas_id: $input.lojas_id, categorias_servico_id: $input.categorias_servico_id},
    volumetria: {total: $total_volume, por_status: [{status: "Novo", quantidade: $novo}, {status: "Em Atendimento", quantidade: $em_atendimento}, {status: "Aguardando Solicitante", quantidade: $aguardando_solicitante}, {status: "Aguardando Mudança", quantidade: $aguardando_mudanca}, {status: "Resolvido", quantidade: $resolvido}, {status: "Solução Rejeitada", quantidade: $solucao_rejeitada}, {status: "Encerrado", quantidade: $encerrado}, {status: "Cancelado", quantidade: $cancelado}], nao_classificados: $nao_classificados},
    conformidade: $sla_resumo.conformidade,
    risco: {calculado_em: $agora, normal: $sla_resumo.risco.normal, risco: $sla_resumo.risco.risco, critico: $sla_resumo.risco.critico, violado: $sla_resumo.risco.violado, nao_calculaveis: $sla_resumo.risco.nao_calculaveis, status_nao_canonicos: $sla_resumo.risco.status_nao_canonicos},
    chamados_filtrados: $chamados_filtrados
  }

  test "diretoria sem chamados" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.volumetria.total) { value = 0 }
    expect.to_be_null ($response.conformidade.percentual)
    expect.to_equal ($response.risco.normal) { value = 0 }
    expect.to_equal ($response.periodo.observado_ate) { value = 1791999000000 }
  }

  test "volume e risco antigo" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.volumetria.total) { value = 3 }
    expect.to_equal ($response.volumetria.nao_classificados) { value = 2 }
    expect.to_contain ($response.volumetria.por_status) { value = {status: "Em Atendimento", quantidade: 1} }
    expect.to_equal ($response.risco.risco) { value = 2 }
    expect.to_equal ($response.risco.status_nao_canonicos) { value = 2 }
  }

  test "categoria filtra chamados" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje", categorias_servico_id: 2}
    expect.to_equal ($response.volumetria.total) { value = 1 }
    expect.to_equal ($response.risco.status_nao_canonicos) { value = 1 }
  }

  test "conformidade resolvido" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.conformidade.percentual) { value = 100 }
    expect.to_equal ($response.conformidade.elegiveis) { value = 1 }
    expect.to_equal ($response.conformidade.cumpriram) { value = 1 }
    expect.to_equal ($response.risco.normal) { value = 0 }
  }

  test "cancelado separado" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.conformidade.cancelados) { value = 1 }
    expect.to_equal ($response.conformidade.elegiveis) { value = 0 }
    expect.to_be_null ($response.conformidade.percentual)
  }

  test "rejeicao e nova resolucao" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.conformidade.elegiveis) { value = 1 }
    expect.to_equal ($response.conformidade.cumpriram) { value = 1 }
    expect.to_equal ($response.conformidade.percentual) { value = 100 }
  }

  test "loja antes da transferencia" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje", lojas_id: 1}
    expect.to_equal ($response.volumetria.total) { value = 1 }
  }

  test "loja depois da transferencia" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje", lojas_id: 2}
    expect.to_equal ($response.volumetria.total) { value = 0 }
  }

  test "operacao sem vinculo global" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje"}
    expect.to_equal ($response.volumetria.total) { value = 1 }
  }

  test "operacao sem vinculo filtrada" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000, visao: "hoje", lojas_id: 1}
    expect.to_equal ($response.volumetria.total) { value = 0 }
  }

  test "operacao gerente negado" {
    input = {usuarios_id: 8, t0: 1791946800000, t1: 1791999000000}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  test "operacao tecnico autorizado" {
    input = {usuarios_id: 3, t0: 1791946800000, t1: 1791999000000}
    expect.to_equal ($response.volumetria.total) { value = 0 }
  }

  test "operacao administrador autorizado" {
    input = {usuarios_id: 2, t0: 1791946800000, t1: 1791999000000}
    expect.to_equal ($response.volumetria.total) { value = 0 }
  }

  test "operacao troca pendente negada" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  test "operacao periodo invertido" {
    input = {usuarios_id: 4, t0: 1791999000000, t1: 1791946800000}
    expect.to_throw { exception = "Período inválido." }
  }
  test "operacao visao invalida" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000, visao: "semana"}
    expect.to_throw { exception = "Visão inválida." }
  }
  test "operacao hoje incompleto" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000, visao: "hoje"}
    expect.to_throw { exception = "Período inválido para Hoje." }
  }
  test "operacao futuro fora de hoje" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1792033200000}
    expect.to_throw { exception = "Período inválido." }
  }
  test "operacao loja invalida" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000, lojas_id: 999999}
    expect.to_throw { exception = "Loja inválida." }
  }
  test "operacao categoria invalida" {
    input = {usuarios_id: 4, t0: 1791946800000, t1: 1791999000000, categorias_servico_id: 999999}
    expect.to_throw { exception = "Categoria inválida." }
  }
  guid = "RqsjE2SOXLrrSjnPPglA3nxj9Ok"
}
