// Retorna opções mínimas de Loja após autenticação e autorização central.
function "administracao/listar_opcoes_lojas" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, administrador: true}
    } as $administrador

    db.query lojas {
      sort = {lojas.nome: "asc"}
      return = {type: "list"}
      mock = {
        "lista opcoes para administrador concluido": ```
          [{id: 1, nome: "Loja Paulista", endereco: "Uso interno no teste", status: "ativa"}]
          ```
      }
    } as $lojas

    var $opcoes {
      value = $lojas|map:{
        id: $$.id,
        nome: $$.nome
      }
    }
  }

  response = {lojas: $opcoes}

  test "lista opcoes para administrador concluido" {
    input = {usuarios_id: 12}

    expect.to_equal ($response.lojas) {
      value = [{id: 1, nome: "Loja Paulista"}]
    }
  }

  test "bloqueia administrador pendente" {
    input = {usuarios_id: 12}

    expect.to_throw {
      exception = ""
    }
  }

  test "bloqueia gerente" {
    input = {usuarios_id: 8}

    expect.to_throw {
      exception = ""
    }
  }

  test "bloqueia tecnico" {
    input = {usuarios_id: 3}

    expect.to_throw {
      exception = ""
    }
  }

  test "bloqueia diretoria" {
    input = {usuarios_id: 4}

    expect.to_throw {
      exception = ""
    }
  }
  guid = "Gd5IMxUpBN6H_0tggZTzLkC7aC0"
}
