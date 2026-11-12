// Lista operacional de chamados associados aos ativos da Loja do Gerente.
function "service_desk/listar_chamados_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }

    text numero? filters=trim
    text[] status?
    int[] ativo_ids?
    timestamp data_inicio?
    timestamp data_fim?
    timestamp ultima_atualizacao_inicio?
    timestamp ultima_atualizacao_fim?
    text ordenar_por? filters=trim
    text direcao? filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "lista padrão da loja": {id: 8, role: "gerente", lojas_id: 1}
        "lista inclui chamado historicamente autorizado": {id: 8, role: "gerente", lojas_id: 1}
        "lista exclui chamado de outra loja historica": {id: 8, role: "gerente", lojas_id: 1}
        "lista exclui chamado sem loja historica": {id: 8, role: "gerente", lojas_id: 1}
        "lista vazio"          : {id: 8, role: "gerente", lojas_id: 1}
        "aceita filtro de totem atual": {id: 8, role: "gerente", lojas_id: 1}
        "rejeita filtro de totem transferido": {id: 8, role: "gerente", lojas_id: 1}
        "rejeita filtro de totem externo": {id: 8, role: "gerente", lojas_id: 1}
      }
    } as $usuario

    // Inputs inteiros opcionais do Xano materializam ausência como 0. A
    // fronteira textual preserva "" para ausência e permite rejeitar 0,
    // negativos e texto não numérico sem usar sentinela pública.
    var $aplicar_numero {
      value = $input.numero != ""
    }

    var $numero_convertido {
      value = $input.numero|to_int
    }

    var $numero_texto_valido {
      value = !$aplicar_numero || ($numero_convertido > 0 && ($numero_convertido|to_text) == $input.numero)
    }

    var $numero_normalizado {
      value = null
    }

    conditional {
      if ($aplicar_numero && $numero_texto_valido) {
        var.update $numero_normalizado {
          value = $numero_convertido
        }
      }
    }

    var $status_normalizados {
      value = []
    }

    foreach ($input.status ?? []) {
      each as $s {
        var $chave {
          value = $s|trim|to_lower
        }

        var $canonico {
          value = null
        }

        conditional {
          if ($chave == "novo") {
            var.update $canonico {
              value = "Novo"
            }
          }

          elseif ($chave == "em atendimento") {
            var.update $canonico {
              value = "Em Atendimento"
            }
          }

          elseif ($chave == "aguardando solicitante") {
            var.update $canonico {
              value = "Aguardando Solicitante"
            }
          }

          elseif ($chave == "aguardando mudança") {
            var.update $canonico {
              value = "Aguardando Mudança"
            }
          }

          elseif ($chave == "resolvido") {
            var.update $canonico {
              value = "Resolvido"
            }
          }

          elseif ($chave == "solução rejeitada") {
            var.update $canonico {
              value = "Solução Rejeitada"
            }
          }

          elseif ($chave == "encerrado") {
            var.update $canonico {
              value = "Encerrado"
            }
          }

          elseif ($chave == "cancelado") {
            var.update $canonico {
              value = "Cancelado"
            }
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

        array.push $status_normalizados {
          value = $canonico
        }
      }
    }

    var.update $status_normalizados {
      value = $status_normalizados|unique
    }

    var $ativo_ids {
      value = ($input.ativo_ids ?? [])|unique
    }

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
            "aceita filtro de totem atual": {id: 16, lojas_id: 1}
            "rejeita filtro de totem transferido": {id: 17, lojas_id: 2}
            "rejeita filtro de totem externo": {id: 18, lojas_id: 2}
          }
        } as $ativo

        precondition ($ativo != null && $ativo.lojas_id == $usuario.lojas_id) {
          error_type = "accessdenied"
          error = "Acesso não autorizado."
        }
      }
    }

    var $aplicar_data_inicio {
      value = false
    }

    var $data_inicio_normalizada {
      value = null
    }

    conditional {
      if ($input.data_inicio != null && $input.data_inicio != "") {
        var.update $aplicar_data_inicio {
          value = true
        }

        var.update $data_inicio_normalizada {
          value = $input.data_inicio
        }
      }
    }

    var $aplicar_data_fim {
      value = false
    }

    var $aplicar_ultima_atualizacao_inicio {
      value = $input.ultima_atualizacao_inicio != null && $input.ultima_atualizacao_inicio != ""
    }

    var $aplicar_ultima_atualizacao_fim {
      value = $input.ultima_atualizacao_fim != null && $input.ultima_atualizacao_fim != ""
    }

    var $data_fim_normalizada {
      value = null
    }

    conditional {
      if ($input.data_fim != null && $input.data_fim != "") {
        var.update $aplicar_data_fim {
          value = true
        }

        var.update $data_fim_normalizada {
          value = $input.data_fim
        }
      }
    }

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    var $ordenar_por {
      value = $input.ordenar_por
    }

    var $direcao {
      value = $input.direcao
    }

    // Entradas textuais opcionais chegam como string vazia em alguns clientes.
    // Normaliza ausência, null e vazio antes da whitelist, preservando a
    // rejeição de qualquer valor explicitamente inválido.
    conditional {
      if ($ordenar_por == null || $ordenar_por == "") {
        var.update $ordenar_por {
          value = "criado_em"
        }
      }
    }

    conditional {
      if ($direcao == null || $direcao == "") {
        var.update $direcao {
          value = "DESC"
        }
      }
    }

    var $ordenacao_valida {
      value = ($ordenar_por == "numero" || $ordenar_por == "titulo" || $ordenar_por == "status" || $ordenar_por == "prioridade" || $ordenar_por == "totem" || $ordenar_por == "categoria" || $ordenar_por == "criado_em" || $ordenar_por == "ultima_atualizacao_em") && ($direcao == "ASC" || $direcao == "DESC")
    }

    var $entrada_valida {
      value = $numero_texto_valido && $ordenacao_valida && (!$aplicar_data_inicio || !$aplicar_data_fim || $data_inicio_normalizada < $data_fim_normalizada) && (!$aplicar_ultima_atualizacao_inicio || !$aplicar_ultima_atualizacao_fim || $input.ultima_atualizacao_inicio < $input.ultima_atualizacao_fim)
    }

    conditional {
      if (!$entrada_valida) {
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

    var $chamados {
      value = []
    }

    // Cada db.query recebe o predicado completo: referências $db não podem ser
    // encapsuladas em variável externa, pois perdem o contexto da consulta no runtime Xano.
    // O runtime Xano aceita projeções diretas em eval, mas não expressões booleanas.
    // Campos textuais são projetados em minúsculas para ordenar no backend sem
    // considerar caixa; datas funcionais usam consulta direta com desempate por id.
    conditional {
      if ($ordenar_por == "numero" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.id: "asc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "numero" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.id: "desc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "titulo" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {titulo_ordenavel: "asc", chamados.id: "asc"}
          eval = {
            ativo_id        : $db.ativo.id
            ativo_nome      : $db.ativo.nome_ativo
            categoria_id    : $db.categoria.id
            categoria_nome  : $db.categoria.nome
            titulo_ordenavel: $db.chamados.titulo|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "titulo" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {titulo_ordenavel: "desc", chamados.id: "desc"}
          eval = {
            ativo_id        : $db.ativo.id
            ativo_nome      : $db.ativo.nome_ativo
            categoria_id    : $db.categoria.id
            categoria_nome  : $db.categoria.nome
            titulo_ordenavel: $db.chamados.titulo|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "status" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {status_ordenavel: "asc", chamados.id: "asc"}
          eval = {
            ativo_id        : $db.ativo.id
            ativo_nome      : $db.ativo.nome_ativo
            categoria_id    : $db.categoria.id
            categoria_nome  : $db.categoria.nome
            status_ordenavel: $db.chamados.status|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "status" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {status_ordenavel: "desc", chamados.id: "desc"}
          eval = {
            ativo_id        : $db.ativo.id
            ativo_nome      : $db.ativo.nome_ativo
            categoria_id    : $db.categoria.id
            categoria_nome  : $db.categoria.nome
            status_ordenavel: $db.chamados.status|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "prioridade" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {prioridade_ordenavel: "asc", chamados.id: "asc"}
          eval = {
            ativo_id            : $db.ativo.id
            ativo_nome          : $db.ativo.nome_ativo
            categoria_id        : $db.categoria.id
            categoria_nome      : $db.categoria.nome
            prioridade_ordenavel: $db.chamados.prioridade|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "prioridade" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {prioridade_ordenavel: "desc", chamados.id: "desc"}
          eval = {
            ativo_id            : $db.ativo.id
            ativo_nome          : $db.ativo.nome_ativo
            categoria_id        : $db.categoria.id
            categoria_nome      : $db.categoria.nome
            prioridade_ordenavel: $db.chamados.prioridade|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "totem" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {totem_ordenavel: "asc", chamados.id: "asc"}
          eval = {
            ativo_id       : $db.ativo.id
            ativo_nome     : $db.ativo.nome_ativo
            categoria_id   : $db.categoria.id
            categoria_nome : $db.categoria.nome
            totem_ordenavel: $db.ativo.nome_ativo|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "totem" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {totem_ordenavel: "desc", chamados.id: "desc"}
          eval = {
            ativo_id       : $db.ativo.id
            ativo_nome     : $db.ativo.nome_ativo
            categoria_id   : $db.categoria.id
            categoria_nome : $db.categoria.nome
            totem_ordenavel: $db.ativo.nome_ativo|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "categoria" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {categoria_ordenavel: "asc", chamados.id: "asc"}
          eval = {
            ativo_id           : $db.ativo.id
            ativo_nome         : $db.ativo.nome_ativo
            categoria_id       : $db.categoria.id
            categoria_nome     : $db.categoria.nome
            categoria_ordenavel: $db.categoria.nome|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "categoria" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {categoria_ordenavel: "desc", chamados.id: "desc"}
          eval = {
            ativo_id           : $db.ativo.id
            ativo_nome         : $db.ativo.nome_ativo
            categoria_id       : $db.categoria.id
            categoria_nome     : $db.categoria.nome
            categoria_ordenavel: $db.categoria.nome|to_lower
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "criado_em" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.criado_em: "asc", chamados.id: "asc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "criado_em" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.criado_em: "desc", chamados.id: "desc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
          mock = {
            "lista padrão da loja": ```
              [
                {id: 102, titulo: "Atual", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000003000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Rede"}
              ]
              ```
            "lista inclui chamado historicamente autorizado": ```
              [
                {id: 201, titulo: "Loja histórica", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000003000, ativo_id: 1, ativo_nome: "Totem 01", ativo_lojas_id: 2, categoria_id: 2, categoria_nome: "Rede"}
              ]
              ```
            "lista exclui chamado de outra loja historica": ```
              [
                {id: 202, titulo: "Outra loja", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000003000, ativo_id: 2, ativo_nome: "Totem 02", ativo_lojas_id: 1, categoria_id: 2, categoria_nome: "Rede"}
              ]
              ```
            "lista exclui chamado sem loja historica": ```
              [
                {id: 203, titulo: "Sem histórico", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000003000, ativo_id: 3, ativo_nome: "Totem 03", ativo_lojas_id: 1, categoria_id: 2, categoria_nome: "Rede"}
              ]
              ```
            "lista vazio": []
          }
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "ultima_atualizacao_em" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.ultima_atualizacao_em: "asc", chamados.id: "asc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      elseif ($ordenar_por == "ultima_atualizacao_em" && $direcao == "DESC") {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.ultima_atualizacao_em: "desc", chamados.id: "desc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }

      else {
        db.query chamados {
          join = {
            ativo    : {
              table: "ativos_referencia"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type : "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }

          where = ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.criado_em: "desc", chamados.id: "desc"}
          eval = {
            ativo_id      : $db.ativo.id
            ativo_nome    : $db.ativo.nome_ativo
            categoria_id  : $db.categoria.id
            categoria_nome: $db.categoria.nome
          }

          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
    }

    // O escopo do Gerente usa a Loja no instante do chamado, nunca a Loja atual.
    var $historicos_autorizados {
      value = []
    }

    foreach ($chamados) {
      each as $chamado {
        function.run "administracao/resolver_loja_totem_no_instante" {
          input = {
            ativos_referencia_id: $chamado.ativo_id
            instante            : $chamado.criado_em
          }

          mock = {
            "lista padrão da loja": {lojas_id: 1}
            "lista inclui chamado historicamente autorizado": {lojas_id: 1}
            "lista exclui chamado de outra loja historica": {lojas_id: 2}
            "lista exclui chamado sem loja historica": {lojas_id: null}
            "lista vazio"          : {lojas_id: null}
          }
        } as $historico

        conditional {
          if ($historico.lojas_id != null && $historico.lojas_id == $usuario.lojas_id) {
            array.push $historicos_autorizados {
              value = $chamado
            }
          }
        }
      }
    }

    var $chamados_filtrados {
      value = $historicos_autorizados
    }

    conditional {
      if (($status_normalizados|count) > 0) {
        array.filter ($chamados_filtrados) if ($status_normalizados|in:$this.status) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
      }
    }

    conditional {
      if (($ativo_ids|count) > 0) {
        array.filter ($chamados_filtrados) if ($ativo_ids|in:$this.ativo_id) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
      }
    }

    conditional {
      if ($aplicar_ultima_atualizacao_inicio) {
        array.filter ($chamados_filtrados) if ($this.ultima_atualizacao_em >= $input.ultima_atualizacao_inicio) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
      }
    }

    conditional {
      if ($aplicar_ultima_atualizacao_fim) {
        array.filter ($chamados_filtrados) if ($this.ultima_atualizacao_em < $input.ultima_atualizacao_fim) as $resultado_filtrado
        var.update $chamados_filtrados {
          value = $resultado_filtrado
        }
      }
    }

    var $items {
      value = ```
        $chamados_filtrados|map:{
                id: $$.id,
                titulo: $$.titulo,
                descricao: $$.descricao,
                status: $$.status,
                prioridade: $$.prioridade,
                origem: $$.origem,
                criado_em: $$.criado_em,
                ultima_atualizacao_em: $$.ultima_atualizacao_em,
                ativo: {id: $$.ativo_id, nome_ativo: $$.ativo_nome},
                categoria: {id: $$.categoria_id, nome: $$.categoria_nome}
              }
        ```
    }
  }

  response = {items: $items, total: $items|count}

  test "lista padrão da loja" {
    input = {usuarios_id: 8}

    expect.to_equal ($response.total) {
      value = 1
    }

    expect.to_not_equal ($response.items) {
      value = []
    }
  }

  test "lista inclui chamado historicamente autorizado" {
    input = {usuarios_id: 8}

    expect.to_equal ($response.items) {
      value = [
        {id: 201, titulo: "Loja histórica", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000003000, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Rede"}}
      ]
    }

    expect.to_equal ($response.total) {
      value = 1
    }
  }

  test "lista exclui chamado de outra loja historica" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response.items)
    expect.to_equal ($response.total) {
      value = 0
    }
  }

  test "lista exclui chamado sem loja historica" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response.items)
    expect.to_equal ($response.total) {
      value = 0
    }
  }

  test "lista vazio" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response.items)
    expect.to_equal ($response.total) {
      value = 0
    }
  }

  test "aceita filtro de totem atual" {
    input = {usuarios_id: 8, ativo_ids: [16]}
    expect.to_equal ($response.total) { value = 0 }
  }

  test "rejeita filtro de totem transferido" {
    input = {usuarios_id: 8, ativo_ids: [17]}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "rejeita filtro de totem externo" {
    input = {usuarios_id: 8, ativo_ids: [18]}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  guid = "bsjXDAqhCr8qGwBABqPGX2sXVD8"
}
