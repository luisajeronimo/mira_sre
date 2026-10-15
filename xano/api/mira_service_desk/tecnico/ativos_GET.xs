// Catálogo global de ativos para os filtros da fila técnica.
query "tecnico/ativos" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_ativos_tecnico" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "zHibXlyDgs1Qkcqyw8BhT6zlh-k"
}
