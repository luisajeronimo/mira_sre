// Lista operacional de chamados associados aos ativos da Loja do Gerente.
function "service_desk/listar_chamados_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    text numero? filters=trim
    text status? filters=trim
    text ativo_id? filters=trim
    timestamp data_inicio?
    timestamp data_fim?
    text ordenar_por? filters=trim
    text direcao? filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "lista padrão da loja": {id: 8, role: "gerente", lojas_id: 1}
        "lista vazio": {id: 8, role: "gerente", lojas_id: 1}
      }
    } as $usuario

    // Inputs inteiros opcionais do Xano materializam ausência como 0. A
    // fronteira textual preserva "" para ausência e permite rejeitar 0,
    // negativos e texto não numérico sem usar sentinela pública.
    var $aplicar_numero {
      value = $input.numero != ""
    }
    var $numero_convertido {
      value = ($input.numero|to_int)
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

    var $aplicar_ativo {
      value = $input.ativo_id != ""
    }
    var $ativo_convertido {
      value = ($input.ativo_id|to_int)
    }
    var $ativo_texto_valido {
      value = !$aplicar_ativo || ($ativo_convertido > 0 && ($ativo_convertido|to_text) == $input.ativo_id)
    }
    var $ativo_id_normalizado {
      value = null
    }
    conditional {
      if ($aplicar_ativo && $ativo_texto_valido) {
        var.update $ativo_id_normalizado {
          value = $ativo_convertido
        }
      }
    }

    var $aplicar_status {
      value = false
    }
    var $status_normalizado {
      value = null
    }
    conditional {
      if ($input.status != null && $input.status != "") {
        var.update $aplicar_status {
          value = true
        }
        var.update $status_normalizado {
          value = $input.status
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

    var $status_valido {
      value = !$aplicar_status || $status_normalizado == "Novo" || $status_normalizado == "Em Atendimento" || $status_normalizado == "Aguardando Solicitante" || $status_normalizado == "Aguardando Mudança" || $status_normalizado == "Resolvido" || $status_normalizado == "Solução Rejeitada" || $status_normalizado == "Encerrado" || $status_normalizado == "Cancelado"
    }

    var $ordenacao_valida {
      value = ($ordenar_por == "numero" || $ordenar_por == "titulo" || $ordenar_por == "status" || $ordenar_por == "prioridade" || $ordenar_por == "totem" || $ordenar_por == "categoria" || $ordenar_por == "criado_em" || $ordenar_por == "ultima_atualizacao_em") && ($direcao == "ASC" || $direcao == "DESC")
    }

    var $entrada_valida {
      value = $numero_texto_valido && $ativo_texto_valido && $status_valido && $ordenacao_valida && (!$aplicar_data_inicio || !$aplicar_data_fim || $data_inicio_normalizada < $data_fim_normalizada)
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

    conditional {
      if ($aplicar_ativo) {
        db.get ativos_referencia {
          field_name = "id"
          field_value = $ativo_id_normalizado
        } as $ativo_filtrado

        precondition ($ativo_filtrado != null) {
          error_type = "notfound"
          error = "Recurso não encontrado."
        }

        precondition ($ativo_filtrado.lojas_id == $usuario.lojas_id) {
          error_type = "accessdenied"
          error = "Acesso não autorizado."
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
            ativo: {
              table: "ativos_referencia"
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.id: "desc"}
          return = {type: "list"}
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            titulo_ordenavel: $db.chamados.titulo|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            titulo_ordenavel: $db.chamados.titulo|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            status_ordenavel: $db.chamados.status|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            status_ordenavel: $db.chamados.status|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            prioridade_ordenavel: $db.chamados.prioridade|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            prioridade_ordenavel: $db.chamados.prioridade|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            totem_ordenavel: $db.ativo.nome_ativo|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            totem_ordenavel: $db.ativo.nome_ativo|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            categoria_ordenavel: $db.categoria.nome|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            categoria_ordenavel: $db.categoria.nome|to_lower
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {categoria_ordenavel: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($ordenar_por == "criado_em" && $direcao == "ASC") {
        db.query chamados {
          join = {
            ativo: {
              table: "ativos_referencia"
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.criado_em: "desc", chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "lista padrão da loja": [
              {id: 102, titulo: "Atual", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000003000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Rede"}
            ]
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
            ativo: {
              table: "ativos_referencia"
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
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
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.ultima_atualizacao_em: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      else {
        db.query chamados {
          join = {
            ativo: {
              table: "ativos_referencia"
              type: "inner"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
            }
            categoria: {
              table: "categorias_servico"
              type: "left"
              where: $db.chamados.categorias_servico_id == $db.categoria.id
            }
          }
          eval = {
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
          }
          where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado) && ($db.chamados.status ==? $status_normalizado) && ($db.chamados.ativos_referencia_id ==? $ativo_id_normalizado) && ($db.chamados.criado_em >=? $data_inicio_normalizada) && ($db.chamados.criado_em <? $data_fim_normalizada)
          sort = {chamados.criado_em: "desc", chamados.id: "desc"}
          return = {type: "list"}
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
    }
    var $items {
      value = $chamados|map:{
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
    }
  }

  response = {items: $items, total: ($items|count)}

  test "lista padrão da loja" {
    input = {usuarios_id: 8}
    expect.to_equal ($response.total) { value = 2 }
    expect.to_not_equal ($response.items) { value = [] }
  }

  test "lista vazio" {
    input = {usuarios_id: 8}
    expect.to_be_empty ($response.items)
    expect.to_equal ($response.total) { value = 0 }
  }

  guid = "bsjXDAqhCr8qGwBABqPGX2sXVD8"
}
