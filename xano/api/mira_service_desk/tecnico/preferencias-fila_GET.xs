query "tecnico/preferencias-fila" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    text escopo filters=trim
  }
  stack {
    function.run "service_desk/obter_preferencia_fila_tecnica" {
      input = {usuarios_id: $auth.id, escopo: $input.escopo}
    } as $resultado
  }
  response = $resultado
  guid = "miraPrefFilaGet01"
}
