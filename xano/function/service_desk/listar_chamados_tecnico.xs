// Lista global com os mesmos filtros explícitos da lista do Gerente.
function "service_desk/listar_chamados_tecnico" {
  input {
    int usuarios_id { table = "usuarios" }
    text numero? filters=trim
    text status? filters=trim
    text ativo_id? filters=trim
    timestamp data_inicio?
    timestamp data_fim?
    text prioridade? filters=trim
    text responsavel_id? filters=trim
    text ordenar_por? filters=trim
    text direcao? filters=trim
    bool somente_atribuidos_a_mim?
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
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

    var $aplicar_ativo { value = $input.ativo_id != null && $input.ativo_id != "" }
    var $ativo_convertido { value = ($input.ativo_id|to_int) }
    var $ativo_valido { value = !$aplicar_ativo || ($ativo_convertido > 0 && ($ativo_convertido|to_text) == $input.ativo_id) }
    var $ativo_normalizado { value = null }
    conditional {
      if ($aplicar_ativo && $ativo_valido) {
        var.update $ativo_normalizado {
          value = $ativo_convertido
        }
      }
    }

    var $aplicar_status { value = $input.status != null && $input.status != "" }
    // O filtro chega livre do cliente, mas é comparado/persistido no literal canônico.
    var $status_chave { value = $input.status|to_lower }
    var $status_normalizado { value = null }
    conditional {
      if ($status_chave == "novo") {
        var.update $status_normalizado {
          value = "Novo"
        }
      }
      elseif ($status_chave == "em atendimento") {
        var.update $status_normalizado {
          value = "Em Atendimento"
        }
      }
      elseif ($status_chave == "aguardando solicitante") {
        var.update $status_normalizado {
          value = "Aguardando Solicitante"
        }
      }
      elseif ($status_chave == "aguardando mudança") {
        var.update $status_normalizado {
          value = "Aguardando Mudança"
        }
      }
      elseif ($status_chave == "resolvido") {
        var.update $status_normalizado {
          value = "Resolvido"
        }
      }
      elseif ($status_chave == "solução rejeitada") {
        var.update $status_normalizado {
          value = "Solução Rejeitada"
        }
      }
      elseif ($status_chave == "encerrado") {
        var.update $status_normalizado {
          value = "Encerrado"
        }
      }
      elseif ($status_chave == "cancelado") {
        var.update $status_normalizado {
          value = "Cancelado"
        }
      }
    }
    var $aplicar_prioridade { value = $input.prioridade != null && $input.prioridade != "" }
    var $prioridade_normalizada { value = $aplicar_prioridade ? $input.prioridade : null }
    var $aplicar_responsavel { value = $input.responsavel_id != null && $input.responsavel_id != "" }
    var $responsavel_convertido { value = $input.responsavel_id|to_int }
    var $responsavel_formato_valido { value = !$aplicar_responsavel || ($responsavel_convertido >= 0 && ($responsavel_convertido|to_text) == $input.responsavel_id) }
    var $responsavel_id_normalizado { value = null }
    var $filtrar_sem_responsavel { value = false }
    var $responsavel_valido { value = !$aplicar_responsavel }
    conditional {
      if ($aplicar_responsavel && $responsavel_formato_valido && $responsavel_convertido == 0) {
        var.update $filtrar_sem_responsavel { value = true }
        var.update $responsavel_valido { value = true }
      }
      elseif ($aplicar_responsavel && $responsavel_formato_valido) {
        var.update $responsavel_id_normalizado { value = $responsavel_convertido }
        db.get usuarios {
          field_name = "id"
          field_value = $responsavel_convertido
        } as $responsavel
        conditional {
          if ($responsavel != null && $responsavel.role == "tecnico") {
            var.update $responsavel_valido { value = true }
          }
        }
      }
    }
    var $ordenar_por { value = ($input.ordenar_por != null && $input.ordenar_por != "") ? $input.ordenar_por : "numero" }
    var $direcao { value = ($input.direcao != null && $input.direcao != "") ? $input.direcao : "DESC" }
    var $aplicar_data_inicio { value = $input.data_inicio != null && $input.data_inicio != "" }
    var $aplicar_data_fim { value = $input.data_fim != null && $input.data_fim != "" }
    var $status_valido { value = !$aplicar_status || $status_normalizado != null }
    var $prioridade_valida { value = !$aplicar_prioridade || $prioridade_normalizada == "Baixa" || $prioridade_normalizada == "Média" || $prioridade_normalizada == "Alta" || $prioridade_normalizada == "Urgente" }
    var $ordenacao_valida { value = ($ordenar_por == "numero" || $ordenar_por == "titulo" || $ordenar_por == "status" || $ordenar_por == "prioridade" || $ordenar_por == "totem" || $ordenar_por == "categoria" || $ordenar_por == "aberto_por" || $ordenar_por == "responsavel" || $ordenar_por == "criado_em" || $ordenar_por == "ultima_atualizacao_em") && ($direcao == "ASC" || $direcao == "DESC") }

    conditional {
      if (!$numero_valido || !$ativo_valido || !$status_valido || !$prioridade_valida || !$responsavel_valido || !$ordenacao_valida || ($aplicar_data_inicio && $aplicar_data_fim && $input.data_inicio >= $input.data_fim)) {
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "consulta padrão preserva query base": ```
              [{id: 102, prioridade: "Alta"}, {id: 101, prioridade: "Média"}]
              ```
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {totem_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "asc"}
          return = {type: "list"}
          mock = {
            "ordena responsável com não atribuído ao final": ```
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
          sort = {chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "ordena responsável descendente com não atribuído ao final": ```
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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
          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_normalizado) && ($db.chamados.criado_em >=? $input.data_inicio) && ($db.chamados.criado_em <? $input.data_fim) && ($db.chamados.tecnico_id ==? $tecnico_id_normalizado)
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

    // Prioridade e responsável continuam no backend, após a consulta já
    // ordenada; array.filter preserva a ordem obtida no Xano.
    var $chamados_filtrados {
      value = $chamados
    }
    conditional {
      if ($aplicar_prioridade) {
        array.filter ($chamados_filtrados) if ($this.prioridade == $prioridade_normalizada) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
      }
    }
    conditional {
      if ($aplicar_responsavel && $filtrar_sem_responsavel) {
        array.filter ($chamados_filtrados) if ($this.tecnico_id == null || $this.tecnico_id == 0) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
      }
      elseif ($aplicar_responsavel) {
        array.filter ($chamados_filtrados) if ($this.tecnico_id == $responsavel_id_normalizado) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
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

  test "filtra prioridade após query base" {
    input = {usuarios_id: 12, prioridade: "Alta"}
    expect.to_equal ($response.total) {
      value = 1
    }
  }

  test "combina prioridade e responsável após query ordenada" {
    input = {usuarios_id: 12, prioridade: "Alta", responsavel_id: "10"}
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
    input = {usuarios_id: 12, responsavel_id: "10"}
    expect.to_equal ($response.total) {
      value = 1
    }
  }

  test "filtra não atribuído sem predicado search dinâmico" {
    input = {usuarios_id: 12, responsavel_id: "0"}
    expect.to_equal ($response.total) {
      value = 2
    }
  }

  guid = "miraFilaTecnico01"
}
