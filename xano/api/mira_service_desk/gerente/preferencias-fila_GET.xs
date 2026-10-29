query "gerente/preferencias-fila" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/obter_preferencia_filtros_gerente" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }
  response = $resultado
  guid = "miraPrefGerenteApiGet01"
}
