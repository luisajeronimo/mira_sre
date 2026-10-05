// Valida dados administrativos de criação sem persistir registros.
function "administracao/validar_criacao_usuario" {
  input {
    email email
    text role filters=trim
    int? lojas_id?
  }

  stack {
    var $perfil_valido {
      value = ($input.role == "gerente" || $input.role == "tecnico" || $input.role == "diretoria" || $input.role == "administrador")
    }

    precondition ($perfil_valido) {
      error_type = "inputerror"
      error = "Perfil inválido."
    }

    var $loja_obrigatoria {
      value = $input.role == "gerente"
    }

    precondition ((!$loja_obrigatoria && $input.lojas_id == null) || ($loja_obrigatoria && $input.lojas_id != null)) {
      error_type = "inputerror"
      error = "Loja incompatível com o perfil informado."
    }

    db.query usuarios {
      where = $db.usuarios.email == $input.email
      return = {type: "single"}
      mock = {
        "aceita gerente com loja existente": null
        "aceita tecnico sem loja": null
        "aceita diretoria sem loja": null
        "aceita administrador sem loja": null
        "rejeita gerente loja inexistente": null
        "rejeita email duplicado": {id: 24, email: "existente@example.test"}
      }
    } as $email_existente

    precondition ($email_existente == null) {
      error_type = "inputerror"
      error = "E-mail já cadastrado."
    }

    conditional {
      if ($loja_obrigatoria) {
        db.get lojas {
          field_name = "id"
          field_value = $input.lojas_id
          mock = {
            "aceita gerente com loja existente": {id: 1, nome: "Loja Paulista"}
            "rejeita gerente loja inexistente": null
          }
        } as $loja

        precondition ($loja != null) {
          error_type = "inputerror"
          error = "Loja não encontrada."
        }
      }
    }

    var $validacao {
      value = {valid: true}
    }
  }

  response = $validacao

  test "aceita gerente com loja existente" {
    input = {email: "gerente@example.test", role: "gerente", lojas_id: 1}

    expect.to_be_true ($response.valid)
  }

  test "aceita tecnico sem loja" {
    input = {email: "tecnico@example.test", role: "tecnico", lojas_id: null}

    expect.to_be_true ($response.valid)
  }

  test "aceita diretoria sem loja" {
    input = {email: "diretoria@example.test", role: "diretoria", lojas_id: null}

    expect.to_be_true ($response.valid)
  }

  test "aceita administrador sem loja" {
    input = {email: "administrador@example.test", role: "administrador", lojas_id: null}

    expect.to_be_true ($response.valid)
  }

  test "rejeita perfil admin legado" {
    input = {email: "legado@example.test", role: "admin", lojas_id: null}

    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita gerente sem loja" {
    input = {email: "gerente@example.test", role: "gerente", lojas_id: null}

    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita gerente loja inexistente" {
    input = {email: "gerente@example.test", role: "gerente", lojas_id: 999}

    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita tecnico com loja" {
    input = {email: "tecnico@example.test", role: "tecnico", lojas_id: 1}

    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita diretoria com loja" {
    input = {email: "diretoria@example.test", role: "diretoria", lojas_id: 1}

    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita administrador com loja" {
    input = {email: "administrador@example.test", role: "administrador", lojas_id: 1}

    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita email duplicado" {
    input = {email: "existente@example.test", role: "tecnico", lojas_id: null}

    expect.to_throw {
      exception = ""
    }
  }

  guid = "gc_eOhWvNVsZIh8Z_PzvwrYQNmw"
}
