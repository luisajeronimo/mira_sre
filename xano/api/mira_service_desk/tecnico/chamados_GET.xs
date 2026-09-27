// Fila técnica com as duas visões aprovadas.
query "tecnico/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    text visao? filters=trim
  }

  stack {
    function.run "service_desk/listar_chamados_tecnico" {
      input = {usuarios_id: $auth.id, visao: $input.visao}
    } as $resultado
  }

  response = $resultado
  guid = "miraFilaTecnicoApi01"
}
