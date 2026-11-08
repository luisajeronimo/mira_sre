// Consulta administrativa sem material de credencial.
query "administracao/usuarios" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador
    db.query usuarios {
      sort = {usuarios.nome: "asc"}
      return = {type: "list"}
    } as $usuarios
    var $items {
      value = $usuarios|map:{
        id: $$.id,
        nome: $$.nome,
        email: $$.email,
        role: $$.role,
        lojas_id: $$.lojas_id
      }
    }
  }

  response = {items: $items}
  guid = "admin-usuarios-listar-1b9fd07d"
}
