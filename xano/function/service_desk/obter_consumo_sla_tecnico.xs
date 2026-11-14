// Consulta autorizada de consumo de SLA para Técnico, Diretoria e Administrador.
function "service_desk/obter_consumo_sla_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "retorna consumo do chamado tecnico": {id: 12, role: "tecnico"},
        "rejeita perfil nao autorizado": {id: 8, role: "gerente"},
        "rejeita chamado inexistente": {id: 12, role: "tecnico"},
        "retorna consumo do chamado diretoria": {id: 12, role: "diretoria"},
        "retorna consumo do chamado administrador": {id: 12, role: "administrador"}
      }
    } as $usuario

    precondition ($usuario.role == "tecnico" || $usuario.role == "diretoria" || $usuario.role == "administrador") {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.get chamados {
      field_name = "id"
      field_value = $input.chamados_id
      mock = {
        "retorna consumo do chamado tecnico": {id: 101, status: "Em Atendimento"},
        "rejeita perfil nao autorizado": {id: 101, status: "Em Atendimento"},
        "rejeita chamado inexistente": null,
        "retorna consumo do chamado diretoria": {id: 101, status: "Em Atendimento"},
        "retorna consumo do chamado administrador": {id: 101, status: "Em Atendimento"}
      }
    } as $chamado

    conditional {
      if ($chamado == null) {
        util.set_header {
          value = "HTTP/1.1 404 Not Found"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "notfound"
          error = "Chamado não encontrado."
        }
      }
    }

    function.run "service_desk/calcular_consumo_sla_chamado" {
      input = {chamados_id: $chamado.id}
      mock = {
        "retorna consumo do chamado tecnico": {
          chamados_id: 101
          calculavel: true
          motivo: null
          consumo_ms: 7200000
          sla_horas_aplicado: 4
          fracao_consumida: 0.5
          faixa: "normal"
          estado_contagem: "em_contagem"
          calculado_em: 1780007200000
        },
        "retorna consumo do chamado diretoria": {
          chamados_id: 101
          calculavel: true
          motivo: null
          consumo_ms: 7200000
          sla_horas_aplicado: 4
          fracao_consumida: 0.5
          faixa: "normal"
          estado_contagem: "em_contagem"
          calculado_em: 1780007200000
        },
        "retorna consumo do chamado administrador": {
          chamados_id: 101
          calculavel: true
          motivo: null
          consumo_ms: 7200000
          sla_horas_aplicado: 4
          fracao_consumida: 0.5
          faixa: "normal"
          estado_contagem: "em_contagem"
          calculado_em: 1780007200000
        }
      }
    } as $consumo
  }

  response = {
    consumo_sla: $consumo
  }

  test "retorna consumo do chamado tecnico" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.consumo_sla.calculavel) { value = true }
    expect.to_equal ($response.consumo_sla.faixa) { value = "normal" }
  }

  test "rejeita chamado inexistente" {
    input = {usuarios_id: 12, chamados_id: 999}
    expect.to_throw { exception = "" }
  }


  test "retorna consumo do chamado diretoria" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.consumo_sla.faixa) { value = "normal" }
  }

  test "retorna consumo do chamado administrador" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.consumo_sla.faixa) { value = "normal" }
  }

  test "rejeita perfil nao autorizado" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  guid = "miraObterConsumoSlaTecnico01"
}
