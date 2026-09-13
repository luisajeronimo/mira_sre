// Get usuarios record
query "usuarios/{usuarios_id}" verb=GET {
  api_group = "APIS from table usuarios"
  auth = "usuarios"

  input {
    int usuarios_id? filters=min:1
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id}
    } as $usuario
  }

  response = null
  guid = "thpfgOhOsJpq14P5RZVZUQYPbKw"
}
