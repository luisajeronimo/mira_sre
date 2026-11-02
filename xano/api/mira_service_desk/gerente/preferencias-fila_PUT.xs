query "gerente/preferencias-fila" verb=PUT {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    int? numero?
    text[] status?
    int[] ativo_ids?
    timestamp? data_inicio?
    timestamp? data_fim?
    timestamp? ultima_atualizacao_inicio?
    timestamp? ultima_atualizacao_fim?
    int[]? loja_ids?=null
    text[]? prioridades?=null
    int[]? responsavel_ids?=null
    bool? incluir_nao_atribuido?
  }
  stack {
    conditional {
      if ($input.loja_ids != null || $input.prioridades != null || $input.responsavel_ids != null || $input.incluir_nao_atribuido != null) {
        util.set_header { value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace" }
        precondition (false) {
          error_type = "inputerror"
          error = "Filtro não permitido."
        }
      }
    }
    function.run "service_desk/salvar_preferencia_filtros_gerente" {
      input = {usuarios_id: $auth.id, numero: $input.numero, status: $input.status, ativo_ids: $input.ativo_ids, data_inicio: $input.data_inicio, data_fim: $input.data_fim, ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio, ultima_atualizacao_fim: $input.ultima_atualizacao_fim}
    } as $resultado
  }
  response = $resultado
  guid = "miraPrefGerenteApiPut01"
}
