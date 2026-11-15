query "monitoramento/ativos/{ativos_referencia_id}/retomar-telemetria" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    int ativos_referencia_id filters=min:1
  }
  stack {
    function.run "service_desk/retomar_telemetria" {
      input = {usuarios_id: $auth.id, ativos_referencia_id: $input.ativos_referencia_id}
    } as $resultado
    conditional {
      if (!$resultado.envio_autorizado) {
        util.set_header {
          value = "HTTP/1.1 409 Conflict"
          duplicates = "replace"
        }
      }
    }
  }
  response = $resultado
  guid = "miraRetomarTelemetriaEndpoint01"
}
