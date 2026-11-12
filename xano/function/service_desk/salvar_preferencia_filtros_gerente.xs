// Substitui integralmente a preferência local depois da consulta candidata.
function "service_desk/salvar_preferencia_filtros_gerente" {
  input {
    int usuarios_id { table = "usuarios" }
    int? numero?
    text[] status?
    int[] ativo_ids?
    timestamp? data_inicio?
    timestamp? data_fim?
    timestamp? ultima_atualizacao_inicio?
    timestamp? ultima_atualizacao_fim?
  }
  stack {
    function.run "autorizacao/exigir_perfil" { input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "upsert de outro usuario falha fechado": {id: 8, role: "gerente", lojas_id: 1}
        "limpar grava snapshot vazio": {id: 8, role: "gerente", lojas_id: 1}
        "normaliza multiplos status": {id: 8, role: "gerente", lojas_id: 1}
        "rejeita status invalido": {id: 8, role: "gerente", lojas_id: 1}
        "aceita totem atual": {id: 8, role: "gerente", lojas_id: 1}
        "rejeita totem transferido": {id: 8, role: "gerente", lojas_id: 1}
        "rejeita totem externo": {id: 8, role: "gerente", lojas_id: 1}
      }
    } as $usuario
    precondition ($usuario.lojas_id != null) {
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
          mock = {
            "aceita totem atual": {id: 16, lojas_id: 1}
            "rejeita totem transferido": {id: 17, lojas_id: 2}
            "rejeita totem externo": {id: 18, lojas_id: 2}
          }
        } as $ativo
        precondition ($ativo != null && $ativo.lojas_id == $usuario.lojas_id) {
          error_type = "accessdenied"
          error = "Acesso não autorizado."
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
    var $multiplos { value = {status: $status_normalizados, ativo_ids: $ativo_ids, loja_ids: [], prioridades: [], responsavel_ids: [], incluir_nao_atribuido: false} }
    var $chave_logica { value = ($usuario.id|to_text) ~ ":" ~ "todos" }
    db.add_or_edit preferencias_fila_chamados {
      field_name = "chave_logica"
      field_value = $chave_logica
      data = {usuarios_id: $usuario.id, escopo: "todos", chave_logica: $chave_logica, numero: $input.numero, status: null, ativos_referencia_id: null, data_inicio: $input.data_inicio, data_fim: $input.data_fim, ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio, ultima_atualizacao_fim: $input.ultima_atualizacao_fim, lojas_id: null, prioridade: null, responsavel_id: null, somente_nao_atribuido: false, filtros_multiplos: $multiplos, atualizado_em: now}
      mock = {
        "upsert de outro usuario falha fechado": {usuarios_id: 999, escopo: "todos"}
        "limpar grava snapshot vazio": {usuarios_id: 8, escopo: "todos"}
        "normaliza multiplos status": {usuarios_id: 8, escopo: "todos"}
        "aceita totem atual": {usuarios_id: 8, escopo: "todos"}
      }
    } as $salva
    precondition ($salva != null && $salva.usuarios_id == $usuario.id && $salva.escopo == "todos") {
          error = "Não foi possível salvar a preferência."
        }
    var $preferencia { value = {numero: $salva.numero, status: $multiplos.status, ativo_ids: $multiplos.ativo_ids, data_inicio: $salva.data_inicio, data_fim: $salva.data_fim, ultima_atualizacao_inicio: $salva.ultima_atualizacao_inicio, ultima_atualizacao_fim: $salva.ultima_atualizacao_fim} }
  }
  response = {preferencia: $preferencia}
  test "limpar grava snapshot vazio" {
    input = {usuarios_id: 8, status: []}
    expect.to_equal ($response.preferencia.status) { value = [] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [] }
  }
  test "normaliza multiplos status" {
    input = {usuarios_id: 8, status: [" novo ", "Resolvido", "Novo"]}
    expect.to_equal ($response.preferencia.status) { value = ["Novo", "Resolvido"] }
    expect.to_equal ($response.preferencia.ativo_ids) { value = [] }
  }
  test "aceita totem atual" {
    input = {usuarios_id: 8, ativo_ids: [16]}
    expect.to_equal ($response.preferencia.ativo_ids) { value = [16] }
  }
  test "rejeita totem transferido" {
    input = {usuarios_id: 8, ativo_ids: [17]}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  test "rejeita totem externo" {
    input = {usuarios_id: 8, ativo_ids: [18]}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  test "rejeita status invalido" {
    input = {usuarios_id: 8, status: ["Invalido"]}
    expect.to_throw { exception = "" }
  }
  test "upsert de outro usuario falha fechado" {
    input = {usuarios_id: 8, status: []}
    expect.to_throw { exception = "" }
  }
  guid = "miraPrefGerentePut01"
}
