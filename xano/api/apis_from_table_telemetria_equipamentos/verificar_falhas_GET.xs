query "verificar-falhas" verb=GET {
  api_group = "APIS from table telemetria_equipamentos"

  input {
  }

  stack {
    var $chave_fiscal_recebida {
      value = $env.$http_headers|get:"X-Mira-Fiscal-Key"
    }

    var $chave_fiscal_configurada {
      value = $env.MIRA_FISCAL_AUTOMATION_KEY
    }

    conditional {
      if (!($chave_fiscal_configurada != null && $chave_fiscal_configurada != "" && $chave_fiscal_recebida != null && $chave_fiscal_recebida != "" && $chave_fiscal_recebida === $chave_fiscal_configurada)) {
        util.set_header {
          value = "HTTP/1.1 401 Unauthorized\nContent-Type: application/json"
          duplicates = "replace"
        }

        return {
          value = {error: "Não autenticado."}
        }
      }
    }

    var $limite_heartbeat {
      value = "now"|add_secs_to_timestamp:-900
    }
  
    var $total_online {
      value = 0
    }
  
    var $total_offline {
      value = 0
    }
  
    var $total_sem_telemetria {
      value = 0
    }
  
    var $incidentes_criados {
      value = 0
    }
  
    db.query ativos_referencia {
      return = {type: "list"}
    } as $ativos
  
    foreach ($ativos) {
      each as $item {
        db.query telemetria_equipamentos {
          where = $db.telemetria_equipamentos.ativos_referencia_id == $item.id
          sort = {telemetria_equipamentos.evento_timestamp: "desc"}
          return = {type: "single"}
        } as $ultima_telemetria
      
        conditional {
          if ($ultima_telemetria == null) {
            var.update $total_sem_telemetria {
              value = $total_sem_telemetria + 1
            }
          }
        
        elseif ($ultima_telemetria.evento_timestamp < $limite_heartbeat) {
          conditional {
            if ($item.status_atual == "offline") {
              var.update $total_offline {
                value = $total_offline + 1
              }
            }

            elseif ($item.status_atual == "online") {
              // A categoria é validada antes de iniciar as escritas da
              // transição. Não há fallback de SLA ou de categoria.
              db.get categorias_servico {
                field_name = "nome"
                field_value = "Totem Offline / Sem Heartbeat"
              } as $categoria_heartbeat

              conditional {
                if ($categoria_heartbeat == null || $categoria_heartbeat.tipo_itil != "Incidente" || $categoria_heartbeat.sla_horas == null || $categoria_heartbeat.permite_abertura_manual != false) {
                  throw {
                    name = "HeartbeatCategoryError"
                    value = "Categoria de heartbeat indisponível ou incompatível."
                  }
                }
              }

              db.transaction {
                stack {
                  // Revalida os fatos que fundamentam a transição antes de
                  // qualquer escrita dependente na unidade atômica.
                  db.get ativos_referencia {
                    field_name = "id"
                    field_value = $item.id
                  } as $ativo_atual

                  db.get categorias_servico {
                    field_name = "nome"
                    field_value = "Totem Offline / Sem Heartbeat"
                  } as $categoria_heartbeat_revalidada

                  db.query telemetria_equipamentos {
                    where = $db.telemetria_equipamentos.ativos_referencia_id == $item.id
                    sort = {telemetria_equipamentos.evento_timestamp: "desc"}
                    return = {type: "single"}
                  } as $telemetria_revalidada

                  conditional {
                    if ($ativo_atual.status_atual == "online" && $telemetria_revalidada != null && $telemetria_revalidada.evento_timestamp < $limite_heartbeat && $categoria_heartbeat_revalidada != null && $categoria_heartbeat_revalidada.tipo_itil == "Incidente" && $categoria_heartbeat_revalidada.sla_horas != null && $categoria_heartbeat_revalidada.permite_abertura_manual == false) {
                      db.query chamados {
                        where = $db.chamados.ativos_referencia_id == $item.id && $db.chamados.categorias_servico_id == $categoria_heartbeat_revalidada.id && ($db.chamados.status == "Novo" || $db.chamados.status == "Em Atendimento" || $db.chamados.status == "Aguardando Solicitante" || $db.chamados.status == "Aguardando Mudança" || $db.chamados.status == "Resolvido" || $db.chamados.status == "Solução Rejeitada")
                        return = {type: "single"}
                      } as $incidente_equivalente

                      db.add historico_disponibilidade_totens {
                        data = {
                          ativos_referencia_id      : $item.id
                          telemetria_referencia_id  : $telemetria_revalidada.id
                          status                     : "offline"
                          detectado_em               : "now"
                          heartbeat_limite_minutos   : 15
                          created_at                 : "now"
                        }
                      } as $evento_offline

                      db.edit ativos_referencia {
                        field_name = "id"
                        field_value = $item.id
                        data = {status_atual: "offline"}
                      } as $ativo_offline

                      conditional {
                        if ($incidente_equivalente == null) {
                          var $criado_em {
                            value = now
                          }

                          db.add chamados {
                            data = {
                              titulo               : "Totem sem heartbeat"
                              status               : "Novo"
                              prioridade           : "Urgente"
                              origem               : "automatico"
                              criador_sistema      : "bot_fiscalizacao"
                              criado_em            : $criado_em
                              ultima_atualizacao_em: $criado_em
                              sla_horas_aplicado   : $categoria_heartbeat_revalidada.sla_horas
                              ativos_referencia_id : $item.id
                              categorias_servico_id: $categoria_heartbeat_revalidada.id
                              created_at           : "now"
                            }
                          } as $novo_incidente

                          var.update $incidentes_criados {
                            value = $incidentes_criados + 1
                          }
                        }
                      }
                    }
                  }
                }
              }

              var.update $total_offline {
                value = $total_offline + 1
              }
            }
          }
        }

        else {
          conditional {
            if ($item.status_atual == "online") {
              var.update $total_online {
                value = $total_online + 1
              }
            }

            elseif ($item.status_atual == "offline") {
              db.transaction {
                stack {
                  db.get ativos_referencia {
                    field_name = "id"
                    field_value = $item.id
                  } as $ativo_atual

                  db.query telemetria_equipamentos {
                    where = $db.telemetria_equipamentos.ativos_referencia_id == $item.id
                    sort = {telemetria_equipamentos.evento_timestamp: "desc"}
                    return = {type: "single"}
                  } as $telemetria_revalidada

                  conditional {
                    if ($ativo_atual.status_atual == "offline" && $telemetria_revalidada != null && $telemetria_revalidada.evento_timestamp >= $limite_heartbeat) {
                      db.add historico_disponibilidade_totens {
                        data = {
                          ativos_referencia_id      : $item.id
                          telemetria_referencia_id  : $telemetria_revalidada.id
                          status                     : "online"
                          detectado_em               : "now"
                          heartbeat_limite_minutos   : 15
                          created_at                 : "now"
                        }
                      } as $evento_online

                      db.edit ativos_referencia {
                        field_name = "id"
                        field_value = $item.id
                        data = {status_atual: "online"}
                      } as $ativo_online
                    }
                  }
                }
              }

              var.update $total_online {
                value = $total_online + 1
              }
            }
          }
        }
        }
      }
    }
  }

  response = {
    success           : true
    message           : "Verificação de heartbeat concluída."
    heartbeat_minutos : 15
    total_ativos      : $ativos|count
    online            : $total_online
    offline           : $total_offline
    sem_telemetria    : $total_sem_telemetria
    incidentes_criados: $incidentes_criados
  }

  guid = "U33I__ejEljqO945VD7PyFI7Ypc"
}
