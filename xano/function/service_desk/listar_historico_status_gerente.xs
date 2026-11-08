// Histórico público de status de chamado autorizado pela Loja do Gerente.
function "service_desk/listar_historico_status_gerente" {
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
        "delega projecao apos autorizar": {id: 101, status: "Resolvido", autor_nome: "Gerente"}
      }
    } as $chamado

    function.run "service_desk/listar_historico_status" {
      input = {chamados_id: $chamado.id}
      mock = {
        "delega projecao apos autorizar": {items: [{id: 30, status_anterior: "Em Atendimento", status_resultante: "Resolvido", criado_em: 1780000005000, autor: {nome: "Técnico", perfil: "Técnico"}}]}
      }
    } as $historico
  }

  response = $historico

  test "delega projecao apos autorizar" {
    input = {usuarios_id: 8, chamados_id: 101}

    expect.to_equal ($response.items) {
      value = [{id: 30, status_anterior: "Em Atendimento", status_resultante: "Resolvido", criado_em: 1780000005000, autor: {nome: "Técnico", perfil: "Técnico"}}]
    }
  }

  guid = "miraHistoricoStatusGerente01"
}
