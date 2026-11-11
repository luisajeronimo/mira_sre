// Consulta autorizada de consumo de SLA de chamado da Loja histórica do Gerente (DE-8).
function "service_desk/obter_consumo_sla_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "service_desk/obter_chamado_gerente_autorizado" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $input.chamados_id}
      mock = {
        "retorna consumo do chamado": {id: 101, status: "Em Atendimento", autor_nome: "Gerente"}
      }
    } as $chamado

    function.run "service_desk/calcular_consumo_sla_chamado" {
      input = {chamados_id: $chamado.id}
      mock = {
        "retorna consumo do chamado": {
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

  test "retorna consumo do chamado" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_equal ($response.consumo_sla.calculavel) { value = true }
    expect.to_equal ($response.consumo_sla.faixa) { value = "normal" }
  }

  guid = "miraObterConsumoSlaGerente01"
}
