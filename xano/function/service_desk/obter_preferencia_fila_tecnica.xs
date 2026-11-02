function "service_desk/obter_preferencia_fila_tecnica" {
  input {
    int usuarios_id { table = "usuarios" }
    text escopo filters=trim
  }
  stack {
    function.run "autorizacao/exigir_perfil" { input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "legado converte escalares": {id: 12, role: "tecnico", lojas_id: null}
        "snapshot vazio vence legado": {id: 12, role: "tecnico", lojas_id: null}
        "json invalido nao restaura legado": {id: 12, role: "tecnico", lojas_id: null}
        "sem preferencia retorna vazio": {id: 12, role: "tecnico", lojas_id: null}
      }
    } as $usuario
    precondition ($input.escopo == "todos" || $input.escopo == "atribuidos_a_mim") {
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
      mock = {
        "legado converte escalares": {status: "Novo", ativos_referencia_id: 7, filtros_multiplos: null}
        "snapshot vazio vence legado": {status: "Novo", ativos_referencia_id: 7, filtros_multiplos: {status: [], ativo_ids: [], loja_ids: [], prioridades: [], responsavel_ids: [], incluir_nao_atribuido: false}}
        "json invalido nao restaura legado": {status: "Novo", filtros_multiplos: {status: "Novo"}}
        "sem preferencia retorna vazio": null
      }
    } as $salva
    var $multiplos { value = {status: [], ativo_ids: [], loja_ids: [], prioridades: [], responsavel_ids: [], incluir_nao_atribuido: false} }
    conditional {
      if ($salva != null && $salva.filtros_multiplos == null) {
        var.update $multiplos { value = {status: ($salva.status != null && $salva.status != "") ? [$salva.status] : [], ativo_ids: $salva.ativos_referencia_id != null ? [$salva.ativos_referencia_id] : [], loja_ids: $salva.lojas_id != null ? [$salva.lojas_id] : [], prioridades: ($salva.prioridade != null && $salva.prioridade != "") ? [$salva.prioridade] : [], responsavel_ids: $salva.responsavel_id != null ? [$salva.responsavel_id] : [], incluir_nao_atribuido: $salva.somente_nao_atribuido == true} }
      }
      elseif ($salva != null && $salva.filtros_multiplos != null) {
        var.update $multiplos { value = $salva.filtros_multiplos }
        precondition (($multiplos|is_object) && ($multiplos.status|is_array) && ($multiplos.ativo_ids|is_array) && ($multiplos.loja_ids|is_array) && ($multiplos.prioridades|is_array) && ($multiplos.responsavel_ids|is_array) && ($multiplos.incluir_nao_atribuido|is_bool)) {
          error_type = "standard"
          error = "Preferência persistida inválida."
        }
      }
    }
    foreach ($multiplos.status) {
      each as $s {
        precondition (($s|is_text) && ($s == "Novo" || $s == "Em Atendimento" || $s == "Aguardando Solicitante" || $s == "Aguardando Mudança" || $s == "Resolvido" || $s == "Solução Rejeitada" || $s == "Encerrado" || $s == "Cancelado")) {
          error_type = "standard"
          error = "Preferência persistida inválida."
        }
      }
    }
    foreach ($multiplos.prioridades) {
      each as $v {
        precondition (($v|is_text) && ($v == "Baixa" || $v == "Média" || $v == "Alta" || $v == "Urgente")) {
          error_type = "standard"
          error = "Preferência persistida inválida."
        }
      }
    }
    foreach ($multiplos.ativo_ids) {
      each as $v {
        precondition (($v|is_int) && $v > 0) {
          error_type = "standard"
          error = "Preferência persistida inválida."
        }
      }
    }
    foreach ($multiplos.loja_ids) {
      each as $v {
        precondition (($v|is_int) && $v > 0) {
          error_type = "standard"
          error = "Preferência persistida inválida."
        }
      }
    }
    foreach ($multiplos.responsavel_ids) {
      each as $v {
        precondition (($v|is_int) && $v > 0) {
          error_type = "standard"
          error = "Preferência persistida inválida."
        }
      }
    }
    var $preferencia { value = {numero: $salva.numero, status: $multiplos.status, ativo_ids: $multiplos.ativo_ids, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, ultima_atualizacao_inicio: $salva.ultima_atualizacao_inicio, ultima_atualizacao_fim: $salva.ultima_atualizacao_fim , escopo: $input.escopo, loja_ids: $multiplos.loja_ids, prioridades: $multiplos.prioridades, responsavel_ids: $multiplos.responsavel_ids, incluir_nao_atribuido: $multiplos.incluir_nao_atribuido, ordenar_por: ($salva.ordenar_por ?? "numero"), direcao: ($salva.direcao ?? "DESC")} }
  }
  response = {preferencia: $preferencia}
  test "legado converte escalares" {
    input = {usuarios_id: 12, escopo: "todos"}
    expect.to_equal ($response.preferencia.status) { value = ["Novo"] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [7] }
  }
  test "snapshot vazio vence legado" {
    input = {usuarios_id: 12, escopo: "todos"}
    expect.to_equal ($response.preferencia.status) { value = [] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [] }
  }
  test "json invalido nao restaura legado" {
    input = {usuarios_id: 12, escopo: "todos"}
    expect.to_throw { exception = "" }
  }
  test "sem preferencia retorna vazio" {
    input = {usuarios_id: 12, escopo: "todos"}
    expect.to_equal ($response.preferencia.status) { value = [] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [] }
  }
  guid = "miraObterPrefFila01"
}
