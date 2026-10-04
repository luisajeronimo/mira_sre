// Transições de disponibilidade materializadas pelo Xano para cada Totem.
table historico_disponibilidade_totens {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int ativos_referencia_id {
      table = "ativos_referencia"
    }

    int telemetria_referencia_id {
      table = "telemetria_equipamentos"
    }

    enum status {
      values = ["online", "offline"]
    }

    timestamp detectado_em
    int heartbeat_limite_minutos
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
  guid = "IifgLPvO-xj14vQ0S8RuLWm_DkY"
}
