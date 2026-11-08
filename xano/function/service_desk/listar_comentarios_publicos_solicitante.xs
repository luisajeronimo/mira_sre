// Lista somente comentários explicitamente públicos de chamado autorizado pelo
// vínculo de solicitante. Filtro e DTO idênticos aos do contrato do Gerente.
function "service_desk/listar_comentarios_publicos_solicitante" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "service_desk/obter_chamado_solicitante_autorizado" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $input.chamados_id}
      mock = {
        "lista publico do solicitante": {id: 101, status: "Resolvido"}
        "lista vazia do solicitante"  : {id: 101, status: "Resolvido"}
      }
    } as $chamado

    db.query interacoes_chamado {
      join = {
        usuarios: {
          table: "usuarios"
          type: "left"
          where: $db.interacoes_chamado.usuarios_id == $db.usuarios.id
        }
      }
      eval = {
        autor_nome: $db.usuarios.nome
      }
      where = $db.interacoes_chamado.chamados_id == $chamado.id && ($db.interacoes_chamado.tipo_evento == "comentario" || $db.interacoes_chamado.tipo_evento == null || $db.interacoes_chamado.tipo_evento == "") && $db.interacoes_chamado.visibilidade == "publica" && $db.interacoes_chamado.mensagem != null && $db.interacoes_chamado.mensagem != ""
      sort = {interacoes_chamado.criado_em: "desc"}
      return = {type: "list"}
      mock = {
        "lista publico do solicitante": [
          {id: 12, mensagem: "Comentário recente", criado_em: 1780000002000, autor_nome: "Técnico"},
          {id: 11, mensagem: "Comentário anterior", criado_em: 1780000001000, autor_nome: null}
        ]
        "lista vazia do solicitante"  : []
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

  test "lista publico do solicitante" {
    input = {usuarios_id: 8, chamados_id: 101}

    expect.to_equal ($response.items) {
      value = [
        {id: 12, conteudo: "Comentário recente", criado_em: 1780000002000, autor: {nome: "Técnico"}},
        {id: 11, conteudo: "Comentário anterior", criado_em: 1780000001000, autor: null}
      ]
    }
  }

  test "lista vazia do solicitante" {
    input = {usuarios_id: 8, chamados_id: 101}

    expect.to_be_empty ($response.items)
  }

  guid = "miraComentariosSolicitante01"
}
