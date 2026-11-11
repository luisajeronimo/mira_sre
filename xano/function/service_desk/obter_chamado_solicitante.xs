// Detalhe somente leitura de chamado autorizado pelo vínculo de solicitante.
// Replica os campos funcionais do detalhe do Gerente, sem telemetria do Totem
// e sem identificadores de usuário em solicitante e técnico.
function "service_desk/obter_chamado_solicitante" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "service_desk/obter_chamado_solicitante_autorizado" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $input.chamados_id}
      mock = {
        "retorna detalhe sem telemetria e sem ids de usuario": {id: 101, status: "Resolvido"}
        "retorna detalhe sem tecnico"                        : {id: 102, status: "Novo"}
        "retorna loja historica diferente da atual"         : {id: 103, status: "Resolvido"}
        "retorna null sem historico com loja atual"         : {id: 104, status: "Resolvido"}
        "retorna null sem historico e sem loja atual"       : {id: 105, status: "Resolvido"}
      }
    } as $autorizado

    db.query chamados {
      join = {
        ativos_referencia: {
          table: "ativos_referencia"
          type: "left"
          where: $db.chamados.ativos_referencia_id == $db.ativos_referencia.id
        }
        categorias_servico: {
          table: "categorias_servico"
          type: "left"
          where: $db.chamados.categorias_servico_id == $db.categorias_servico.id
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
        ativo_id: $db.ativos_referencia.id
        ativo_nome: $db.ativos_referencia.nome_ativo
        categoria_id: $db.categorias_servico.id
        categoria_nome: $db.categorias_servico.nome
        solicitante_usuario_id: $db.solicitante.id
        solicitante_nome: $db.solicitante.nome
        tecnico_usuario_id: $db.tecnico.id
        tecnico_nome: $db.tecnico.nome
      }
      where = $db.chamados.id == $autorizado.id
      return = {type: "single"}
      mock = {
        "retorna detalhe sem telemetria e sem ids de usuario": {id: 101, titulo: "Falha", descricao: "Totem não conecta", status: "Resolvido", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000005000, sla_horas_aplicado: 2, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: 12, tecnico_nome: "Técnico"}
        "retorna detalhe sem tecnico"                        : {id: 102, titulo: "Impressora", descricao: null, status: "Novo", prioridade: "Média", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 4, ativo_id: 3, ativo_nome: "Totem 03", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
        "retorna loja historica diferente da atual"         : {id: 103, titulo: "Falha", descricao: "Totem transferido", status: "Resolvido", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000005000, sla_horas_aplicado: 2, ativo_id: 3, ativo_nome: "Totem 03", ativo_lojas_id: 2, categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
        "retorna null sem historico com loja atual"         : {id: 104, titulo: "Falha legada", descricao: null, status: "Resolvido", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000005000, sla_horas_aplicado: 2, ativo_id: 4, ativo_nome: "Totem 04", ativo_lojas_id: 1, categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
        "retorna null sem historico e sem loja atual"       : {id: 105, titulo: "Falha legada", descricao: null, status: "Resolvido", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000005000, sla_horas_aplicado: 2, ativo_id: 5, ativo_nome: "Totem 05", ativo_lojas_id: null, categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
      }
    } as $registro

    precondition ($registro != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    // Mesma regra do detalhe do Gerente: Loja do Totem no instante do chamado.
    function.run "administracao/resolver_loja_totem_no_instante" {
      input = {
        ativos_referencia_id: $registro.ativo_id
        instante            : $registro.criado_em
      }
      mock = {
        "retorna detalhe sem telemetria e sem ids de usuario": {lojas_id: 1}
        "retorna detalhe sem tecnico"                        : {lojas_id: null}
        "retorna loja historica diferente da atual"         : {lojas_id: 1}
        "retorna null sem historico com loja atual"         : {lojas_id: null}
        "retorna null sem historico e sem loja atual"       : {lojas_id: null}
      }
    } as $historico

    var $loja {
      value = null
    }

    conditional {
      if ($historico.lojas_id != null) {
        db.get lojas {
          field_name = "id"
          field_value = $historico.lojas_id
          mock = {
            "retorna detalhe sem telemetria e sem ids de usuario": {id: 1, nome: "Loja Centro"}
            "retorna loja historica diferente da atual"         : {id: 1, nome: "Loja Centro"}
          }
        } as $loja_historica

        conditional {
          if ($loja_historica != null) {
            var.update $loja {
              value = {id: $loja_historica.id, nome: $loja_historica.nome}
            }
          }
        }
      }
    }

    var $solicitante {
      value = null
    }

    conditional {
      if ($registro.solicitante_usuario_id != null) {
        var.update $solicitante {
          value = {nome: $registro.solicitante_nome}
        }
      }
    }

    var $tecnico {
      value = null
    }

    conditional {
      if ($registro.tecnico_usuario_id != null) {
        var.update $tecnico {
          value = {nome: $registro.tecnico_nome}
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
        criador_sistema: $registro.criador_sistema,
        criado_em: $registro.criado_em,
        ultima_atualizacao_em: $registro.ultima_atualizacao_em,
        ativo: {id: $registro.ativo_id, nome_ativo: $registro.ativo_nome},
        categoria: {id: $registro.categoria_id, nome: $registro.categoria_nome},
        solicitante: $solicitante,
        tecnico: $tecnico,
        loja: $loja,
        resumo_totem: null
      }
    }
  }

  response = {chamado: $chamado}

  test "retorna detalhe sem telemetria e sem ids de usuario" {
    input = {usuarios_id: 8, chamados_id: 101}

    expect.to_equal ($response.chamado.id) {
      value = 101
    }

    expect.to_be_null ($response.chamado.resumo_totem)

    expect.to_equal ($response.chamado.solicitante) {
      value = {nome: "Gerente"}
    }

    expect.to_equal ($response.chamado.tecnico) {
      value = {nome: "Técnico"}
    }

    expect.to_equal ($response.chamado.loja) {
      value = {id: 1, nome: "Loja Centro"}
    }
  }

  test "retorna detalhe sem tecnico" {
    input = {usuarios_id: 8, chamados_id: 102}

    expect.to_be_null ($response.chamado.tecnico)

    expect.to_be_null ($response.chamado.loja)
  }

  test "retorna loja historica diferente da atual" {
    input = {usuarios_id: 8, chamados_id: 103}

    expect.to_equal ($response.chamado.loja) {
      value = {id: 1, nome: "Loja Centro"}
    }
  }

  test "retorna null sem historico com loja atual" {
    input = {usuarios_id: 8, chamados_id: 104}

    expect.to_be_null ($response.chamado.loja)
  }

  test "retorna null sem historico e sem loja atual" {
    input = {usuarios_id: 8, chamados_id: 105}

    expect.to_be_null ($response.chamado.loja)
  }

  guid = "miraChamadoSolicitante01"
}
