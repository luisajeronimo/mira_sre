// Localiza um chamado no escopo persistido da Loja do Gerente autenticado.
function "service_desk/obter_chamado_gerente_autorizado" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "autoriza chamado da loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita gerente sem loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: null}
          ```
        "rejeita chamado inexistente": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita chamado de outra loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
      }
    } as $usuario

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query chamados {
      join = {
        ativo: {
          table: "ativos_referencia"
          type: "left"
          where: $db.chamados.ativos_referencia_id == $db.ativo.id
        }
      }
      eval = {
        ativo_lojas_id: $db.ativo.lojas_id
      }
      where = $db.chamados.id == $input.chamados_id
      return = {type: "single"}
      mock = {
        "autoriza chamado da loja": ```
          {id: 101, status: "Novo", ativo_lojas_id: 1}
          ```
        "rejeita chamado inexistente": null
        "rejeita chamado de outra loja": ```
          {id: 102, status: "Novo", ativo_lojas_id: 2}
          ```
      }
    } as $registro

    precondition ($registro != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    precondition ($registro.ativo_lojas_id != null && $registro.ativo_lojas_id == $usuario.lojas_id) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
  }

  response = {id: $registro.id, status: $registro.status, autor_nome: $usuario.nome}

  test "autoriza chamado da loja" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_equal ($response.id) { value = 101 }
    expect.to_equal ($response.autor_nome) { value = "Gerente" }
  }

  test "rejeita gerente sem loja" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_throw { exception = "" }
  }

  test "rejeita chamado inexistente" {
    input = {usuarios_id: 8, chamados_id: 999}
    expect.to_throw { exception = "" }
  }

  test "rejeita chamado de outra loja" {
    input = {usuarios_id: 8, chamados_id: 102}
    expect.to_throw { exception = "" }
  }
  guid = "miraGerenteChamadoAutorizado01"
}
