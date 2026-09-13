// Query all usuarios records
query usuarios verb=GET {
  api_group = "APIS from table usuarios"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id}
    } as $usuario
  }

  response = null
  guid = "blh5xYoTaTXrXx_b5bOn7XJ7ATs"
}
