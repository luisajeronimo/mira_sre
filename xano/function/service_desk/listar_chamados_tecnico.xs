// Lista a fila global nas visões simples aprovadas.
function "service_desk/listar_chamados_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    text visao? filters=trim
    text numero? filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "lista todos para Diretoria": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "lista todos para Administrador": ```
          {id: 12, nome: "Administradora", email: "admin@example.test", role: "administrador", lojas_id: null}
          ```
        "lista não atribuídos": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "lista atribuídos a mim": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "lista atribuídos a outros": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "pesquisa por número": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "visão inválida": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "número inválido": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    var $visao {
      value = $input.visao
    }
    conditional {
      if ($visao == null || $visao == "") {
        var.update $visao {
          value = "todos"
        }
      }
    }

    var $aplicar_numero {
      value = $input.numero != null && $input.numero != ""
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

    var $visao_valida {
      value = $visao == "todos" || $visao == "nao_atribuidos" || $visao == "atribuidos_a_mim" || $visao == "atribuidos_a_outros"
    }

    conditional {
      if (!$visao_valida || !$numero_texto_valido) {
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
      where = ($db.chamados.id ==? $numero_normalizado) && ($visao == "todos" || ($visao == "nao_atribuidos" && ($db.chamados.tecnico_id == null || $db.chamados.tecnico_id == 0)) || ($visao == "atribuidos_a_mim" && $usuario.role == "tecnico" && $db.chamados.tecnico_id == $usuario.id) || ($visao == "atribuidos_a_outros" && $db.chamados.tecnico_id != null && $db.chamados.tecnico_id != 0 && ($usuario.role != "tecnico" || $db.chamados.tecnico_id != $usuario.id)))
      sort = {chamados.id: "desc"}
      return = {type: "list"}
      mock = {
        "lista todos para Diretoria": ```
          [
            {id: 102, titulo: "Encerrado atribuído", descricao: "Descrição", status: "Encerrado", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000002000, sla_horas_aplicado: 2, atribuido_em: 1780000001000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: 12, tecnico_nome: "Técnico"},
            {id: 101, titulo: "Novo sem responsável", descricao: "Descrição", status: "Novo", prioridade: "Urgente", origem: "automatico", criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 4, atribuido_em: null, ativo_id: 2, ativo_nome: "Totem 02", categoria_id: 3, categoria_nome: "Falha de Energia", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: null, tecnico_nome: null}
          ]
          ```
        "lista todos para Administrador": ```
          [{id: 102, titulo: "Encerrado atribuído", descricao: "Descrição", status: "Encerrado", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000002000, sla_horas_aplicado: 2, atribuido_em: 1780000001000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: 12, tecnico_nome: "Técnico"}]
          ```
        "lista não atribuídos": ```
          [{id: 101, titulo: "Novo sem responsável", descricao: "Descrição", status: "Novo", prioridade: "Urgente", origem: "automatico", criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 4, atribuido_em: null, ativo_id: 2, ativo_nome: "Totem 02", categoria_id: 3, categoria_nome: "Falha de Energia", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: null, tecnico_nome: null}]
          ```
        "lista atribuídos a mim": ```
          [{id: 102, titulo: "Falha atribuída", descricao: "Descrição", status: "Resolvido", prioridade: "Urgente", origem: "automatico", criado_em: 1780000001000, ultima_atualizacao_em: 1780000001000, sla_horas_aplicado: 4, atribuido_em: 1780000001000, ativo_id: 2, ativo_nome: "Totem 02", categoria_id: 3, categoria_nome: "Falha de Energia", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: 12, tecnico_nome: "Técnico"}]
          ```
        "lista atribuídos a outros": ```
          [{id: 103, titulo: "Falha de outro Técnico", descricao: "Descrição", status: "Em Atendimento", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000002000, sla_horas_aplicado: 2, atribuido_em: 1780000002000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: 10, tecnico_nome: "Outro Técnico"}]
          ```
        "pesquisa por número": ```
          [{id: 102, titulo: "Falha atribuída", descricao: "Descrição", status: "Resolvido", prioridade: "Urgente", origem: "automatico", criado_em: 1780000001000, ultima_atualizacao_em: 1780000001000, sla_horas_aplicado: 4, atribuido_em: 1780000001000, ativo_id: 2, ativo_nome: "Totem 02", categoria_id: 3, categoria_nome: "Falha de Energia", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: 12, tecnico_nome: "Técnico"}]
          ```
        "visão inválida": []
        "número inválido": []
      }
    } as $chamados

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

  test "lista todos para Diretoria" {
    input = {usuarios_id: 4}
    expect.to_equal ($response.items) {
      value = [
        {id: 102, titulo: "Encerrado atribuído", descricao: "Descrição", status: "Encerrado", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000002000, sla_horas_aplicado: 2, atribuido_em: 1780000001000, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Falha de Rede"}, solicitante: {id: 8, nome: "Gerente"}, tecnico: {id: 12, nome: "Técnico"}},
        {id: 101, titulo: "Novo sem responsável", descricao: "Descrição", status: "Novo", prioridade: "Urgente", origem: "automatico", criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 4, atribuido_em: null, ativo: {id: 2, nome_ativo: "Totem 02"}, categoria: {id: 3, nome: "Falha de Energia"}, solicitante: {id: null, nome: null}, tecnico: {id: null, nome: null}}
      ]
    }
  }

  test "lista todos para Administrador" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [{id: 102, titulo: "Encerrado atribuído", descricao: "Descrição", status: "Encerrado", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000002000, sla_horas_aplicado: 2, atribuido_em: 1780000001000, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Falha de Rede"}, solicitante: {id: 8, nome: "Gerente"}, tecnico: {id: 12, nome: "Técnico"}}]
    }
  }

  test "lista não atribuídos" {
    input = {usuarios_id: 12, visao: "nao_atribuidos"}
    expect.to_equal ($response.items) {
      value = [{id: 101, titulo: "Novo sem responsável", descricao: "Descrição", status: "Novo", prioridade: "Urgente", origem: "automatico", criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 4, atribuido_em: null, ativo: {id: 2, nome_ativo: "Totem 02"}, categoria: {id: 3, nome: "Falha de Energia"}, solicitante: {id: null, nome: null}, tecnico: {id: null, nome: null}}]
    }
  }

  test "lista atribuídos a mim" {
    input = {usuarios_id: 12, visao: "atribuidos_a_mim"}
    expect.to_equal ($response.items) {
      value = [{id: 102, titulo: "Falha atribuída", descricao: "Descrição", status: "Resolvido", prioridade: "Urgente", origem: "automatico", criado_em: 1780000001000, ultima_atualizacao_em: 1780000001000, sla_horas_aplicado: 4, atribuido_em: 1780000001000, ativo: {id: 2, nome_ativo: "Totem 02"}, categoria: {id: 3, nome: "Falha de Energia"}, solicitante: {id: null, nome: null}, tecnico: {id: 12, nome: "Técnico"}}]
    }
  }

  test "lista atribuídos a outros" {
    input = {usuarios_id: 12, visao: "atribuidos_a_outros"}
    expect.to_equal ($response.items) {
      value = [{id: 103, titulo: "Falha de outro Técnico", descricao: "Descrição", status: "Em Atendimento", prioridade: "Alta", origem: "manual", criado_em: 1780000002000, ultima_atualizacao_em: 1780000002000, sla_horas_aplicado: 2, atribuido_em: 1780000002000, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Falha de Rede"}, solicitante: {id: 8, nome: "Gerente"}, tecnico: {id: 10, nome: "Outro Técnico"}}]
    }
  }

  test "pesquisa por número" {
    input = {usuarios_id: 12, numero: "102"}
    expect.to_equal ($response.items) {
      value = [{id: 102, titulo: "Falha atribuída", descricao: "Descrição", status: "Resolvido", prioridade: "Urgente", origem: "automatico", criado_em: 1780000001000, ultima_atualizacao_em: 1780000001000, sla_horas_aplicado: 4, atribuido_em: 1780000001000, ativo: {id: 2, nome_ativo: "Totem 02"}, categoria: {id: 3, nome: "Falha de Energia"}, solicitante: {id: null, nome: null}, tecnico: {id: 12, nome: "Técnico"}}]
    }
  }

  test "visão inválida" {
    input = {usuarios_id: 12, visao: "qualquer"}
    expect.to_throw { exception = "" }
  }

  test "número inválido" {
    input = {usuarios_id: 12, numero: "abc"}
    expect.to_throw { exception = "" }
  }

  guid = "miraFilaTecnico01"
}
