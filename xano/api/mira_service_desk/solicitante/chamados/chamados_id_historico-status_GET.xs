// Histórico público de status de chamado em que o usuário autenticado é solicitante.
query "solicitante/chamados/{chamados_id}/historico-status" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/listar_historico_status_solicitante" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id}
    } as $resultado
  }

  response = $resultado
  guid = "miraHistoricoStatusSolicitanteGet01"
}
