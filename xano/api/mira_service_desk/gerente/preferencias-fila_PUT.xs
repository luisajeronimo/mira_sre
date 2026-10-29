query "gerente/preferencias-fila" verb=PUT {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    int? numero?
    text? status? filters=trim
    int? ativo_id? {
      table = "ativos_referencia"
    }
    timestamp? data_inicio?
    timestamp? data_fim?
    timestamp? ultima_atualizacao_inicio?
    timestamp? ultima_atualizacao_fim?
  }
  stack {
    function.run "service_desk/salvar_preferencia_filtros_gerente" {
      input = {usuarios_id: $auth.id, numero: $input.numero, status: $input.status, ativo_id: $input.ativo_id, data_inicio: $input.data_inicio, data_fim: $input.data_fim, ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio, ultima_atualizacao_fim: $input.ultima_atualizacao_fim}
    } as $resultado
  }
  response = $resultado
  guid = "miraPrefGerenteApiPut01"
}
