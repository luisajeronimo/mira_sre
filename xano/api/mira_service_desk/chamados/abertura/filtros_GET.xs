query "chamados/abertura/filtros" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {}
  stack {
    function.run "service_desk/catalogo_abertura_global" {
      input = {usuarios_id: $auth.id}
    } as $dados
  }
  response = $dados
  guid = "uc1EqvUiITJCXTKM-pW8VrnW6lY"
}
