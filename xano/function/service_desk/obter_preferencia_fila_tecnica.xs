function "service_desk/obter_preferencia_fila_tecnica" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    text escopo filters=trim
  }
  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
    } as $usuario
    var $escopo_enumerado { value = $input.escopo == "todos" || $input.escopo == "atribuidos_a_mim" }
    precondition ($escopo_enumerado) {
      error_type = "inputerror"
      error = "Escopo inválido."
    }
    precondition ($input.escopo != "atribuidos_a_mim" || $usuario.role == "tecnico") {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    db.query preferencias_fila_chamados {
      where = $db.preferencias_fila_chamados.usuarios_id == $usuario.id && $db.preferencias_fila_chamados.escopo == $input.escopo
      return = {type: "single"}
    } as $salva
    var $preferencia { value = $salva != null ? {escopo: $salva.escopo, numero: $salva.numero, status: $salva.status, ativo_id: $salva.ativos_referencia_id, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, prioridade: $salva.prioridade, responsavel_id: $salva.responsavel_id, somente_nao_atribuido: $salva.somente_nao_atribuido == true, ordenar_por: $salva.ordenar_por, direcao: $salva.direcao} : {escopo: $input.escopo, numero: null, status: null, ativo_id: null, data_inicio: null, data_fim: null, prioridade: null, responsavel_id: null, somente_nao_atribuido: false, ordenar_por: "numero", direcao: "DESC"} }
  }
  response = {preferencia: $preferencia}
  guid = "miraObterPrefFila01"
}
