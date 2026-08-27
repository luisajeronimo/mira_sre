// Identidade e autorização básica
table usuarios {
  auth = false

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
        "diretor"
        "tecnico_n1"
        "tecnico_n2"
        "tecnico_n3"
        "admin"
      ]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "hNNLPxZsON5_QbwxKPRhMeuR1og"
}