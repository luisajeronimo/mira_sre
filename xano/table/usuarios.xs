// Identidade e autorização básica
table usuarios {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    email email? filters=trim|lower
    enum role? {
      values = [
        "gerente"
        "tecnico"
        "diretoria"
      ]
    }

    password? senha? {
      sensitive = true
    }

    int? lojas_id? {
      table = "lojas"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "hNNLPxZsON5_QbwxKPRhMeuR1og"
}
