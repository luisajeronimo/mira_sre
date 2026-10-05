// Obtém somente os dados públicos de uma identidade com perfil oficial.
function "autorizacao/obter_identidade" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    db.get usuarios {
      field_name = "id"
      field_value = $input.usuarios_id
      mock = {
        "retorna identidade de gerente": ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            senha: "nao-retornar",
            lojas_id: 1
          }
          ```
        "rejeita perfil nao oficial"   : ```
          {
            id: 99,
            nome: "Perfil legado",
            email: "legado@example.test",
            role: "tecnico_n1",
            senha: "nao-retornar",
            lojas_id: null
          }
          ```
        "rejeita admin"                : ```
          {
            id: 90,
            role: "admin"
          }
          ```
        "rejeita tecnico n2"           : ```
          {
            id: 91,
            role: "tecnico_n2"
          }
          ```
        "rejeita tecnico n3"           : ```
          {
            id: 92,
            role: "tecnico_n3"
          }
          ```
        "rejeita diretor"              : ```
          {
            id: 93,
            role: "diretor"
          }
          ```
        "rejeita perfil desconhecido"  : ```
          {
            id: 94,
            role: "desconhecido"
          }
          ```
        "retorna identidade administrador pendente": ```
          {
            id: 12,
            nome: "Administradora",
            email: "admin@example.test",
            role: "administrador",
            lojas_id: null,
            deve_trocar_senha: true,
            senha: "nao-retornar"
          }
          ```
      }
    } as $usuario
  
    precondition ($usuario != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  
    var $perfil_oficial {
      value = ($usuario.role == "gerente" || $usuario.role == "tecnico" || $usuario.role == "diretoria" || $usuario.role == "administrador")
    }
  
    precondition ($perfil_oficial) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  
    var $lojas_id {
      value = null
    }
  
    conditional {
      if ($usuario.role == "gerente") {
        var.update $lojas_id {
          value = $usuario.lojas_id
        }
      }
    }
  
    var $identidade {
      value = {
        id      : $usuario.id
        nome    : $usuario.nome
        email   : $usuario.email
        role    : $usuario.role
        lojas_id: $lojas_id
        deve_trocar_senha: $usuario.deve_trocar_senha
      }
    }
  }

  response = $identidade

  test "retorna identidade de gerente" {
    input = {usuarios_id: 8}
  
    expect.to_equal ($response.id) {
      value = 8
    }
  
    expect.to_equal ($response.role) {
      value = "gerente"
    }
  
    expect.to_equal ($response.lojas_id) {
      value = 1
    }
  
    expect.to_not_be_defined ($response.senha)
  }

  test "rejeita perfil nao oficial" {
    input = {usuarios_id: 99}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita admin" {
    input = {usuarios_id: 90}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita tecnico n2" {
    input = {usuarios_id: 91}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita tecnico n3" {
    input = {usuarios_id: 92}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita diretor" {
    input = {usuarios_id: 93}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita perfil desconhecido" {
    input = {usuarios_id: 94}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "retorna identidade administrador pendente" {
    input = {usuarios_id: 12}

    expect.to_equal ($response.role) {
      value = "administrador"
    }

    expect.to_be_true ($response.deve_trocar_senha)
    expect.to_be_null ($response.lojas_id)
    expect.to_not_be_defined ($response.senha)
  }

  guid = "6Ic54j6lFL7p2rhQsV-M9MUI4Rc"
}
