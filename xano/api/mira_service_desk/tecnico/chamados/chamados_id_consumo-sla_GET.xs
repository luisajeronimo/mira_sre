// Exposição do consumo de SLA do chamado para Técnico e Administrador (DE-8).
query "tecnico/chamados/{chamados_id}/consumo-sla" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/obter_consumo_sla_tecnico" {
      input = {
        usuarios_id: $auth.id
        chamados_id: $input.chamados_id
      }
    } as $resultado
  }

  response = $resultado
  guid = "miraConsumoSlaTecnicoEndpoint01"
}
