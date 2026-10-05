// Exige identidade oficial e um dos perfis autorizados pela operação.
function "autorizacao/exigir_perfil" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  
    bool gerente?
    bool tecnico?
    bool diretoria?
    bool administrador?
  }

  stack {
    function.run "autorizacao/obter_identidade" {
      input = {usuarios_id: $input.usuarios_id}
      mock = {
        "autoriza perfil previsto": ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            lojas_id: 1,
            deve_trocar_senha: false
          }
          ```
        "nega perfil nao previsto": ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            lojas_id: 1,
            deve_trocar_senha: false
          }
          ```
        "lista opcoes para administrador concluido": ```
          {
            id: 12,
            nome: "Administradora",
            email: "admin@example.test",
            role: "administrador",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "bloqueia administrador pendente": ```
          {
            id: 12,
            nome: "Administradora",
            email: "admin@example.test",
            role: "administrador",
            lojas_id: null,
            deve_trocar_senha: true
          }
          ```
        "bloqueia gerente": ```
          {
            id: 8,
            nome: "Gerente",
            email: "gerente@example.test",
            role: "gerente",
            lojas_id: 1,
            deve_trocar_senha: false
          }
          ```
        "bloqueia tecnico": ```
          {
            id: 3,
            nome: "Técnico",
            email: "tecnico@example.test",
            role: "tecnico",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "bloqueia diretoria": ```
          {
            id: 4,
            nome: "Diretoria",
            email: "diretoria@example.test",
            role: "diretoria",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "exigir perfil administrador concluido": ```
          {
            id: 12,
            nome: "Administradora",
            email: "admin@example.test",
            role: "administrador",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "exigir perfil administrador pendente": ```
          {
            id: 12,
            nome: "Administradora",
            email: "admin@example.test",
            role: "administrador",
            lojas_id: null,
            deve_trocar_senha: true
          }
          ```
        "exigir perfil bloqueia gerente": ```
          {
            id: 8,
            nome: "Gerente",
            email: "gerente@example.test",
            role: "gerente",
            lojas_id: 1,
            deve_trocar_senha: false
          }
          ```
        "exigir perfil bloqueia tecnico": ```
          {
            id: 3,
            nome: "Técnico",
            email: "tecnico@example.test",
            role: "tecnico",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "exigir perfil bloqueia diretoria": ```
          {
            id: 4,
            nome: "Diretoria",
            email: "diretoria@example.test",
            role: "diretoria",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
      }
    } as $usuario
  
    var $permitido {
      value = ($usuario.role == "gerente" && $input.gerente) || ($usuario.role == "tecnico" && $input.tecnico) || ($usuario.role == "diretoria" && $input.diretoria) || ($usuario.role == "administrador" && $input.administrador)
    }

    // Toda operação humana funcional passa por este gate. /me usa somente
    // obter_identidade e a troca de senha é uma exceção explícita.
    precondition ($usuario.deve_trocar_senha != true) {
      error_type = "accessdenied"
      error = "Troca de senha obrigatória."
    }
  
    precondition ($permitido) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  }

  response = $usuario

  test "autoriza perfil previsto" {
    input = {usuarios_id: 8, gerente: true}
  
    expect.to_equal ($response.role) {
      value = "gerente"
    }
  }

  test "nega perfil nao previsto" {
    input = {usuarios_id: 8, tecnico: true}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "exigir perfil administrador concluido" {
    input = {usuarios_id: 12, administrador: true}

    expect.to_equal ($response.role) {
      value = "administrador"
    }
  }

  test "exigir perfil administrador pendente" {
    input = {usuarios_id: 12, administrador: true}

    expect.to_throw {
      exception = ""
    }
  }

  test "exigir perfil bloqueia gerente" {
    input = {usuarios_id: 8, administrador: true}

    expect.to_throw {
      exception = ""
    }
  }

  test "exigir perfil bloqueia tecnico" {
    input = {usuarios_id: 3, administrador: true}

    expect.to_throw {
      exception = ""
    }
  }

  test "exigir perfil bloqueia diretoria" {
    input = {usuarios_id: 4, administrador: true}

    expect.to_throw {
      exception = ""
    }
  }

  guid = "2ervMfe4CLYElGWRo6o3Nddz26s"
}
