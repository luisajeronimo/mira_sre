// Query all telemetria_equipamentos records
query telemetria_equipamentos verb=GET {
  api_group = "APIS from table telemetria_equipamentos"

  input {
    int ativos_referencia_id {
      table = "ativos_referencia"
    }
  
    timestamp? data_inicio?
    timestamp? data_fim?
    int limit?=100
  }

  stack {
    db.query telemetria_equipamentos {
      sort = {telemetria_equipamentos.evento_timestamp: "desc"}
      return = {type: "list"}
      output = [
        "id"
        "ativos_referencia_id"
        "uso_cpu"
        "uso_memoria"
        "temperatura"
        "status_rede"
        "evento_timestamp"
      ]
    } as $telemetria_equipamentos
  }

  response = $telemetria_equipamentos
  guid = "l_HQnw0mBrkXpVcEX8G3PUK8JNo"
}