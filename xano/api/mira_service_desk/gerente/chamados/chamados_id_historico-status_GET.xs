// Histórico público de status, projetado de alteracao_chamado, de chamado da Loja do Gerente.
query "gerente/chamados/{chamados_id}/historico-status" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/listar_historico_status_gerente" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id}
    } as $resultado
  }

  response = $resultado
  guid = "miraHistoricoStatusGerenteGet01"
}
