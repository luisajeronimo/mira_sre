// Histórico público de status de chamado autorizado pelo vínculo de solicitante.
function "service_desk/listar_historico_status_solicitante" {
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
        "delega projecao apos vinculo": {id: 101, status: "Resolvido"}
      }
    } as $chamado

    function.run "service_desk/listar_historico_status" {
      input = {chamados_id: $chamado.id}
      mock = {
        "delega projecao apos vinculo": {items: []}
      }
    } as $historico
  }

  response = $historico

  test "delega projecao apos vinculo" {
    input = {usuarios_id: 8, chamados_id: 101}

    expect.to_be_empty ($response.items)
  }

  guid = "miraHistoricoStatusSolicitante01"
}
