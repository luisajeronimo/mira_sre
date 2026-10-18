// Preferência durável, isolada por usuário autenticado e escopo da fila.
table preferencias_fila_chamados {
  auth = false

  schema {
    int id
    timestamp created_at?=now { visibility = "private" }
    int usuarios_id { table = "usuarios" }
    enum escopo { values = ["todos", "atribuidos_a_mim"] }
    // Chave interna do upsert: construída exclusivamente a partir do usuário
    // autenticado e do escopo já autorizado.
    text chave_logica { visibility = "private" }
    int? numero?
    text? status? filters=trim
    int? ativos_referencia_id? { table = "ativos_referencia" }
    timestamp? data_inicio?
    timestamp? data_fim?
    text? prioridade? filters=trim
    int? responsavel_id? { table = "usuarios" }
    bool somente_nao_atribuido?=false
    text ordenar_por?="numero" filters=trim
    text direcao?="DESC" filters=trim
    timestamp atualizado_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "usuarios_id"}, {name: "escopo"}]}
    {type: "btree|unique", field: [{name: "chave_logica"}]}
  ]

  guid = "miraPreferenciasFila01"
}
