// Work logs e comunicação
table interacoes_chamado {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text mensagem? filters=trim
    timestamp? criado_em?
    int chamados_id? {
      table = "chamados"
    }
  
    int usuarios_id? {
      table = "usuarios"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "XjRNC6p0BpmH7vWnIQiqZpwFLTE"
}