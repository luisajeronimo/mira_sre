// Preferência exclusiva dos cinco filtros básicos do Gerente autenticado.
function "service_desk/obter_preferencia_filtros_gerente" {
  input { int usuarios_id { table = "usuarios" } }
  stack {
    function.run "autorizacao/exigir_perfil" { input = {usuarios_id: $input.usuarios_id, gerente: true} } as $usuario
    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    db.query preferencias_fila_chamados {
      where = $db.preferencias_fila_chamados.usuarios_id == $usuario.id && $db.preferencias_fila_chamados.escopo == "todos"
      return = {type: "single"}
    } as $salva
    var $preferencia { value = $salva != null ? {numero: $salva.numero, status: $salva.status, ativo_id: $salva.ativos_referencia_id, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, ultima_atualizacao_inicio: $salva.ultima_atualizacao_inicio, ultima_atualizacao_fim: $salva.ultima_atualizacao_fim} : {numero: null, status: null, ativo_id: null, data_inicio: null, data_fim: null, ultima_atualizacao_inicio: null, ultima_atualizacao_fim: null} }
  }
  response = {preferencia: $preferencia}
  guid = "miraPrefGerenteGet01"
}
