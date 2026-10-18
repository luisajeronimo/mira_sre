query "tecnico/preferencias-fila" verb=PUT {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    text escopo filters=trim
    int? numero?
    text? status? filters=trim
    int? ativo_id? {
      table = "ativos_referencia"
    }
    timestamp? data_inicio?
    timestamp? data_fim?
    text? prioridade? filters=trim
    int? responsavel_id? { table = "usuarios" }
    bool somente_nao_atribuido?
    text ordenar_por filters=trim
    text direcao filters=trim
  }
  stack {
    function.run "service_desk/salvar_preferencia_fila_tecnica" {
      input = {usuarios_id: $auth.id, escopo: $input.escopo, numero: $input.numero, status: $input.status, ativo_id: $input.ativo_id, data_inicio: $input.data_inicio, data_fim: $input.data_fim, prioridade: $input.prioridade, responsavel_id: $input.responsavel_id, somente_nao_atribuido: $input.somente_nao_atribuido, ordenar_por: $input.ordenar_por, direcao: $input.direcao}
    } as $resultado
  }
  response = $resultado
  guid = "miraPrefFilaPut01"
}
