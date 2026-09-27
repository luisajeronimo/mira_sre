// Registro de incidentes/requisições
table chamados {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text titulo? filters=trim
    text? descricao? filters=trim
    text status? filters=trim
    text prioridade? filters=trim
    enum? origem? {
      values = ["manual", "automatico"]
    }

    timestamp? criado_em?
    decimal? sla_horas_aplicado?
    int solicitante_id? {
      table = "usuarios"
    }
  
    int tecnico_id? {
      table = "usuarios"
    }
  
    int categorias_servico_id? {
      table = "categorias_servico"
    }
  
    int ativos_referencia_id? {
      table = "ativos_referencia"
    }

    timestamp atribuido_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "j6MWyWUtfPRPV_ZNZbjrmXlOoZc"
}
