// Catálogo de categorias permitidas para abertura manual.
query "gerente/categorias" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_categorias_manuais" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "z3I54EEnWj2rKRXmyTB7YvGiSg0"
}
