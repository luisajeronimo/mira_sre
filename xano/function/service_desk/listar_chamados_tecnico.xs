// Lista global com os mesmos filtros explícitos da lista do Gerente.
function "service_desk/listar_chamados_tecnico" {
  input {
    int usuarios_id { table = "usuarios" }
    text numero? filters=trim
    text[] status?
    int[] ativo_ids?
    timestamp data_inicio?
    timestamp data_fim?
    timestamp ultima_atualizacao_inicio?
    timestamp ultima_atualizacao_fim?
    int[] loja_ids?
    text[] prioridades?
    int[] responsavel_ids?
    bool incluir_nao_atribuido?
    text ordenar_por? filters=trim
    text direcao? filters=trim
    bool somente_atribuidos_a_mim?
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "multiplos status usam OR": {id: 12, role: "tecnico"}
        "filtros diferentes usam AND": {id: 12, role: "tecnico"}
        "responsavel inclui nao atribuido": {id: 12, role: "tecnico"}
        "usa loja historica": {id: 12, role: "tecnico"}
        "consulta padrão preserva query base": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "filtra prioridade após query base": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "combina prioridade e responsável após query ordenada": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "filtra responsável sem predicado search dinâmico": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "filtra não atribuído sem predicado search dinâmico": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "ordena responsável pelo texto exibido ascendente": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "ordena responsável pelo texto exibido descendente": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
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
    conditional {
      if ($aplicar_numero && $numero_valido) {
        var.update $numero_normalizado {
          value = $numero_convertido
        }
      }
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
          mock = {
        "combina prioridade e responsável após query ordenada": {id: 10, role: "tecnico"}
        "responsavel inclui nao atribuido": {id: 10, role: "tecnico"}
        "filtra responsável sem predicado search dinâmico": {id: 10, role: "tecnico"}
      }
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
    var $ordenar_por { value = ($input.ordenar_por != null && $input.ordenar_por != "") ? $input.ordenar_por : "numero" }
    var $direcao { value = ($input.direcao != null && $input.direcao != "") ? $input.direcao : "DESC" }
    var $aplicar_data_inicio { value = $input.data_inicio != null && $input.data_inicio != "" }
    var $aplicar_data_fim { value = $input.data_fim != null && $input.data_fim != "" }
    var $aplicar_ultima_atualizacao_inicio { value = $input.ultima_atualizacao_inicio != null && $input.ultima_atualizacao_inicio != "" }
    var $aplicar_ultima_atualizacao_fim { value = $input.ultima_atualizacao_fim != null && $input.ultima_atualizacao_fim != "" }
    var $ordenacao_valida { value = ($ordenar_por == "numero" || $ordenar_por == "titulo" || $ordenar_por == "status" || $ordenar_por == "prioridade" || $ordenar_por == "totem" || $ordenar_por == "loja" || $ordenar_por == "categoria" || $ordenar_por == "aberto_por" || $ordenar_por == "responsavel" || $ordenar_por == "criado_em" || $ordenar_por == "ultima_atualizacao_em") && ($direcao == "ASC" || $direcao == "DESC") }

    conditional {
      if (!$numero_valido || !$ordenacao_valida || ($aplicar_data_inicio && $aplicar_data_fim && $input.data_inicio >= $input.data_fim) || ($aplicar_ultima_atualizacao_inicio && $aplicar_ultima_atualizacao_fim && $input.ultima_atualizacao_inicio >= $input.ultima_atualizacao_fim)) {
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

    // $ordenar_por é validado por whitelist; numero é a projeção interna
    // de chamados.id e nunca uma chave pública id.
    var $chamados {
      value = []
    }

    conditional {
      if ($ordenar_por == "numero" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "numero" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "multiplos status usam OR": [{id: 4, status: "Novo", prioridade: "Alta", tecnico_id: 10}, {id: 3, status: "Resolvido", prioridade: "Média", tecnico_id: 11}, {id: 2, status: "Novo", prioridade: "Alta", tecnico_id: null}, {id: 1, status: "Encerrado", prioridade: "Baixa", tecnico_id: 11}]
            "filtros diferentes usam AND": [{id: 4, status: "Novo", prioridade: "Alta", tecnico_id: 10}, {id: 3, status: "Resolvido", prioridade: "Média", tecnico_id: 11}, {id: 2, status: "Novo", prioridade: "Alta", tecnico_id: null}, {id: 1, status: "Encerrado", prioridade: "Baixa", tecnico_id: 11}]
            "responsavel inclui nao atribuido": [{id: 4, status: "Novo", prioridade: "Alta", tecnico_id: 10}, {id: 3, status: "Resolvido", prioridade: "Média", tecnico_id: 11}, {id: 2, status: "Novo", prioridade: "Alta", tecnico_id: null}, {id: 1, status: "Encerrado", prioridade: "Baixa", tecnico_id: 11}]
            "consulta padrão preserva query base": ```
              [{id: 102, prioridade: "Alta"}, {id: 101, prioridade: "Média"}]
              ```
            "usa loja historica": [{id: 105, ativo_id: 1, criado_em: 1780000000000, loja_id: 2, loja_nome: "Loja de destino"}]
            "filtra prioridade após query base": ```
              [{id: 102, prioridade: "Alta"}, {id: 101, prioridade: "Média"}]
              ```
            "combina prioridade e responsável após query ordenada": ```
              [{id: 104, prioridade: "Alta", tecnico_id: 10}, {id: 103, prioridade: "Alta", tecnico_id: 11}, {id: 102, prioridade: "Média", tecnico_id: 10}]
              ```
            "filtra responsável sem predicado search dinâmico": ```
              [{id: 103, tecnico_id: 11}, {id: 102, tecnico_id: 10}, {id: 101, tecnico_id: null}]
              ```
            "filtra não atribuído sem predicado search dinâmico": ```
              [{id: 103, tecnico_id: 11}, {id: 102, tecnico_id: 10}, {id: 101, tecnico_id: null}, {id: 100, tecnico_id: 0}]
              ```
          }
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "titulo" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {titulo_ordenavel: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "titulo" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {titulo_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "status" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {status_ordenavel: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "status" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {status_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "prioridade" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {prioridade_ordenavel: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "prioridade" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {prioridade_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "totem" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {totem_ordenavel: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "totem" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {totem_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "loja" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo: {table: "ativos_referencia", type: "left", where: $db.chamados.ativos_referencia_id == $db.ativo.id}
            loja: {table: "lojas", type: "left", where: $db.ativo.lojas_id == $db.loja.id}
            categoria: {table: "categorias_servico", type: "left", where: $db.chamados.categorias_servico_id == $db.categoria.id}
            solicitante: {table: "usuarios", type: "left", where: $db.chamados.solicitante_id == $db.solicitante.id}
            tecnico: {table: "usuarios", type: "left", where: $db.chamados.tecnico_id == $db.tecnico.id}
          }
          eval = {
            ativo_id: $db.ativo.id, ativo_nome: $db.ativo.nome_ativo,
            loja_id: $db.loja.id, loja_nome: $db.loja.nome, loja_ordenavel: $db.loja.nome|to_lower,
            categoria_id: $db.categoria.id, categoria_nome: $db.categoria.nome,
            solicitante_usuario_id: $db.solicitante.id, solicitante_nome: $db.solicitante.nome,
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id, titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower, prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower, categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower, criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {loja_ordenavel: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado
        var.update $chamados { value = $resultado }
      }
      elseif ($ordenar_por == "loja" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo: {table: "ativos_referencia", type: "left", where: $db.chamados.ativos_referencia_id == $db.ativo.id}
            loja: {table: "lojas", type: "left", where: $db.ativo.lojas_id == $db.loja.id}
            categoria: {table: "categorias_servico", type: "left", where: $db.chamados.categorias_servico_id == $db.categoria.id}
            solicitante: {table: "usuarios", type: "left", where: $db.chamados.solicitante_id == $db.solicitante.id}
            tecnico: {table: "usuarios", type: "left", where: $db.chamados.tecnico_id == $db.tecnico.id}
          }
          eval = {
            ativo_id: $db.ativo.id, ativo_nome: $db.ativo.nome_ativo,
            loja_id: $db.loja.id, loja_nome: $db.loja.nome, loja_ordenavel: $db.loja.nome|to_lower,
            categoria_id: $db.categoria.id, categoria_nome: $db.categoria.nome,
            solicitante_usuario_id: $db.solicitante.id, solicitante_nome: $db.solicitante.nome,
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id, titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower, prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower, categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower, criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {loja_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado
        var.update $chamados { value = $resultado }
      }
      elseif ($ordenar_por == "categoria" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {categoria_ordenavel: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "categoria" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {categoria_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "responsavel" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo: {table: "ativos_referencia", type: "left", where: $db.chamados.ativos_referencia_id == $db.ativo.id}
            loja: {table: "lojas", type: "left", where: $db.ativo.lojas_id == $db.loja.id}
            categoria: {table: "categorias_servico", type: "left", where: $db.chamados.categorias_servico_id == $db.categoria.id}
            solicitante: {table: "usuarios", type: "left", where: $db.chamados.solicitante_id == $db.solicitante.id}
            tecnico: {table: "usuarios", type: "left", where: $db.chamados.tecnico_id == $db.tecnico.id}
          }
          eval = {
            ativo_id: $db.ativo.id, ativo_nome: $db.ativo.nome_ativo,
            loja_id: $db.loja.id, loja_nome: $db.loja.nome,
            categoria_id: $db.categoria.id, categoria_nome: $db.categoria.nome,
            solicitante_usuario_id: $db.solicitante.id, solicitante_nome: $db.solicitante.nome,
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "asc"}
          return = {type: "list"}
          mock = {
            "ordena responsável pelo texto exibido ascendente": ```
              [
                {id: 400, tecnico_usuario_id: 10, tecnico_nome: "Zeca"},
                {id: 302, tecnico_usuario_id: 20, tecnico_nome: "ana"},
                {id: 301, tecnico_usuario_id: 21, tecnico_nome: "Ana"},
                {id: 101, tecnico_usuario_id: null, tecnico_nome: null},
                {id: 100, tecnico_usuario_id: 0, tecnico_nome: null}
              ]
              ```
          }
        } as $resultado
        var.update $chamados { value = $resultado }
      }
      elseif ($ordenar_por == "responsavel" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo: {table: "ativos_referencia", type: "left", where: $db.chamados.ativos_referencia_id == $db.ativo.id}
            loja: {table: "lojas", type: "left", where: $db.ativo.lojas_id == $db.loja.id}
            categoria: {table: "categorias_servico", type: "left", where: $db.chamados.categorias_servico_id == $db.categoria.id}
            solicitante: {table: "usuarios", type: "left", where: $db.chamados.solicitante_id == $db.solicitante.id}
            tecnico: {table: "usuarios", type: "left", where: $db.chamados.tecnico_id == $db.tecnico.id}
          }
          eval = {
            ativo_id: $db.ativo.id, ativo_nome: $db.ativo.nome_ativo,
            loja_id: $db.loja.id, loja_nome: $db.loja.nome,
            categoria_id: $db.categoria.id, categoria_nome: $db.categoria.nome,
            solicitante_usuario_id: $db.solicitante.id, solicitante_nome: $db.solicitante.nome,
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "ordena responsável pelo texto exibido descendente": ```
              [
                {id: 100, tecnico_usuario_id: 0, tecnico_nome: null},
                {id: 101, tecnico_usuario_id: null, tecnico_nome: null},
                {id: 301, tecnico_usuario_id: 21, tecnico_nome: "Ana"},
                {id: 302, tecnico_usuario_id: 20, tecnico_nome: "ana"},
                {id: 400, tecnico_usuario_id: 10, tecnico_nome: "Zeca"}
              ]
              ```
          }
        } as $resultado
        var.update $chamados { value = $resultado }
      }
      elseif ($ordenar_por == "aberto_por") {
        db.query chamados {
          join = {
            ativo: {table: "ativos_referencia", type: "left", where: $db.chamados.ativos_referencia_id == $db.ativo.id}
            loja: {table: "lojas", type: "left", where: $db.ativo.lojas_id == $db.loja.id}
            categoria: {table: "categorias_servico", type: "left", where: $db.chamados.categorias_servico_id == $db.categoria.id}
            solicitante: {table: "usuarios", type: "left", where: $db.chamados.solicitante_id == $db.solicitante.id}
            tecnico: {table: "usuarios", type: "left", where: $db.chamados.tecnico_id == $db.tecnico.id}
          }
          eval = {
            ativo_id: $db.ativo.id, ativo_nome: $db.ativo.nome_ativo,
            loja_id: $db.loja.id, loja_nome: $db.loja.nome,
            categoria_id: $db.categoria.id, categoria_nome: $db.categoria.nome,
            solicitante_usuario_id: $db.solicitante.id, solicitante_nome: $db.solicitante.nome,
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado
        var.update $chamados { value = $resultado }
      }
      elseif ($ordenar_por == "criado_em" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.criado_em: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "criado_em" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.criado_em: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "ultima_atualizacao_em" && $direcao == "ASC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.ultima_atualizacao_em: "asc", chamados.id: "asc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "ultima_atualizacao_em" && $direcao == "DESC") {
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
            tecnico_usuario_id: $db.tecnico.id, tecnico_nome: $db.tecnico.nome,
            numero: $db.chamados.id,
            titulo_ordenavel: $db.chamados.titulo|to_lower,
            status_ordenavel: $db.chamados.status|to_lower,
            prioridade_ordenavel: $db.chamados.prioridade|to_lower,
            totem_ordenavel: $db.ativo.nome_ativo|to_lower,
            categoria_ordenavel: $db.categoria.nome|to_lower,
            tecnico_ordenavel: $db.tecnico.nome|to_lower,
            criado_em: $db.chamados.criado_em,
            ultima_atualizacao_em: $db.chamados.ultima_atualizacao_em
          }
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.ultima_atualizacao_em: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
    }
    // O Query all Records mantém a composição comprovadamente funcional de
    // filtros `where`. Para responsável, a ordem é composta após a query pelo
    // mesmo texto exibido na fila, inclusive "Não atribuído".
    conditional {
      if ($ordenar_por == "responsavel") {
        var $chaves_responsavel {
          value = $chamados|map:{
            chave: ((($$.tecnico_usuario_id != null && $$.tecnico_usuario_id != 0) ? $$.tecnico_nome : "Não atribuído")|to_lower) ~ "|" ~ ($$.id|to_text),
            chamado: $$
          }
        }
        var $chamados_ordenados { value = $chaves_responsavel|sort:"chave":"natural":true }
        conditional {
          if ($direcao == "DESC") {
            var.update $chamados_ordenados { value = $chamados_ordenados|reverse }
          }
        }
        var.update $chamados {
          value = $chamados_ordenados|map:$$.chamado
        }
      }
    }
    conditional {
      if ($ordenar_por == "aberto_por") {
        var $chaves_aberto_por {
          value = $chamados|map:{
            chave: ((($$.origem == "automatico") ? "bot de fiscalização" : (($$.solicitante_nome != null && $$.solicitante_nome != "") ? ($$.solicitante_nome|to_lower) : "não informado")) ~ "|" ~ ($$.id|to_text)),
            chamado: $$
          }
        }
        var $chamados_ordenados { value = $chaves_aberto_por|sort:"chave":"natural":true }
        conditional {
          if ($direcao == "DESC") {
            var.update $chamados_ordenados { value = $chamados_ordenados|reverse }
          }
        }
        var.update $chamados { value = $chamados_ordenados|map:$$.chamado }
      }
    }

    // Filtragem no backend após ordenação preserva o desempate original.
    // Resolve Loja histórica antes de filtrar ou apresentar a fila global.
    var $chamados_historicos { value = [] }
    foreach ($chamados) {
      each as $chamado {
        var $ativo_id_fato { value = $chamado|get:"ativo_id":null }
        var $instante_fato { value = $chamado|get:"criado_em":null }
        var $lojas_id_historico { value = null }
        var $loja_nome_historica { value = null }
        conditional {
          if ($ativo_id_fato != null && $instante_fato != null) {
            function.run "administracao/resolver_loja_totem_no_instante" {
              input = {
                ativos_referencia_id: $ativo_id_fato
                instante: $instante_fato
              }
              mock = {
                "usa loja historica": {lojas_id: 3}
              }
            } as $historico
            var.update $lojas_id_historico { value = $historico.lojas_id }
            conditional {
              if ($lojas_id_historico != null) {
                db.get lojas {
                  field_name = "id"
                  field_value = $lojas_id_historico
                  mock = {
                    "usa loja historica": {id: 3, nome: "Loja de origem"}
                  }
                } as $loja_historica
                conditional {
                  if ($loja_historica != null) {
                    var.update $loja_nome_historica { value = $loja_historica.nome }
                  }
                }
              }
            }
          }
        }
        var $chamado_historico {
          value = $chamado|set:"loja_id":$lojas_id_historico|set:"loja_nome":$loja_nome_historica|set:"loja_ordenavel":($loja_nome_historica != null ? ($loja_nome_historica|to_lower) : null)
        }
        array.push $chamados_historicos { value = $chamado_historico }
      }
    }
    conditional {
      if ($ordenar_por == "loja") {
        var.update $chamados_historicos { value = $chamados_historicos|sort:"loja_ordenavel":"natural":true }
        conditional {
          if ($direcao == "DESC") {
            var.update $chamados_historicos { value = $chamados_historicos|reverse }
          }
        }
      }
    }
    var $chamados_filtrados { value = $chamados_historicos }
    conditional {
      if (($status_normalizados|count) > 0) {
        array.filter ($chamados_filtrados) if ($status_normalizados|in:$this.status) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    conditional {
      if (($ativo_ids|count) > 0) {
        array.filter ($chamados_filtrados) if ($ativo_ids|in:$this.ativo_id) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    conditional {
      if (($prioridades|count) > 0) {
        array.filter ($chamados_filtrados) if ($prioridades|in:$this.prioridade) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    conditional {
      if (($responsavel_ids|count) > 0 || $input.incluir_nao_atribuido == true) {
        array.filter ($chamados_filtrados) if (($responsavel_ids|in:$this.tecnico_id) || ($input.incluir_nao_atribuido == true && ($this.tecnico_id == null || $this.tecnico_id == 0))) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    conditional {
      if (($loja_ids|count) > 0) {
        array.filter ($chamados_filtrados) if ($loja_ids|in:$this.loja_id) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    conditional {
      if ($aplicar_ultima_atualizacao_inicio) {
        array.filter ($chamados_filtrados) if ($this.ultima_atualizacao_em >= $input.ultima_atualizacao_inicio) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    conditional {
      if ($aplicar_ultima_atualizacao_fim) {
        array.filter ($chamados_filtrados) if ($this.ultima_atualizacao_em < $input.ultima_atualizacao_fim) as $resultado_filtrado
        var.update $chamados_filtrados { value = $resultado_filtrado }
      }
    }
    var $items {
      value = $chamados_filtrados|map:{
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

  test "consulta padrão preserva query base" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.total) {
      value = 2
    }
  }

  test "usa loja historica" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [{id: 105, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: 1, nome_ativo: null}, loja: {id: 3, nome: "Loja de origem"}, categoria: {id: null, nome: null}, solicitante: null, tecnico: null}]
    }
  }

  test "filtra prioridade após query base" {
    input = {usuarios_id: 12, prioridades: ["Alta"]}
    expect.to_equal ($response.total) {
      value = 1
    }
  }

  test "combina prioridade e responsável após query ordenada" {
    input = {usuarios_id: 12, prioridades: ["Alta"], responsavel_ids: [10]}
    expect.to_equal ($response.total) {
      value = 1
    }
  }

  test "ordena responsável pelo texto exibido ascendente" {
    input = {usuarios_id: 12, ordenar_por: "responsavel", direcao: "ASC"}
    expect.to_equal ($response.items) {
      value = [
        {id: 301, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: {id: 21, nome: "Ana"}},
        {id: 302, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: {id: 20, nome: "ana"}},
        {id: 100, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: null},
        {id: 101, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: null},
        {id: 400, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: {id: 10, nome: "Zeca"}}
      ]
    }
  }

  test "ordena responsável pelo texto exibido descendente" {
    input = {usuarios_id: 12, ordenar_por: "responsavel", direcao: "DESC"}
    expect.to_equal ($response.items) {
      value = [
        {id: 400, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: {id: 10, nome: "Zeca"}},
        {id: 101, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: null},
        {id: 100, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: null},
        {id: 302, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: {id: 20, nome: "ana"}},
        {id: 301, titulo: null, descricao: null, status: null, prioridade: null, origem: null, criador_sistema: null, criado_em: null, ultima_atualizacao_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo: {id: null, nome_ativo: null}, loja: null, categoria: {id: null, nome: null}, solicitante: null, tecnico: {id: 21, nome: "Ana"}}
      ]
    }
  }

  test "filtra responsável sem predicado search dinâmico" {
    input = {usuarios_id: 12, responsavel_ids: [10]}
    expect.to_equal ($response.total) {
      value = 1
    }
  }

  test "filtra não atribuído sem predicado search dinâmico" {
    input = {usuarios_id: 12, incluir_nao_atribuido: true}
    expect.to_equal ($response.total) {
      value = 2
    }
  }

  test "multiplos status usam OR" {
    input = {usuarios_id: 12, status: ["Novo", "Resolvido"]}
    expect.to_equal ($response.total) { value = 3 }
  }
  test "filtros diferentes usam AND" {
    input = {usuarios_id: 12, status: ["Novo", "Resolvido"], prioridades: ["Alta"]}
    expect.to_equal ($response.total) { value = 2 }
  }
  test "responsavel inclui nao atribuido" {
    input = {usuarios_id: 12, responsavel_ids: [10], incluir_nao_atribuido: true}
    expect.to_equal ($response.total) { value = 2 }
  }
  guid = "miraFilaTecnico01"
}
