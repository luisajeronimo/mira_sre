// Constrói o DTO somente leitura usado pela fila e pelo detalhe técnico.
function "service_desk/construir_dto_chamado_tecnico" {
  input {
    json registro
  }

  stack {
    var $solicitante {
      value = null
    }

    conditional {
      if ($input.registro.solicitante_usuario_id != null) {
        var.update $solicitante {
          value = {id: $input.registro.solicitante_usuario_id, nome: $input.registro.solicitante_nome}
        }
      }
    }

    var $tecnico {
      value = null
    }

    conditional {
      if ($input.registro.tecnico_usuario_id != null && $input.registro.tecnico_usuario_id != 0) {
        var.update $tecnico {
          value = {id: $input.registro.tecnico_usuario_id, nome: $input.registro.tecnico_nome}
        }
      }
    }

    var $atribuido_em {
      value = null
    }

    conditional {
      if ($input.registro.atribuido_em != null && $input.registro.atribuido_em != 0) {
        var.update $atribuido_em {
          value = $input.registro.atribuido_em
        }
      }
    }

    var $chamado {
      value = {
        id: $input.registro.id,
        titulo: $input.registro.titulo,
        descricao: $input.registro.descricao,
        status: $input.registro.status,
        prioridade: $input.registro.prioridade,
        origem: $input.registro.origem,
        criador_sistema: $input.registro.criador_sistema,
        criado_em: $input.registro.criado_em,
        sla_horas_aplicado: $input.registro.sla_horas_aplicado,
        atribuido_em: $atribuido_em,
        ativo: {id: $input.registro.ativo_id, nome_ativo: $input.registro.ativo_nome},
        categoria: {id: $input.registro.categoria_id, nome: $input.registro.categoria_nome},
        solicitante: $solicitante,
        tecnico: $tecnico
      }
    }
  }

  response = $chamado

  test "preserva tecnico e atribuido_em" {
    input = {registro: {id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: 1780000001000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: 12, tecnico_nome: "Técnico"}}
    expect.to_equal ($response.id) { value = 101 }
    expect.to_equal ($response.tecnico.id) { value = 12 }
    expect.to_equal ($response.atribuido_em) { value = 1780000001000 }
    expect.to_be_null ($response.criador_sistema)
  }

  test "preserva nulos legados" {
    input = {registro: {id: 16, titulo: "Legado", descricao: null, status: "Novo", prioridade: "Urgente", origem: null, criador_sistema: null, criado_em: null, sla_horas_aplicado: null, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 1, categoria_nome: "Totem Offline / Sem Heartbeat", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: null, tecnico_nome: null}}
    expect.to_be_null ($response.descricao)
    expect.to_be_null ($response.origem)
    expect.to_be_null ($response.criador_sistema)
    expect.to_be_null ($response.atribuido_em)
    expect.to_be_null ($response.tecnico)
  }
  guid = "0M0qt2--nIDImCR9ZlVm9E5SaWk"
}
