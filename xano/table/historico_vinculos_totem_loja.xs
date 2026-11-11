// Vínculos comprovados por instante; não reconstitui o passado de Totens legados.
table historico_vinculos_totem_loja {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int ativos_referencia_id {
      table = "ativos_referencia"
    }

    int? loja_origem_id? {
      table = "lojas"
    }

    int loja_destino_id {
      table = "lojas"
    }

    enum tipo {
      values = ["criacao", "marco", "transferencia"]
    }

    timestamp efetivado_em
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "ativos_referencia_id"}, {name: "efetivado_em"}]
    }
    {type: "btree", field: [{name: "loja_destino_id"}]}
    {type: "btree", field: [{name: "loja_origem_id"}]}
  ]

  guid = "miraHistoricoVinculoTotemLoja01"
}