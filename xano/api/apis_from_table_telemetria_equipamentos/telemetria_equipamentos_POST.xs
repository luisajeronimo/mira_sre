// Add telemetria_equipamentos record
query telemetria_equipamentos verb=POST {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    int ativos_referencia_id
    decimal uso_cpu
    decimal uso_memoria
    decimal temperatura
    text status_rede
    timestamp evento_timestamp
  }

  stack {
    db.get ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
    } as $ativo
  
    conditional {
      if ($ativo == null) {
        precondition (false) {
          error_type = "notfound"
          error = "ATIVO_NAO_ENCONTRADO - O ativo informado não existe."
        }
      }
    
      else {
        db.add telemetria_equipamentos {
          enforce_hidden_fields = false
          data = {
            created_at          : "now"
            ativos_referencia_id: $input.ativos_referencia_id
            uso_cpu             : $input.uso_cpu
            uso_memoria         : $input.uso_memoria
            temperatura         : $input.temperatura
            status_rede         : $input.status_rede
            evento_timestamp    : $input.evento_timestamp
          }
        } as $telemetria_equipamentos
      }
    }
  }

  response = {
    success             : true
    message             : "Telemetria registrada com sucesso."
    telemetria_id       : $telemetria_equipamentos.id
    ativos_referencia_id: $telemetria_equipamentos.ativos_referencia_id
    evento_timestamp    : $telemetria_equipamentos.evento_timestamp
  }

  guid = "rv26AQvmgM-PHWCz53dBj3OjUHA"
}