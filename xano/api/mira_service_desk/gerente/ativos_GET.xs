// Catálogo de ativos da Loja do Gerente.
query "gerente/ativos" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_ativos_gerente" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "hjFTQuxR9qfMh82kAFzETt-323I"
}
