// Exige identidade oficial e um dos perfis autorizados pela operação.
function "autorizacao/exigir_perfil" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  
    bool gerente?
    bool tecnico?
    bool diretoria?
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
            lojas_id: 1
          }
          ```
        "nega perfil nao previsto": ```
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
  
    var $permitido {
      value = ($usuario.role == "gerente" && $input.gerente) || ($usuario.role == "tecnico" && $input.tecnico) || ($usuario.role == "diretoria" && $input.diretoria)
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

  guid = "2ervMfe4CLYElGWRo6o3Nddz26s"
}
