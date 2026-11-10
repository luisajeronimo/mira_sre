// Encerramento sob comando manual de chamados em Resolvido há 72 horas (DE-1 a DE-5, DE-9).
function "service_desk/encerrar_chamados_resolvidos_elegiveis" {
  input {
    timestamp? agora?
  }

  stack {
    var $agora_efetivo {
      value = now
      mock = {
        "encerra chamado elegivel": 1780300000000
        "chamado fora da vigencia": 1780300000000
        "prazo nao vencido": 1780050000000
        "rejeicao antes da revalidacao": 1780300000000
        "linha do tempo inconsistente": 1780300000000
      }
    }

    conditional {
      if ($input.agora != null && $input.agora > 0) {
        var.update $agora_efetivo {
          value = $input.agora
        }
      }
    }

    // Constante versionada de início de vigência (DE-9 / D3). Fixada na publicação.
    var $inicio_vigencia {
      value = 1794181165000
      mock = {
        "encerra chamado elegivel": 1780000000000
        "chamado fora da vigencia": 1780100000000
        "prazo nao vencido": 1780000000000
        "rejeicao antes da revalidacao": 1780000000000
        "linha do tempo inconsistente": 1780000000000
      }
    }

    var $prazo_72h_ms {
      value = 259200000
    }

    var $avaliados {
      value = 0
    }

    var $encerrados {
      value = 0
    }

    var $fora_vigencia {
      value = 0
    }

    var $prazo_nao_vencido {
      value = 0
    }

    var $nao_calculaveis {
      value = 0
    }

    var $conflitos {
      value = 0
    }

    db.query chamados {
      where = $db.chamados.status == "Resolvido"
      sort = {chamados.id: "asc"}
      return = {type: "list"}
      mock = {
        "encerra chamado elegivel": [
          {id: 101, status: "Resolvido", criado_em: 1780000000000, ultima_atualizacao_em: 1780010000000}
        ]
        "chamado fora da vigencia": [
          {id: 102, status: "Resolvido", criado_em: 1779900000000, ultima_atualizacao_em: 1779950000000}
        ]
        "prazo nao vencido": [
          {id: 103, status: "Resolvido", criado_em: 1780000000000, ultima_atualizacao_em: 1780010000000}
        ]
        "rejeicao antes da revalidacao": [
          {id: 104, status: "Resolvido", criado_em: 1780000000000, ultima_atualizacao_em: 1780010000000}
        ]
        "linha do tempo inconsistente": [
          {id: 105, status: "Resolvido", criado_em: 1780000000000, ultima_atualizacao_em: 1780010000000}
        ]
      }
    } as $candidatos

    foreach ($candidatos) {
      each as $candidato {
        var.update $avaliados {
          value = $avaliados + 1
        }

        db.query interacoes_chamado {
          where = $db.interacoes_chamado.chamados_id == $candidato.id && $db.interacoes_chamado.tipo_evento == "alteracao_chamado"
          sort = {interacoes_chamado.criado_em: "asc", interacoes_chamado.id: "asc"}
          return = {type: "list"}
          mock = {
            "encerra chamado elegivel": [
              {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780005000000}
              {id: 2, alteracoes: {status: {anterior: "Em Atendimento", resultante: "Resolvido"}}, criado_em: 1780010000000}
            ]
            "chamado fora da vigencia": [
              {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Resolvido"}}, criado_em: 1779950000000}
            ]
            "prazo nao vencido": [
              {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Resolvido"}}, criado_em: 1780010000000}
            ]
            "rejeicao antes da revalidacao": [
              {id: 1, alteracoes: {status: {anterior: "Novo", resultante: "Resolvido"}}, criado_em: 1780010000000}
            ]
            "linha do tempo inconsistente": [
              {id: 1, alteracoes: {status: {anterior: "Em Atendimento", resultante: "Resolvido"}}, criado_em: 1780010000000}
            ]
          }
        } as $eventos

        var $estado {
          value = "Novo"
        }

        var $inicio {
          value = $candidato.criado_em
        }

        var $invalido {
          value = false
        }

        var $t_r {
          value = null
        }

        conditional {
          if ($candidato.criado_em == null) {
            var.update $invalido {
              value = true
            }
          }
        }

        foreach ($eventos) {
          each as $ev {
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
              if ($ev.alteracoes|is_object) {
                var.update $par {
                  value = $ev.alteracoes|get:"status":null
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
              value = ($anterior|is_text) && ($resultante|is_text) && $anterior != "" && $resultante != "" && $anterior != $resultante && $ev.criado_em != null
            }

            conditional {
              if (!$valido || $anterior != $estado || $ev.criado_em < $inicio) {
                var.update $invalido {
                  value = true
                }
              }
              else {
                var.update $estado {
                  value = $resultante
                }
                var.update $inicio {
                  value = $ev.criado_em
                }
                conditional {
                  if ($resultante == "Resolvido") {
                    var.update $t_r {
                      value = $ev.criado_em
                    }
                  }
                }
              }
            }
          }
        }

        conditional {
          if ($estado != "Resolvido") {
            var.update $invalido {
              value = true
            }
          }
        }

        conditional {
          if ($invalido || $t_r == null) {
            var.update $nao_calculaveis {
              value = $nao_calculaveis + 1
            }
          }
          elseif ($t_r < $inicio_vigencia) {
            var.update $fora_vigencia {
              value = $fora_vigencia + 1
            }
          }
          elseif ($agora_efetivo < ($t_r + $prazo_72h_ms)) {
            var.update $prazo_nao_vencido {
              value = $prazo_nao_vencido + 1
            }
          }
          else {
            db.transaction {
              stack {
                db.get chamados {
                  field_name = "id"
                  field_value = $candidato.id
                  mock = {
                    "encerra chamado elegivel": {id: 101, status: "Resolvido", ultima_atualizacao_em: 1780010000000}
                    "rejeicao antes da revalidacao": {id: 104, status: "Solução Rejeitada", ultima_atualizacao_em: 1780020000000}
                  }
                } as $revalidado

                conditional {
                  if ($revalidado.status != "Resolvido" || $revalidado.ultima_atualizacao_em != $candidato.ultima_atualizacao_em) {
                    var.update $conflitos {
                      value = $conflitos + 1
                    }
                  }
                  else {
                    db.add interacoes_chamado {
                      data = {
                        mensagem: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução."
                        criado_em: $agora_efetivo
                        visibilidade: "publica"
                        tipo_evento: "comentario"
                        chamados_id: $candidato.id
                        usuarios_id: null
                      }
                      mock = {
                        "encerra chamado elegivel": {id: 301, chamados_id: 101, criado_em: 1780300000000}
                      }
                    } as $comentario_sistema

                    db.patch chamados {
                      field_name = "id"
                      field_value = $candidato.id
                      data = {
                        status: "Encerrado"
                        ultima_atualizacao_em: $agora_efetivo
                      }
                      mock = {
                        "encerra chamado elegivel": {id: 101, status: "Encerrado", ultima_atualizacao_em: 1780300000000}
                      }
                    } as $chamado_encerrado

                    db.add interacoes_chamado {
                      data = {
                        tipo_evento: "alteracao_chamado"
                        alteracoes: {
                          status: {
                            anterior: "Resolvido"
                            resultante: "Encerrado"
                          }
                          comentario_interacao_id: $comentario_sistema.id
                        }
                        criado_em: $agora_efetivo
                        chamados_id: $candidato.id
                        usuarios_id: null
                      }
                      mock = {
                        "encerra chamado elegivel": {id: 302, tipo_evento: "alteracao_chamado", chamados_id: 101}
                      }
                    } as $evento_sistema

                    var.update $encerrados {
                      value = $encerrados + 1
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  response = {
    avaliados: $avaliados
    encerrados: $encerrados
    fora_vigencia: $fora_vigencia
    prazo_nao_vencido: $prazo_nao_vencido
    nao_calculaveis: $nao_calculaveis
    conflitos: $conflitos
  }

  test "encerra chamado elegivel" {
    input = {}
    expect.to_equal ($response.avaliados) { value = 1 }
    expect.to_equal ($response.encerrados) { value = 1 }
    expect.to_equal ($response.fora_vigencia) { value = 0 }
    expect.to_equal ($response.prazo_nao_vencido) { value = 0 }
    expect.to_equal ($response.nao_calculaveis) { value = 0 }
    expect.to_equal ($response.conflitos) { value = 0 }
  }

  test "chamado fora da vigencia" {
    input = {}
    expect.to_equal ($response.avaliados) { value = 1 }
    expect.to_equal ($response.encerrados) { value = 0 }
    expect.to_equal ($response.fora_vigencia) { value = 1 }
  }

  test "prazo nao vencido" {
    input = {}
    expect.to_equal ($response.avaliados) { value = 1 }
    expect.to_equal ($response.encerrados) { value = 0 }
    expect.to_equal ($response.prazo_nao_vencido) { value = 1 }
  }

  test "rejeicao antes da revalidacao" {
    input = {}
    expect.to_equal ($response.avaliados) { value = 1 }
    expect.to_equal ($response.encerrados) { value = 0 }
    expect.to_equal ($response.conflitos) { value = 1 }
  }

  test "linha do tempo inconsistente" {
    input = {}
    expect.to_equal ($response.avaliados) { value = 1 }
    expect.to_equal ($response.encerrados) { value = 0 }
    expect.to_equal ($response.nao_calculaveis) { value = 1 }
  }

  guid = "miraEncerrarResolvidosElegiveis01"
}
