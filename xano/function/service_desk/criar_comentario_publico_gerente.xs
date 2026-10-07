// Cria comentário público autorizado e atualiza o chamado na mesma transação.
function "service_desk/criar_comentario_publico_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
    text conteudo? filters=trim
  }

  stack {
    function.run "service_desk/obter_chamado_gerente_autorizado" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $input.chamados_id}
      mock = {
        "cria comentario publico": {id: 101, status: "Novo", autor_nome: "Gerente"}
        "rejeita conteudo vazio": {id: 101, status: "Novo", autor_nome: "Gerente"}
        "rejeita encerrado": {id: 101, status: "Encerrado", autor_nome: "Gerente"}
        "rejeita cancelado": {id: 101, status: "Cancelado", autor_nome: "Gerente"}
      }
    } as $chamado

    conditional {
      if ($input.conteudo == null || $input.conteudo == "") {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Entrada inválida."
        }
      }
    }

    conditional {
      if ($chamado.status == "Encerrado" || $chamado.status == "Cancelado") {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Chamado não aceita novos comentários."
        }
      }
    }

    var $criado_em {
      value = now
      mock = {"cria comentario publico": 1780000002000}
    }

    var $novo_comentario {
      value = null
    }

    db.transaction {
      stack {
        db.add interacoes_chamado {
          data = {
            mensagem: $input.conteudo
            criado_em: $criado_em
            visibilidade: "publica"
            chamados_id: $chamado.id
            usuarios_id: $input.usuarios_id
          }
          mock = {
            "cria comentario publico": {id: 12, mensagem: "Comentário público", criado_em: 1780000002000, visibilidade: "publica", chamados_id: 101, usuarios_id: 8}
          }
        } as $comentario_criado

        db.edit chamados {
          field_name = "id"
          field_value = $chamado.id
          data = {ultima_atualizacao_em: $criado_em}
          mock = {
            "cria comentario publico": {id: 101, ultima_atualizacao_em: 1780000002000}
          }
        } as $chamado_atualizado

        var.update $novo_comentario {
          value = $comentario_criado
        }
      }
    }

    var $autor {
      value = null
    }

    conditional {
      if ($chamado.autor_nome != null && $chamado.autor_nome != "") {
        var.update $autor {
          value = {nome: $chamado.autor_nome}
        }
      }
    }

    var $comentario {
      value = {
        id: $novo_comentario.id,
        conteudo: $novo_comentario.mensagem,
        criado_em: $novo_comentario.criado_em,
        autor: $autor
      }
    }
  }

  response = {comentario: $comentario}

  test "cria comentario publico" {
    input = {usuarios_id: 8, chamados_id: 101, conteudo: "Comentário público"}
    expect.to_equal ($response.comentario.conteudo) { value = "Comentário público" }
    expect.to_equal ($response.comentario.autor.nome) { value = "Gerente" }
    expect.to_not_be_defined ($response.comentario.usuarios_id)
  }

  test "rejeita conteudo vazio" {
    input = {usuarios_id: 8, chamados_id: 101, conteudo: "   "}
    expect.to_throw { exception = "" }
  }

  test "rejeita encerrado" {
    input = {usuarios_id: 8, chamados_id: 101, conteudo: "Comentário"}
    expect.to_throw { exception = "" }
  }

  test "rejeita cancelado" {
    input = {usuarios_id: 8, chamados_id: 101, conteudo: "Comentário"}
    expect.to_throw { exception = "" }
  }
  guid = "miraCriarComentarioGerente01"
}
