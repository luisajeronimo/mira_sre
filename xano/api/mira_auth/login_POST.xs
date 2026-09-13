// Autentica um usuário com perfil oficial.
query login verb=POST {
  api_group = "MIRA Auth"

  input {
    email email filters=trim|lower
    text senha {
      sensitive = true
    }
  }

  stack {
    db.query usuarios {
      where = $db.usuarios.email == $input.email
      return = {type: "single"}
      mock = {
        "aceita credenciais validas" : ```
          {
            id: 8,
            role: "gerente",
            senha: "hash-teste"
          }
          ```
        "rejeita senha incorreta"    : ```
          {
            id: 8,
            role: "gerente",
            senha: "hash-teste"
          }
          ```
        "rejeita usuario inexistente": null
        "rejeita perfil nao oficial" : ```
          {
            id: 99,
            role: "tecnico_n1",
            senha: "hash-teste"
          }
          ```
      }
    } as $usuario
  
    var $autenticado {
      value = false
    }
  
    conditional {
      if ($usuario != null) {
        security.check_password {
          text_password = $input.senha
          hash_password = $usuario.senha
          mock = {
            "aceita credenciais validas": true
            "rejeita senha incorreta"   : false
            "rejeita perfil nao oficial": true
          }
        } as $senha_valida
      
        var $perfil_oficial {
          value = ($usuario.role == "gerente" || $usuario.role == "tecnico" || $usuario.role == "diretoria")
        }
      
        conditional {
          if ($senha_valida && $perfil_oficial) {
            security.create_auth_token {
              table = "usuarios"
              extras = {}
              expiration = 28800
              id = $usuario.id
            } as $auth_token
          
            var.update $autenticado {
              value = true
            }
          }
        }
      }
    }
  
    precondition ($autenticado) {
      error_type = "accessdenied"
      error = "Credenciais inválidas."
    }
  }

  response = {authToken: $auth_token}

  test "aceita credenciais validas" {
    input = {email: "thiago@example.test", senha: "senha-teste"}
  
    expect.to_be_defined ($response.authToken)
    expect.to_not_be_defined ($response.senha)
  }

  test "rejeita senha incorreta" {
    input = {
      email: "thiago@example.test"
      senha: "senha-incorreta"
    }
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita usuario inexistente" {
    input = {
      email: "inexistente@example.test"
      senha: "senha-teste"
    }
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita perfil nao oficial" {
    input = {email: "legado@example.test", senha: "senha-teste"}
  
    expect.to_throw {
      exception = ""
    }
  }

  guid = "qVbnFOctDmZW2NZagunm7FNdVT4"
}
