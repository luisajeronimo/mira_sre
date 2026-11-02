query "tecnico/preferencias-fila" verb=PUT {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    text escopo filters=trim
    int? numero?
    text[] status?
    int[] ativo_ids?
    timestamp? data_inicio?
    timestamp? data_fim?
    timestamp? ultima_atualizacao_inicio?
    timestamp? ultima_atualizacao_fim?
    int[] loja_ids?
    text[] prioridades?
    int[] responsavel_ids?
    bool incluir_nao_atribuido?
    text ordenar_por filters=trim
    text direcao filters=trim
  }
  stack {
    function.run "service_desk/salvar_preferencia_fila_tecnica" {
      input = {usuarios_id: $auth.id, escopo: $input.escopo, numero: $input.numero, status: $input.status, ativo_ids: $input.ativo_ids, data_inicio: $input.data_inicio, data_fim: $input.data_fim, ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio, ultima_atualizacao_fim: $input.ultima_atualizacao_fim, loja_ids: $input.loja_ids, prioridades: $input.prioridades, responsavel_ids: $input.responsavel_ids, incluir_nao_atribuido: $input.incluir_nao_atribuido, ordenar_por: $input.ordenar_por, direcao: $input.direcao}
    } as $resultado
  }
  response = $resultado
  guid = "miraPrefFilaPut01"
}
