// Série temporal de saúde dos equipamentos.
table telemetria_equipamentos {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int ativos_referencia_id {
      table = "ativos_referencia"
    }
  
    decimal uso_cpu
    decimal uso_memoria
    decimal temperatura
    text status_rede filters=trim
    timestamp? evento_timestamp
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "rRAPdw4KFBXypTJgG3TcDfj8QjQ"
}