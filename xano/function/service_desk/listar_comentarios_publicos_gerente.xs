// Lista somente comentários explicitamente públicos de chamado autorizado.
function "service_desk/listar_comentarios_publicos_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "service_desk/obter_chamado_gerente_autorizado" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $input.chamados_id}
      mock = {
        "lista publico em ordem desc": {id: 101, status: "Novo", autor_nome: "Gerente"}
        "lista sem interacao legado": {id: 101, status: "Novo", autor_nome: "Gerente"}
      }
    } as $chamado

    db.query interacoes_chamado {
      join = {
        autor: {
          table: "usuarios"
          type: "left"
          where: $db.interacoes_chamado.usuarios_id == $db.autor.id
        }
      }
      eval = {
        autor_nome: $db.autor.nome
      }
      where = $db.interacoes_chamado.chamados_id == $chamado.id && $db.interacoes_chamado.visibilidade == "publica" && $db.interacoes_chamado.mensagem != null && $db.interacoes_chamado.mensagem != ""
      sort = {interacoes_chamado.criado_em: "desc"}
      return = {type: "list"}
      mock = {
        "lista publico em ordem desc": ```
          [
            {id: 12, mensagem: "Comentário recente", criado_em: 1780000002000, autor_nome: "Gerente"},
            {id: 11, mensagem: "Comentário anterior", criado_em: 1780000001000, autor_nome: null}
          ]
          ```
        "lista sem interacao legado": []
      }
    } as $interacoes

    var $items {
      value = $interacoes|map:{
        id: $$.id,
        conteudo: $$.mensagem,
        criado_em: $$.criado_em,
        autor: ($$.autor_nome != null && $$.autor_nome != "") ? {nome: $$.autor_nome} : null
      }
    }
  }

  response = {items: $items}

  test "lista publico em ordem desc" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_not_be_null ($response.items)
  }

  test "lista sem interacao legado" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_be_empty ($response.items)
  }
  guid = "miraListarComentariosGerente01"
}
