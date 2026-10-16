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
    enum? tipo_evento? {
      values = ["comentario", "atribuicao", "reatribuicao", "liberacao", "alteracao_chamado"]
    }
    // Auditoria estruturada e aditiva do Save operacional. Para
    // `alteracao_chamado`, contém somente pares anterior/resultante dos
    // campos efetivamente modificados. Interações históricas permanecem
    // com este campo nulo, sem backfill.
    json? alteracoes?
    enum? visibilidade? {
      values = ["publica", "interna"]
    }
    int chamados_id? {
      table = "chamados"
    }

    int? tecnico_anterior_id? {
      table = "usuarios"
    }

    int? tecnico_novo_id? {
      table = "usuarios"
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
