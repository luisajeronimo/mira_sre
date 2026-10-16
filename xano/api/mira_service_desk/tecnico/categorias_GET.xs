// Catálogo de categorias ativas para a edição operacional global.
query "tecnico/categorias" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_categorias_tratativa" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "miraCategoriasTratativaApi01"
}
