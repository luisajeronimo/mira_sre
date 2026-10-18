function "service_desk/salvar_preferencia_fila_tecnica" {
  input {
    int usuarios_id { table = "usuarios" }
    text escopo filters=trim
    int? numero?
    text? status? filters=trim
    int? ativo_id? { table = "ativos_referencia" }
    timestamp? data_inicio?
    timestamp? data_fim?
    text? prioridade? filters=trim
    int? responsavel_id? { table = "usuarios" }
    bool somente_nao_atribuido?
    text ordenar_por filters=trim
    text direcao filters=trim
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
    var $status_chave { value = $input.status|to_lower }
    var $status { value = null }
    conditional {
      if ($input.status == null || $input.status == "") {
        var.update $status {
          value = null
        }
      }
      elseif ($status_chave == "novo") {
        var.update $status {
          value = "Novo"
        }
      }
      elseif ($status_chave == "em atendimento") {
        var.update $status {
          value = "Em Atendimento"
        }
      }
      elseif ($status_chave == "aguardando solicitante") {
        var.update $status {
          value = "Aguardando Solicitante"
        }
      }
      elseif ($status_chave == "aguardando mudança") {
        var.update $status {
          value = "Aguardando Mudança"
        }
      }
      elseif ($status_chave == "resolvido") {
        var.update $status {
          value = "Resolvido"
        }
      }
      elseif ($status_chave == "solução rejeitada") {
        var.update $status {
          value = "Solução Rejeitada"
        }
      }
      elseif ($status_chave == "encerrado") {
        var.update $status {
          value = "Encerrado"
        }
      }
      elseif ($status_chave == "cancelado") {
        var.update $status {
          value = "Cancelado"
        }
      }
    }
    var $responsavel { value = null }
    conditional {
      if ($input.responsavel_id != null) {
        db.get usuarios {
          field_name = "id"
          field_value = $input.responsavel_id
        } as $responsavel_encontrado
        var.update $responsavel { value = $responsavel_encontrado }
      }
    }
    var $ordem_valida { value = ($input.ordenar_por == "numero" || $input.ordenar_por == "titulo" || $input.ordenar_por == "status" || $input.ordenar_por == "prioridade" || $input.ordenar_por == "totem" || $input.ordenar_por == "categoria" || $input.ordenar_por == "responsavel" || $input.ordenar_por == "criado_em" || $input.ordenar_por == "ultima_atualizacao_em") && ($input.direcao == "ASC" || $input.direcao == "DESC") }
    precondition (($input.numero == null || $input.numero > 0) && ($input.status == null || $input.status == "" || $status != null) && ($input.prioridade == null || $input.prioridade == "" || $input.prioridade == "Baixa" || $input.prioridade == "Média" || $input.prioridade == "Alta" || $input.prioridade == "Urgente") && ($input.responsavel_id == null || ($responsavel != null && $responsavel.role == "tecnico")) && !($input.responsavel_id != null && $input.somente_nao_atribuido == true) && $ordem_valida && ($input.data_inicio == null || $input.data_fim == null || $input.data_inicio < $input.data_fim)) {
      error_type = "inputerror"
      error = "Preferência inválida."
    }
    var $agora {
      value = now
    }
    // add_or_edit usa uma única chave para evitar a corrida leitura+add quando
    // duas primeiras escritas válidas encontram a preferência ausente.
    var $chave_logica { value = ($usuario.id|to_text) ~ ":" ~ $input.escopo }
    db.add_or_edit preferencias_fila_chamados {
      field_name = "chave_logica"
      field_value = $chave_logica
      data = {usuarios_id: $usuario.id, escopo: $input.escopo, chave_logica: $chave_logica, numero: $input.numero, status: $status, ativos_referencia_id: $input.ativo_id, data_inicio: $input.data_inicio, data_fim: $input.data_fim, prioridade: $input.prioridade, responsavel_id: $input.responsavel_id, somente_nao_atribuido: $input.somente_nao_atribuido == true, ordenar_por: $input.ordenar_por, direcao: $input.direcao, atualizado_em: $agora}
    } as $salva
    precondition ($salva != null && $salva.usuarios_id == $usuario.id && $salva.escopo == $input.escopo) {
      error_type = "standard"
      error = "Não foi possível salvar a preferência."
    }
    var $preferencia { value = {escopo: $salva.escopo, numero: $salva.numero, status: $salva.status, ativo_id: $salva.ativos_referencia_id, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, prioridade: $salva.prioridade, responsavel_id: $salva.responsavel_id, somente_nao_atribuido: $salva.somente_nao_atribuido == true, ordenar_por: $salva.ordenar_por, direcao: $salva.direcao} }
  }
  response = {preferencia: $preferencia}
  guid = "miraSalvarPrefFila01"
}
