// Lista global com os mesmos filtros explícitos da lista do Gerente.
function "service_desk/listar_chamados_tecnico" {
  input {
    int usuarios_id { table = "usuarios" }
    text numero? filters=trim
    text status? filters=trim
    text ativo_id? filters=trim
    timestamp data_inicio?
    timestamp data_fim?
    bool somente_atribuidos_a_mim?
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
    } as $usuario

    precondition ($input.somente_atribuidos_a_mim != true || $usuario.role == "tecnico") {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    var $tecnico_id_normalizado {
      value = $input.somente_atribuidos_a_mim == true ? $usuario.id : null
    }

    var $aplicar_numero { value = $input.numero != null && $input.numero != "" }
    var $numero_convertido { value = ($input.numero|to_int) }
    var $numero_valido { value = !$aplicar_numero || ($numero_convertido > 0 && ($numero_convertido|to_text) == $input.numero) }
    var $numero_normalizado { value = null }
    conditional { if ($aplicar_numero && $numero_valido) { var.update $numero_normalizado { value = $numero_convertido } } }

    var $aplicar_ativo { value = $input.ativo_id != null && $input.ativo_id != "" }
    var $ativo_convertido { value = ($input.ativo_id|to_int) }
    var $ativo_valido { value = !$aplicar_ativo || ($ativo_convertido > 0 && ($ativo_convertido|to_text) == $input.ativo_id) }
    var $ativo_normalizado { value = null }
    conditional { if ($aplicar_ativo && $ativo_valido) { var.update $ativo_normalizado { value = $ativo_convertido } } }

    var $aplicar_status { value = $input.status != null && $input.status != "" }
    var $status_normalizado { value = $aplicar_status ? $input.status : null }
    var $aplicar_data_inicio { value = $input.data_inicio != null && $input.data_inicio != "" }
    var $aplicar_data_fim { value = $input.data_fim != null && $input.data_fim != "" }
    var $status_valido { value = !$aplicar_status || $status_normalizado == "Novo" || $status_normalizado == "Em Atendimento" || $status_normalizado == "Aguardando Solicitante" || $status_normalizado == "Aguardando Mudança" || $status_normalizado == "Resolvido" || $status_normalizado == "Solução Rejeitada" || $status_normalizado == "Encerrado" || $status_normalizado == "Cancelado" }

    conditional {
      if (!$numero_valido || !$ativo_valido || !$status_valido || ($aplicar_data_inicio && $aplicar_data_fim && $input.data_inicio >= $input.data_fim)) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }
        precondition (false) {
          error_type = "inputerror"
          error = "Consulta inválida."
        }
      }
    }

    db.query chamados {
      join = {
        ativo: {
          table: "ativos_referencia"
          type: "left"
          where: $db.chamados.ativos_referencia_id == $db.ativo.id
        }
        loja: {
          table: "lojas"
          type: "left"
          where: $db.ativo.lojas_id == $db.loja.id
        }
        categoria: {
          table: "categorias_servico"
          type: "left"
          where: $db.chamados.categorias_servico_id == $db.categoria.id
        }
        solicitante: {
          table: "usuarios"
          type: "left"
          where: $db.chamados.solicitante_id == $db.solicitante.id
        }
        tecnico: {
          table: "usuarios"
          type: "left"
          where: $db.chamados.tecnico_id == $db.tecnico.id
        }
      }
      eval = {
        ativo_id: $db.ativo.id, ativo_nome: $db.ativo.nome_ativo,
        loja_id: $db.loja.id, loja_nome: $db.loja.nome,
        categoria_id: $db.categoria.id, categoria_nome: $db.categoria.nome,
        solicitante_usuario_id: $db.solicitante.id, solicitante_nome: $db.solicitante.nome,
        tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome
      }
      where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
      sort = {chamados.id: "desc"}
      return = {type: "list"}
    } as $chamados

    var $items {
      value = $chamados|map:{
        id: $$.id, titulo: $$.titulo, descricao: $$.descricao, status: $$.status,
        prioridade: $$.prioridade, origem: $$.origem, criador_sistema: $$.criador_sistema,
        criado_em: $$.criado_em, ultima_atualizacao_em: $$.ultima_atualizacao_em,
        sla_horas_aplicado: $$.sla_horas_aplicado,
        atribuido_em: ($$.atribuido_em != null && $$.atribuido_em != 0) ? $$.atribuido_em : null,
        ativo: {id: $$.ativo_id, nome_ativo: $$.ativo_nome},
        loja: ($$.loja_id != null && $$.loja_id != 0) ? {id: $$.loja_id, nome: $$.loja_nome} : null,
        categoria: {id: $$.categoria_id, nome: $$.categoria_nome},
        solicitante: ($$.solicitante_usuario_id != null && $$.solicitante_usuario_id != 0) ? {id: $$.solicitante_usuario_id, nome: $$.solicitante_nome} : null,
        tecnico: ($$.tecnico_usuario_id != null && $$.tecnico_usuario_id != 0) ? {id: $$.tecnico_usuario_id, nome: $$.tecnico_nome} : null
      }
    }
  }

  response = {items: $items, total: ($items|count)}
  guid = "miraFilaTecnico01"
}
