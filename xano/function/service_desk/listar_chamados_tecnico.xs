// Lista a fila técnica global nas duas visões aprovadas.
function "service_desk/listar_chamados_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    text visao? filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true}
      mock = {
        "não atribuídos": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "atribuídos a mim": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "visão inválida": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    var $visao_valida {
      value = $input.visao == "nao_atribuidos" || $input.visao == "atribuidos_a_mim"
    }

    conditional {
      if (!$visao_valida) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Visão inválida."
        }
      }
    }

    var $chamados {
      value = []
    }

    conditional {
      if ($input.visao == "nao_atribuidos") {
        db.query chamados {
          join = {
            ativo: {
              table: "ativos_referencia"
              type: "left"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
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
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            solicitante_usuario_id: $db.solicitante.id
            solicitante_nome: $db.solicitante.nome
            tecnico_usuario_id: $db.tecnico.id
            tecnico_nome: $db.tecnico.nome
          }
          where = $db.chamados.status == "Novo" && ($db.chamados.tecnico_id == null || $db.chamados.tecnico_id == 0)
          sort = {chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "não atribuídos": ```
              [{id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}]
              ```
          }
        } as $resultado

        var.update $chamados {
          value = $resultado
        }
      }
      elseif ($input.visao == "atribuidos_a_mim") {
        db.query chamados {
          join = {
            ativo: {
              table: "ativos_referencia"
              type: "left"
              where: $db.chamados.ativos_referencia_id == $db.ativo.id
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
            ativo_id: $db.ativo.id
            ativo_nome: $db.ativo.nome_ativo
            categoria_id: $db.categoria.id
            categoria_nome: $db.categoria.nome
            solicitante_usuario_id: $db.solicitante.id
            solicitante_nome: $db.solicitante.nome
            tecnico_usuario_id: $db.tecnico.id
            tecnico_nome: $db.tecnico.nome
          }
          where = $db.chamados.status == "Novo" && $db.chamados.tecnico_id == $usuario.id
          sort = {chamados.id: "desc"}
          return = {type: "list"}
          mock = {
            "atribuídos a mim": ```
              [{id: 102, titulo: "Falha atribuída", descricao: "Descrição", status: "Novo", prioridade: "Urgente", origem: "automatico", criado_em: 1780000000000, sla_horas_aplicado: 4, atribuido_em: 1780000001000, ativo_id: 2, ativo_nome: "Totem 02", categoria_id: 3, categoria_nome: "Falha de Energia", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: 12, tecnico_nome: "Técnico"}]
              ```
          }
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
        sla_horas_aplicado: $$.sla_horas_aplicado,
        atribuido_em: $$.atribuido_em,
        ativo: {id: $$.ativo_id, nome_ativo: $$.ativo_nome},
        categoria: {id: $$.categoria_id, nome: $$.categoria_nome},
        solicitante: {id: $$.solicitante_usuario_id, nome: $$.solicitante_nome},
        tecnico: {id: $$.tecnico_usuario_id, nome: $$.tecnico_nome}
      }
    }
  }

  response = {items: $items}

  test "não atribuídos" {
    input = {usuarios_id: 12, visao: "nao_atribuidos"}
    expect.to_equal ($response.items) { value = [{id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: null, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Falha de Rede"}, solicitante: {id: 8, nome: "Gerente"}, tecnico: {id: null, nome: null}}] }
  }

  test "atribuídos a mim" {
    input = {usuarios_id: 12, visao: "atribuidos_a_mim"}
    expect.to_equal ($response.items) { value = [{id: 102, titulo: "Falha atribuída", descricao: "Descrição", status: "Novo", prioridade: "Urgente", origem: "automatico", criado_em: 1780000000000, sla_horas_aplicado: 4, atribuido_em: 1780000001000, ativo: {id: 2, nome_ativo: "Totem 02"}, categoria: {id: 3, nome: "Falha de Energia"}, solicitante: {id: null, nome: null}, tecnico: {id: 12, nome: "Técnico"}}] }
  }

  test "visão inválida" {
    input = {usuarios_id: 12, visao: "todos"}
    expect.to_throw { exception = "" }
  }

  guid = "miraFilaTecnico01"
}
