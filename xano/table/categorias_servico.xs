// Classificação e parâmetro SLA
table categorias_servico {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text tipo_itil? filters=trim
    text sla_horas? filters=trim
    text desc? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "SlpRM3zb744b2w0KqDyVj7bamLI"
}