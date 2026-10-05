// Autoriza a Loja do Gerente ou a consulta global explicitamente permitida.
function "autorizacao/exigir_escopo_loja" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  
    int? lojas_id
    bool tecnico?
    bool diretoria?
  }

  stack {
    function.run "autorizacao/obter_identidade" {
      input = {usuarios_id: $input.usuarios_id}
      mock = {
        "autoriza loja do gerente"          : ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            lojas_id: 1,
            deve_trocar_senha: false
          }
          ```
        "nega outra loja ao gerente"        : ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            lojas_id: 1,
            deve_trocar_senha: false
          }
          ```
        "nega gerente sem loja"             : ```
          {
            id: 8,
            nome: "Thiago Pereira",
            email: "thiago@example.test",
            role: "gerente",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "autoriza loja da segunda gerente"  : ```
          {
            id: 10,
            nome: "Isabelly Garcia",
            email: "isabelly@example.test",
            role: "gerente",
            lojas_id: 2,
            deve_trocar_senha: false
          }
          ```
        "isola lojas entre gerentes"        : ```
          {
            id: 10,
            nome: "Isabelly Garcia",
            email: "isabelly@example.test",
            role: "gerente",
            lojas_id: 2,
            deve_trocar_senha: false
          }
          ```
        "autoriza tecnico quando previsto"  : ```
          {
            id: 1,
            nome: "Técnico",
            email: "tecnico@example.test",
            role: "tecnico",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
        "autoriza diretoria quando prevista": ```
          {
            id: 2,
            nome: "Diretoria",
            email: "diretoria@example.test",
            role: "diretoria",
            lojas_id: null,
            deve_trocar_senha: false
          }
          ```
      }
    } as $usuario

    precondition ($usuario.deve_trocar_senha != true) {
      error_type = "accessdenied"
      error = "Troca de senha obrigatória."
    }
  
    var $permitido {
      value = ($usuario.role == "gerente" && $usuario.lojas_id != null && $input.lojas_id != null && $usuario.lojas_id == $input.lojas_id) || ($usuario.role == "tecnico" && $input.tecnico) || ($usuario.role == "diretoria" && $input.diretoria)
    }
  
    precondition ($permitido) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  }

  response = $usuario

  test "autoriza loja do gerente" {
    input = {usuarios_id: 8, lojas_id: 1}
  
    expect.to_equal ($response.lojas_id) {
      value = 1
    }
  }

  test "nega outra loja ao gerente" {
    input = {usuarios_id: 8, lojas_id: 2}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "nega gerente sem loja" {
    input = {usuarios_id: 8, lojas_id: 1}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "autoriza loja da segunda gerente" {
    input = {usuarios_id: 10, lojas_id: 2}
  
    expect.to_equal ($response.lojas_id) {
      value = 2
    }
  }

  test "isola lojas entre gerentes" {
    input = {usuarios_id: 10, lojas_id: 1}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "autoriza tecnico quando previsto" {
    input = {usuarios_id: 1, lojas_id: null, tecnico: true}
  
    expect.to_equal ($response.role) {
      value = "tecnico"
    }
  }

  test "autoriza diretoria quando prevista" {
    input = {usuarios_id: 2, lojas_id: null, diretoria: true}
  
    expect.to_equal ($response.role) {
      value = "diretoria"
    }
  }

  guid = "8RkIpuYOBlIun3fpt4Zu236YbaY"
}
