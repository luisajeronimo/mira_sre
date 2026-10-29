// Substitui integralmente a preferência local depois da consulta candidata.
function "service_desk/salvar_preferencia_filtros_gerente" {
  input {
    int usuarios_id { table = "usuarios" }
    int? numero?
    text? status? filters=trim
    int? ativo_id? { table = "ativos_referencia" }
    timestamp? data_inicio?
    timestamp? data_fim?
    timestamp? ultima_atualizacao_inicio?
    timestamp? ultima_atualizacao_fim?
  }
  stack {
    function.run "autorizacao/exigir_perfil" { input = {usuarios_id: $input.usuarios_id, gerente: true} } as $usuario
    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    var $status_valido { value = $input.status == null || $input.status == "" || $input.status == "Novo" || $input.status == "Em Atendimento" || $input.status == "Aguardando Solicitante" || $input.status == "Aguardando Mudança" || $input.status == "Resolvido" || $input.status == "Solução Rejeitada" || $input.status == "Encerrado" || $input.status == "Cancelado" }
    precondition (($input.numero == null || $input.numero > 0) && $status_valido && ($input.data_inicio == null || $input.data_fim == null || $input.data_inicio < $input.data_fim) && ($input.ultima_atualizacao_inicio == null || $input.ultima_atualizacao_fim == null || $input.ultima_atualizacao_inicio < $input.ultima_atualizacao_fim)) {
      error_type = "inputerror"
      error = "Preferência inválida."
    }
    conditional {
      if ($input.ativo_id != null) {
        db.get ativos_referencia {
          field_name = "id"
          field_value = $input.ativo_id
        } as $ativo
        precondition ($ativo != null && $ativo.lojas_id == $usuario.lojas_id) {
          error_type = "accessdenied"
          error = "Acesso não autorizado."
        }
      }
    }
    var $chave_logica { value = ($usuario.id|to_text) ~ ":todos" }
    db.add_or_edit preferencias_fila_chamados {
      field_name = "chave_logica"
      field_value = $chave_logica
      data = {usuarios_id: $usuario.id, escopo: "todos", chave_logica: $chave_logica, numero: $input.numero, status: $input.status, ativos_referencia_id: $input.ativo_id, data_inicio: $input.data_inicio, data_fim: $input.data_fim, ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio, ultima_atualizacao_fim: $input.ultima_atualizacao_fim, atualizado_em: now}
    } as $salva
    var $preferencia { value = {numero: $salva.numero, status: $salva.status, ativo_id: $salva.ativos_referencia_id, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, ultima_atualizacao_inicio: $salva.ultima_atualizacao_inicio, ultima_atualizacao_fim: $salva.ultima_atualizacao_fim} }
  }
  response = {preferencia: $preferencia}
  guid = "miraPrefGerentePut01"
}
