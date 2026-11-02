function "service_desk/salvar_preferencia_fila_tecnica" {
  input {
    int usuarios_id { table = "usuarios" }
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
    function.run "autorizacao/exigir_perfil" { input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "upsert de outro usuario falha fechado": {id: 12, role: "tecnico", lojas_id: 1}
        "limpar grava snapshot vazio": {id: 12, role: "tecnico", lojas_id: null}
        "normaliza multiplos status": {id: 12, role: "tecnico", lojas_id: null}
        "rejeita status invalido": {id: 12, role: "tecnico", lojas_id: null}
      }
    } as $usuario
    conditional {
      if (!($input.escopo == "todos" || $input.escopo == "atribuidos_a_mim")) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }
        precondition (false) {
          error_type = "inputerror"
          error = "Escopo inválido."
        }
      }
    }
    precondition ($input.escopo != "atribuidos_a_mim" || $usuario.role == "tecnico") {
          error_type = "accessdenied"
          error = "Acesso não autorizado."
        }
    var $status_normalizados { value = [] }
    foreach ($input.status ?? []) {
      each as $s {
        var $chave { value = ($s|trim|to_lower) }
        var $canonico { value = null }
        conditional {
        if ($chave == "novo") {
          var.update $canonico { value = "Novo" }
        }
        elseif ($chave == "em atendimento") {
          var.update $canonico { value = "Em Atendimento" }
        }
        elseif ($chave == "aguardando solicitante") {
          var.update $canonico { value = "Aguardando Solicitante" }
        }
        elseif ($chave == "aguardando mudança") {
          var.update $canonico { value = "Aguardando Mudança" }
        }
        elseif ($chave == "resolvido") {
          var.update $canonico { value = "Resolvido" }
        }
        elseif ($chave == "solução rejeitada") {
          var.update $canonico { value = "Solução Rejeitada" }
        }
        elseif ($chave == "encerrado") {
          var.update $canonico { value = "Encerrado" }
        }
        elseif ($chave == "cancelado") {
          var.update $canonico { value = "Cancelado" }
        }
        }
        conditional {
          if (!($canonico != null)) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Status inválido."
            }
          }
        }
        array.push $status_normalizados { value = $canonico }
      }
    }
    var.update $status_normalizados { value = $status_normalizados|unique }
    var $ativo_ids { value = ($input.ativo_ids ?? [])|unique }
    foreach ($ativo_ids) {
      each as $id {
        conditional {
          if (!($id > 0)) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Totem inválido."
            }
          }
        }
        db.get ativos_referencia {
          field_name = "id"
          field_value = $id
        } as $ativo
        conditional {
          if (!($ativo != null)) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Totem inválido."
            }
          }
        }
      }
    }
    var $loja_ids { value = ($input.loja_ids ?? [])|unique }
    foreach ($loja_ids) {
      each as $id {
        conditional {
          if (!($id > 0)) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Loja inválida."
            }
          }
        }
        db.get lojas {
          field_name = "id"
          field_value = $id
        } as $loja
        conditional {
          if (!($loja != null)) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Loja inválida."
            }
          }
        }
      }
    }
    var $responsavel_ids { value = ($input.responsavel_ids ?? [])|unique }
    foreach ($responsavel_ids) {
      each as $id {
        conditional {
          if (!($id > 0)) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Responsável inválido."
            }
          }
        }
        db.get usuarios {
          field_name = "id"
          field_value = $id
        } as $responsavel
        conditional {
          if (!($responsavel != null && $responsavel.role == "tecnico")) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Responsável inválido."
            }
          }
        }
      }
    }
    var $prioridades { value = ($input.prioridades ?? [])|unique }
    foreach ($prioridades) {
      each as $prioridade {
        conditional {
          if (!($prioridade == "Baixa" || $prioridade == "Média" || $prioridade == "Alta" || $prioridade == "Urgente")) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Prioridade inválida."
            }
          }
        }
      }
    }
    conditional {
      if (!(($input.ordenar_por == "numero" || $input.ordenar_por == "titulo" || $input.ordenar_por == "status" || $input.ordenar_por == "prioridade" || $input.ordenar_por == "totem" || $input.ordenar_por == "loja" || $input.ordenar_por == "categoria" || $input.ordenar_por == "aberto_por" || $input.ordenar_por == "responsavel" || $input.ordenar_por == "criado_em" || $input.ordenar_por == "ultima_atualizacao_em") && ($input.direcao == "ASC" || $input.direcao == "DESC"))) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }
        precondition (false) {
          error_type = "inputerror"
          error = "Ordenação inválida."
        }
      }
    }
    conditional {
      if (!(($input.numero == null || $input.numero > 0) && ($input.data_inicio == null || $input.data_fim == null || $input.data_inicio < $input.data_fim) && ($input.ultima_atualizacao_inicio == null || $input.ultima_atualizacao_fim == null || $input.ultima_atualizacao_inicio < $input.ultima_atualizacao_fim))) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }
        precondition (false) {
          error_type = "inputerror"
          error = "Preferência inválida."
        }
      }
    }
    var $multiplos { value = {status: $status_normalizados, ativo_ids: $ativo_ids, loja_ids: $loja_ids, prioridades: $prioridades, responsavel_ids: $responsavel_ids, incluir_nao_atribuido: ($input.incluir_nao_atribuido == true)} }
    var $chave_logica { value = ($usuario.id|to_text) ~ ":" ~ $input.escopo }
    db.add_or_edit preferencias_fila_chamados {
      field_name = "chave_logica"
      field_value = $chave_logica
      data = {usuarios_id: $usuario.id, escopo: $input.escopo, chave_logica: $chave_logica, numero: $input.numero, status: null, ativos_referencia_id: null, data_inicio: $input.data_inicio, data_fim: $input.data_fim, ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio, ultima_atualizacao_fim: $input.ultima_atualizacao_fim, lojas_id: null, prioridade: null, responsavel_id: null, somente_nao_atribuido: false, filtros_multiplos: $multiplos, ordenar_por: $input.ordenar_por, direcao: $input.direcao, atualizado_em: now}
      mock = {
        "upsert de outro usuario falha fechado": {usuarios_id: 999, escopo: "todos"}
        "limpar grava snapshot vazio": {usuarios_id: 12, escopo: "todos", ordenar_por: "numero", direcao: "DESC"}
        "normaliza multiplos status": {usuarios_id: 12, escopo: "todos", ordenar_por: "numero", direcao: "DESC"}
      }
    } as $salva
    precondition ($salva != null && $salva.usuarios_id == $usuario.id && $salva.escopo == $input.escopo) {
          error_type = "standard"
          error = "Não foi possível salvar a preferência."
        }
    var $preferencia { value = {numero: $salva.numero, status: $multiplos.status, ativo_ids: $multiplos.ativo_ids, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, ultima_atualizacao_inicio: $salva.ultima_atualizacao_inicio, ultima_atualizacao_fim: $salva.ultima_atualizacao_fim, escopo: $input.escopo, loja_ids: $multiplos.loja_ids, prioridades: $multiplos.prioridades, responsavel_ids: $multiplos.responsavel_ids, incluir_nao_atribuido: $multiplos.incluir_nao_atribuido, ordenar_por: $salva.ordenar_por, direcao: $salva.direcao} }
  }
  response = {preferencia: $preferencia}
  test "limpar grava snapshot vazio" {
    input = {usuarios_id: 12, status: [], escopo: "todos", ordenar_por: "numero", direcao: "DESC"}
    expect.to_equal ($response.preferencia.status) { value = [] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [] }
  }
  test "normaliza multiplos status" {
    input = {usuarios_id: 12, status: [" novo ", "Resolvido", "Novo"], escopo: "todos", ordenar_por: "numero", direcao: "DESC"}
    expect.to_equal ($response.preferencia.status) { value = ["Novo", "Resolvido"] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [] }
  }
  test "rejeita status invalido" {
    input = {usuarios_id: 12, status: ["Invalido"], escopo: "todos", ordenar_por: "numero", direcao: "DESC"}
    expect.to_throw { exception = "" }
  }
  test "upsert de outro usuario falha fechado" {
    input = {usuarios_id: 12, status: [], escopo: "todos", ordenar_por: "numero", direcao: "DESC"}
    expect.to_throw { exception = "" }
  }
  guid = "miraSalvarPrefFila01"
}
