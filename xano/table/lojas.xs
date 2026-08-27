// Cadastro das unidades da rede e sua localização operacional
table lojas {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text endereco? filters=trim
    text regiao? filters=trim
    text status? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "6TAUDS__HCKDZT58sz5oanh0n_I"
}