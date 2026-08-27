// Inventário de equipamentos.
table ativos_referencia {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome_ativo? filters=trim
    text tipo? filters=trim
    text status_atual? filters=trim
    int lojas_id? {
      table = "lojas"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "lk-vNYejgP1rhN-OGPRYjIQBXWo"
}