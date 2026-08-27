query "verificar-falhas" verb=GET {
  api_group = "APIS from table telemetria_equipamentos"

  input {
  }

  stack {
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
  
    db.get categorias_servico {
      field_name = "nome"
      field_value = "Totem Offline / Sem Heartbeat"
    } as $categoria_heartbeat
  
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
            db.edit ativos_referencia {
              field_name = "id"
              field_value = $item.id
              data = {status_atual: "offline"}
            } as $ativo_offline
          
            var.update $total_offline {
              value = $total_offline + 1
            }
          
            db.query chamados {
              where = $db.chamados.ativos_referencia_id == $item.id && $db.chamados.categorias_servico_id == $categoria_heartbeat.id && ($db.chamados.status == "Novo" || $db.chamados.status == "Em Atendimento" || $db.chamados.status == "Aguardando Terceiro")
              return = {type: "single"}
            } as $incidente_aberto
          
            conditional {
              if ($incidente_aberto == null) {
                db.add chamados {
                  data = {
                    titulo               : "Totem sem heartbeat"
                    status               : "Novo"
                    prioridade           : "Urgente"
                    ativos_referencia_id : $item.id
                    categorias_servico_id: $categoria_heartbeat.id
                    created_at           : "now"
                  }
                } as $novo_incidente
              
                var.update $incidentes_criados {
                  value = $incidentes_criados + 1
                }
              }
            }
          }
        
          else {
            db.edit ativos_referencia {
              field_name = "id"
              field_value = $item.id
              data = {status_atual: "online"}
            } as $ativo_online
          
            var.update $total_online {
              value = $total_online + 1
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