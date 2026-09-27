// Retorna o detalhe funcional de um chamado autorizado pela Loja.
function "service_desk/obter_chamado_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }

    int chamados_id
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "retorna detalhe da loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "retorna detalhe legado": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita chamado inexistente": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita chamado de outra loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita chamado sem ativo autorizavel": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
      }
    } as $usuario

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
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
        ativo_lojas_id: $db.ativo.lojas_id
        categoria_id: $db.categoria.id
        categoria_nome: $db.categoria.nome
        solicitante_usuario_id: $db.solicitante.id
        solicitante_nome: $db.solicitante.nome
        tecnico_usuario_id: $db.tecnico.id
        tecnico_nome: $db.tecnico.nome
      }
      where = $db.chamados.id == $input.chamados_id
      return = {type: "single"}
      mock = {
        "retorna detalhe da loja": ```
          {id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, sla_horas_aplicado: 2, ativo_id: 1, ativo_nome: "Totem 01", ativo_lojas_id: 1, categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
          ```
        "retorna detalhe legado": ```
          {id: 16, titulo: "Legado", descricao: null, status: "Novo", prioridade: "Urgente", origem: null, criado_em: null, sla_horas_aplicado: null, ativo_id: 1, ativo_nome: "Totem 01", ativo_lojas_id: 1, categoria_id: 1, categoria_nome: "Totem Offline / Sem Heartbeat", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: null, tecnico_nome: null}
          ```
        "rejeita chamado inexistente": null
        "rejeita chamado de outra loja": ```
          {id: 102, ativo_id: 8, ativo_nome: "Totem 08", ativo_lojas_id: 2}
          ```
        "rejeita chamado sem ativo autorizavel": ```
          {id: 103, ativo_id: null, ativo_nome: null, ativo_lojas_id: null}
          ```
      }
    } as $registro

    precondition ($registro != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    precondition ($registro.ativo_lojas_id != null && $registro.ativo_lojas_id == $usuario.lojas_id) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    var $solicitante {
      value = null
    }

    conditional {
      if ($registro.solicitante_usuario_id != null) {
        var.update $solicitante {
          value = {id: $registro.solicitante_usuario_id, nome: $registro.solicitante_nome}
        }
      }
    }

    var $tecnico {
      value = null
    }

    conditional {
      if ($registro.tecnico_usuario_id != null) {
        var.update $tecnico {
          value = {id: $registro.tecnico_usuario_id, nome: $registro.tecnico_nome}
        }
      }
    }

    var $chamado {
      value = {
        id: $registro.id,
        titulo: $registro.titulo,
        descricao: $registro.descricao,
        status: $registro.status,
        prioridade: $registro.prioridade,
        origem: $registro.origem,
        criado_em: $registro.criado_em,
        sla_horas_aplicado: $registro.sla_horas_aplicado,
        ativo: {id: $registro.ativo_id, nome_ativo: $registro.ativo_nome},
        categoria: {id: $registro.categoria_id, nome: $registro.categoria_nome},
        solicitante: $solicitante,
        tecnico: $tecnico
      }
    }
  }

  response = {chamado: $chamado}

  test "retorna detalhe da loja" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_equal ($response.chamado.id) { value = 101 }
    expect.to_equal ($response.chamado.solicitante.id) { value = 8 }
    expect.to_be_null ($response.chamado.tecnico)
    expect.to_not_be_defined ($response.chamado.created_at)
  }

  test "retorna detalhe legado" {
    input = {usuarios_id: 8, chamados_id: 16}
    expect.to_be_null ($response.chamado.descricao)
    expect.to_be_null ($response.chamado.origem)
    expect.to_be_null ($response.chamado.sla_horas_aplicado)
  }

  test "rejeita chamado inexistente" {
    input = {usuarios_id: 8, chamados_id: 999}
    expect.to_throw { exception = "" }
  }

  test "rejeita chamado de outra loja" {
    input = {usuarios_id: 8, chamados_id: 102}
    expect.to_throw { exception = "" }
  }

  test "rejeita chamado sem ativo autorizavel" {
    input = {usuarios_id: 8, chamados_id: 103}
    expect.to_throw { exception = "" }
  }
  guid = "SDxf7t8lCf5IwjBf3TnELdgGnm0"
}
