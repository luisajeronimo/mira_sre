// Autoatribuição atômica de chamado pelo Técnico autenticado.
query "tecnico/chamados/{chamados_id}/assumir" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/assumir_chamado_tecnico" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id}
    } as $resultado
  }

  response = $resultado
  guid = "miraAssumirTecnicoApi01"
}
