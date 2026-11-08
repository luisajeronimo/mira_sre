// Consumo de SLA em tempo corrido (DS-1), somente leitura, conforme o design
// D1–D2 de `sla-resolucao-encerramento`: linha do tempo iniciada em `Novo` na
// criação e seguida das transições válidas de `alteracao_chamado` (critério H-1).
// Função interna sem endpoint: onde o consumo é exposto depende da decisão DE-8.
// Nenhum valor é persistido, estimado ou completado.
function "service_desk/calcular_consumo_sla_chamado" {
  input {
    int chamados_id
    int? instante_referencia?
  }

  stack {
    db.query chamados {
      where = $db.chamados.id == $input.chamados_id
      return = {type: "single"}
      mock = {
        "exemplo do design com rejeicao": {id: 101, status: "Resolvido", criado_em: 1780000000000, sla_horas_aplicado: 4}
        "conta sem pausas": {id: 102, status: "Em Atendimento", criado_em: 1780000000000, sla_horas_aplicado: 8}
        "multiplas pausas": {id: 103, status: "Solução Rejeitada", criado_em: 1780000000000, sla_horas_aplicado: 4}
        "espera conta": {id: 104, status: "Aguardando Solicitante", criado_em: 1780000000000, sla_horas_aplicado: 10}
        "encerrado nao aumenta": {id: 105, status: "Encerrado", criado_em: 1780000000000, sla_horas_aplicado: 2}
        "cancelado nao aumenta": {id: 106, status: "Cancelado", criado_em: 1780000000000, sla_horas_aplicado: 2}
        "status atual nao reconstruido": {id: 107, status: "Em Atendimento", criado_em: 1780000000000, sla_horas_aplicado: 4}
        "transicao desencadeada": {id: 108, status: "Encerrado", criado_em: 1780000000000, sla_horas_aplicado: 4}
        "status fora da lista": {id: 109, status: "Aguardando Terceiro", criado_em: 1780000000000, sla_horas_aplicado: 4}
        "limite de 70": {id: 110, status: "Novo", criado_em: 1780000000000, sla_horas_aplicado: 10}
        "limite de 90": {id: 110, status: "Novo", criado_em: 1780000000000, sla_horas_aplicado: 10}
        "limite de 100": {id: 110, status: "Novo", criado_em: 1780000000000, sla_horas_aplicado: 10}
        "acima de 100": {id: 110, status: "Novo", criado_em: 1780000000000, sla_horas_aplicado: 10}
        "sem sla aplicado": {id: 111, status: "Novo", criado_em: 1780000000000, sla_horas_aplicado: null}
        "sem criado em": {id: 112, status: "Novo", criado_em: null, sla_horas_aplicado: 4}
        "transicao anterior a abertura": {id: 113, status: "Em Atendimento", criado_em: 1780000000000, sla_horas_aplicado: 4}
        "chamado inexistente": null
      }
    } as $chamado

    precondition ($chamado != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    var $t {
      value = $input.instante_referencia
    }

    conditional {
      if ($t == null) {
        var.update $t {
          value = "now"|to_ms
        }
      }
    }

    db.query interacoes_chamado {
      where = $db.interacoes_chamado.chamados_id == $input.chamados_id && $db.interacoes_chamado.tipo_evento == "alteracao_chamado"
      sort = {interacoes_chamado.criado_em: "asc", interacoes_chamado.id: "asc"}
      return = {type: "list"}
      mock = {
        "exemplo do design com rejeicao": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780001800000}
          {id: 2, alteracoes: {status: {anterior: "Em Atendimento", resultante: "Resolvido"}}, criado_em: 1780007200000}
          {id: 3, alteracoes: {prioridade: {anterior: "Média", resultante: "Alta"}}, criado_em: 1780010000000}
          {id: 4, alteracoes: {status: {anterior: "Resolvido", resultante: "Solução Rejeitada"}}, criado_em: 1780018000000}
          {id: 5, alteracoes: {status: {anterior: "Solução Rejeitada", resultante: "Em Atendimento"}}, criado_em: 1780021600000}
          {id: 6, alteracoes: {status: {anterior: "Em Atendimento", resultante: "Resolvido"}}, criado_em: 1780025200000}
        ]
        "conta sem pausas": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780003600000}
        ]
        "multiplas pausas": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Resolvido"}}, criado_em: 1780003600000}
          {id: 2, alteracoes: {status: {anterior: "Resolvido", resultante: "Solução Rejeitada"}}, criado_em: 1780010800000}
          {id: 3, alteracoes: {status: {anterior: "Solução Rejeitada", resultante: "Resolvido"}}, criado_em: 1780014400000}
          {id: 4, alteracoes: {status: {anterior: "Resolvido", resultante: "Solução Rejeitada"}}, criado_em: 1780021600000}
        ]
        "espera conta": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Aguardando Solicitante"}}, criado_em: 1780003600000}
        ]
        "encerrado nao aumenta": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780003600000}
          {id: 2, alteracoes: {status: {anterior: "Em Atendimento", resultante: "Encerrado"}}, criado_em: 1780007200000}
        ]
        "cancelado nao aumenta": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Cancelado"}}, criado_em: 1780001800000}
        ]
        "status atual nao reconstruido": []
        "transicao desencadeada": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780003600000}
          {id: 2, alteracoes: {status: {anterior: "Resolvido", resultante: "Encerrado"}}, criado_em: 1780007200000}
        ]
        "status fora da lista": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Aguardando Terceiro"}}, criado_em: 1780003600000}
        ]
        "limite de 70": []
        "limite de 90": []
        "limite de 100": []
        "acima de 100": []
        "sem sla aplicado": []
        "sem criado em": []
        "transicao anterior a abertura": [
          {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1779999000000}
        ]
      }
    } as $eventos

    var $estado {
      value = "Novo"
    }

    var $inicio {
      value = $chamado.criado_em
    }

    var $consumo {
      value = 0
    }

    var $motivo {
      value = null
    }

    conditional {
      if ($chamado.criado_em == null) {
        var.update $motivo {
          value = "sem_criado_em"
        }
      }
    }

    foreach ($eventos) {
      each as $evento {
        var $par {
          value = null
        }

        var $anterior {
          value = null
        }

        var $resultante {
          value = null
        }

        conditional {
          if ($evento.alteracoes|is_object) {
            var.update $par {
              value = $evento.alteracoes|get:"status":null
            }
          }
        }

        conditional {
          if ($par|is_object) {
            var.update $anterior {
              value = $par|get:"anterior":null
            }

            var.update $resultante {
              value = $par|get:"resultante":null
            }
          }
        }

        var $valido {
          value = ($anterior|is_text) && ($resultante|is_text) && $anterior != "" && $resultante != "" && $anterior != $resultante && $evento.criado_em != null
        }

        var $canonico {
          value = $resultante == "Novo" || $resultante == "Em Atendimento" || $resultante == "Aguardando Solicitante" || $resultante == "Aguardando Mudança" || $resultante == "Resolvido" || $resultante == "Solução Rejeitada" || $resultante == "Encerrado" || $resultante == "Cancelado"
        }

        conditional {
          if ($motivo == null && $valido && $anterior != $estado) {
            var.update $motivo {
              value = "transicao_desencadeada"
            }
          }
        }

        conditional {
          if ($motivo == null && $valido && !$canonico) {
            var.update $motivo {
              value = "status_fora_da_lista"
            }
          }
        }

        conditional {
          if ($motivo == null && $valido && $evento.criado_em < $inicio) {
            var.update $motivo {
              value = "ordem_temporal_inconsistente"
            }
          }
        }

        conditional {
          if ($motivo == null && $valido) {
            conditional {
              if ($estado == "Novo" || $estado == "Em Atendimento" || $estado == "Aguardando Solicitante" || $estado == "Aguardando Mudança" || $estado == "Solução Rejeitada") {
                // Segmento [inicio, min(fim, t)); duração negativa não é somada.
                var $fim_segmento {
                  value = $evento.criado_em
                }

                conditional {
                  if ($t < $fim_segmento) {
                    var.update $fim_segmento {
                      value = $t
                    }
                  }
                }

                var $duracao {
                  value = $fim_segmento - $inicio
                }

                conditional {
                  if ($duracao > 0) {
                    var.update $consumo {
                      value = $consumo + $duracao
                    }
                  }
                }
              }
            }

            var.update $estado {
              value = $resultante
            }

            var.update $inicio {
              value = $evento.criado_em
            }
          }
        }
      }
    }

    conditional {
      if ($motivo == null && $estado != $chamado.status) {
        var.update $motivo {
          value = "status_atual_divergente"
        }
      }
    }

    var $em_contagem {
      value = $estado == "Novo" || $estado == "Em Atendimento" || $estado == "Aguardando Solicitante" || $estado == "Aguardando Mudança" || $estado == "Solução Rejeitada"
    }

    conditional {
      if ($motivo == null && $em_contagem) {
        var $duracao_final {
          value = $t - $inicio
        }

        conditional {
          if ($duracao_final > 0) {
            var.update $consumo {
              value = $consumo + $duracao_final
            }
          }
        }
      }
    }

    conditional {
      if ($motivo == null && ($chamado.sla_horas_aplicado == null || $chamado.sla_horas_aplicado <= 0)) {
        var.update $motivo {
          value = "sem_sla_aplicado"
        }
      }
    }

    var $resultado {
      value = {
        chamados_id: $chamado.id
        calculavel: false
        motivo: $motivo
        consumo_ms: null
        sla_horas_aplicado: $chamado.sla_horas_aplicado
        fracao_consumida: null
        faixa: null
        estado_contagem: null
        calculado_em: $t
      }
    }

    conditional {
      if ($motivo == null) {
        var $sla_ms {
          value = $chamado.sla_horas_aplicado * 3600000
        }

        // Faixas do domínio §12, comparadas em inteiros para evitar arredondamento:
        // < 70% normal; 70%–90% risco; > 90% até 100% crítico; > 100% violado.
        var $faixa {
          value = "violado"
        }

        conditional {
          if ($consumo * 10 < $sla_ms * 7) {
            var.update $faixa {
              value = "normal"
            }
          }

          elseif ($consumo * 10 <= $sla_ms * 9) {
            var.update $faixa {
              value = "risco"
            }
          }

          elseif ($consumo <= $sla_ms) {
            var.update $faixa {
              value = "critico"
            }
          }
        }

        var $estado_contagem {
          value = "encerrada"
        }

        conditional {
          if ($em_contagem) {
            var.update $estado_contagem {
              value = "em_contagem"
            }
          }

          elseif ($estado == "Resolvido") {
            var.update $estado_contagem {
              value = "pausada"
            }
          }
        }

        var.update $resultado {
          value = {
            chamados_id: $chamado.id
            calculavel: true
            motivo: null
            consumo_ms: $consumo
            sla_horas_aplicado: $chamado.sla_horas_aplicado
            fracao_consumida: $consumo / $sla_ms
            faixa: $faixa
            estado_contagem: $estado_contagem
            calculado_em: $t
          }
        }
      }
    }
  }

  response = $resultado

  test "exemplo do design com rejeicao" {
    input = {chamados_id: 101, instante_referencia: 1780028800000}

    expect.to_equal ($response.consumo_ms) {
      value = 14400000
    }

    expect.to_equal ($response.faixa) {
      value = "critico"
    }

    expect.to_equal ($response.estado_contagem) {
      value = "pausada"
    }
  }

  test "conta sem pausas" {
    input = {chamados_id: 102, instante_referencia: 1780018000000}

    expect.to_equal ($response.consumo_ms) {
      value = 18000000
    }

    expect.to_equal ($response.faixa) {
      value = "normal"
    }

    expect.to_equal ($response.estado_contagem) {
      value = "em_contagem"
    }
  }

  test "multiplas pausas" {
    input = {chamados_id: 103, instante_referencia: 1780025200000}

    expect.to_equal ($response.consumo_ms) {
      value = 10800000
    }

    expect.to_equal ($response.faixa) {
      value = "risco"
    }
  }

  test "espera conta" {
    input = {chamados_id: 104, instante_referencia: 1780010800000}

    expect.to_equal ($response.consumo_ms) {
      value = 10800000
    }
  }

  test "encerrado nao aumenta" {
    input = {chamados_id: 105, instante_referencia: 1780360000000}

    expect.to_equal ($response.consumo_ms) {
      value = 7200000
    }

    expect.to_equal ($response.faixa) {
      value = "critico"
    }

    expect.to_equal ($response.estado_contagem) {
      value = "encerrada"
    }
  }

  test "cancelado nao aumenta" {
    input = {chamados_id: 106, instante_referencia: 1780360000000}

    expect.to_equal ($response.consumo_ms) {
      value = 1800000
    }
  }

  test "status atual nao reconstruido" {
    input = {chamados_id: 107, instante_referencia: 1780010800000}

    expect.to_be_false ($response.calculavel)

    expect.to_equal ($response.motivo) {
      value = "status_atual_divergente"
    }

    expect.to_be_null ($response.consumo_ms)
  }

  test "transicao desencadeada" {
    input = {chamados_id: 108, instante_referencia: 1780010800000}

    expect.to_equal ($response.motivo) {
      value = "transicao_desencadeada"
    }

    expect.to_be_null ($response.consumo_ms)
  }

  test "status fora da lista" {
    input = {chamados_id: 109, instante_referencia: 1780010800000}

    expect.to_equal ($response.motivo) {
      value = "status_fora_da_lista"
    }
  }

  test "limite de 70" {
    input = {chamados_id: 110, instante_referencia: 1780025200000}

    expect.to_equal ($response.faixa) {
      value = "risco"
    }
  }

  test "limite de 90" {
    input = {chamados_id: 110, instante_referencia: 1780032400000}

    expect.to_equal ($response.faixa) {
      value = "risco"
    }
  }

  test "limite de 100" {
    input = {chamados_id: 110, instante_referencia: 1780036000000}

    expect.to_equal ($response.faixa) {
      value = "critico"
    }
  }

  test "acima de 100" {
    input = {chamados_id: 110, instante_referencia: 1780036000001}

    expect.to_equal ($response.faixa) {
      value = "violado"
    }
  }

  test "sem sla aplicado" {
    input = {chamados_id: 111, instante_referencia: 1780010800000}

    expect.to_equal ($response.motivo) {
      value = "sem_sla_aplicado"
    }
  }

  test "sem criado em" {
    input = {chamados_id: 112, instante_referencia: 1780010800000}

    expect.to_equal ($response.motivo) {
      value = "sem_criado_em"
    }
  }

  test "transicao anterior a abertura" {
    input = {chamados_id: 113, instante_referencia: 1780010800000}

    expect.to_equal ($response.motivo) {
      value = "ordem_temporal_inconsistente"
    }
  }

  test "chamado inexistente" {
    input = {chamados_id: 999, instante_referencia: 1780010800000}

    expect.to_throw {
      exception = ""
    }
  }

  guid = "miraConsumoSlaChamado01"
}
