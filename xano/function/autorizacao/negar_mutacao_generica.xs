// Nega mutações CRUD genéricas para todos os perfis oficiais.
function "autorizacao/negar_mutacao_generica" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/obter_identidade" {
      input = {usuarios_id: $input.usuarios_id}
      mock = {
        "nega mutacao a perfil oficial": ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            lojas_id: 1
          }
          ```
      }
    } as $usuario
  
    precondition (false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  }

  response = null

  test "nega mutacao a perfil oficial" {
    input = {usuarios_id: 8}
  
    expect.to_throw {
      exception = ""
    }
  }

  guid = "NPx7HQseGLoMruOsNBAOC-IGrpM"
}
