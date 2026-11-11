// Lista somente leitura dos chamados em que o usuário autenticado é solicitante.
query "solicitante/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_chamados_solicitante" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "miraChamadosSolicitanteGet01"
}
