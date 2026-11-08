// Detalhe somente leitura de chamado em que o usuário autenticado é solicitante.
query "solicitante/chamados/{chamados_id}" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/obter_chamado_solicitante" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id}
    } as $resultado
  }

  response = $resultado
  guid = "miraChamadoSolicitanteGet01"
}
