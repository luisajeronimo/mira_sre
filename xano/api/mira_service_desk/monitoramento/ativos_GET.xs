// Consulta global de Totens para monitoramento; Gerente não recebe este contrato.
query "monitoramento/ativos" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_ativos_monitoramento" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "wP1hYdUyg3Lw8Q22S3cCPhyHhro"
}
