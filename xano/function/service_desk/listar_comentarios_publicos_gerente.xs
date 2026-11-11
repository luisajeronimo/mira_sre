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
        "identifica somente comentario do encerramento": {id: 101, status: "Encerrado"}
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
      where = $db.interacoes_chamado.chamados_id == $chamado.id && ($db.interacoes_chamado.tipo_evento == "comentario" || $db.interacoes_chamado.tipo_evento == null || $db.interacoes_chamado.tipo_evento == "") && $db.interacoes_chamado.visibilidade == "publica" && $db.interacoes_chamado.mensagem != null && $db.interacoes_chamado.mensagem != ""
      sort = {interacoes_chamado.criado_em: "desc"}
      return = {type: "list"}
      mock = {
        "lista publico em ordem desc": ```
          [
            {id: 12, mensagem: "Comentário recente", criado_em: 1780000002000, usuarios_id: 8, autor_nome: "Gerente"},
            {id: 11, mensagem: "Comentário anterior", criado_em: 1780000001000, usuarios_id: null, autor_nome: null}
          ]
          ```
        "lista sem interacao legado": []
        "identifica somente comentario do encerramento": [
          {id: 32, mensagem: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução.", criado_em: 1780000003000, usuarios_id: null, autor_nome: null},
          {id: 31, mensagem: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução.", criado_em: 1780000002000, usuarios_id: null, autor_nome: null}
        ]
      }
    } as $interacoes

    db.query interacoes_chamado {
      where = $db.interacoes_chamado.chamados_id == $chamado.id && $db.interacoes_chamado.tipo_evento == "alteracao_chamado" && $db.interacoes_chamado.usuarios_id == null
      return = {type: "list"}
      mock = {
        "lista publico em ordem desc": []
        "lista sem interacao legado": []
        "identifica somente comentario do encerramento": [
          {id: 33, usuarios_id: null, alteracoes: {status: {anterior: "Resolvido", resultante: "Encerrado"}, comentario_interacao_id: 32}}
        ]
      }
    } as $eventos_sistema

    var $items {
      value = []
    }

    foreach ($interacoes) {
      each as $interacao {
        var $eh_sistema {
          value = false
        }
        conditional {
          if ($interacao.usuarios_id == null && $interacao.mensagem == "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução.") {
            foreach ($eventos_sistema) {
              each as $evento {
                var $status_evento {
                  value = null
                }
                var $comentario_id {
                  value = null
                }
                var $anterior {
                  value = null
                }
                var $resultante {
                  value = null
                }
                conditional {
                  if ($evento.alteracoes|is_object) {
                    var.update $status_evento {
                      value = $evento.alteracoes|get:"status":null
                    }
                    var.update $comentario_id {
                      value = $evento.alteracoes|get:"comentario_interacao_id":null
                    }
                  }
                }
                conditional {
                  if ($status_evento|is_object) {
                    var.update $anterior {
                      value = $status_evento|get:"anterior":null
                    }
                    var.update $resultante {
                      value = $status_evento|get:"resultante":null
                    }
                  }
                }
                conditional {
                  if ($anterior == "Resolvido" && $resultante == "Encerrado" && $comentario_id == $interacao.id) {
                    var.update $eh_sistema {
                      value = true
                    }
                  }
                }
              }
            }
          }
        }
        array.push $items {
          value = {
            id: $interacao.id
            conteudo: $interacao.mensagem
            criado_em: $interacao.criado_em
            autor: ($interacao.autor_nome != null && $interacao.autor_nome != "") ? {nome: $interacao.autor_nome} : ($eh_sistema ? {nome: "Sistema"} : null)
          }
        }
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

  test "identifica somente comentario do encerramento" {
    input = {usuarios_id: 8, chamados_id: 101}
    expect.to_equal ($response.items) {
      value = [
        {id: 32, conteudo: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução.", criado_em: 1780000003000, autor: {nome: "Sistema"}},
        {id: 31, conteudo: "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução.", criado_em: 1780000002000, autor: null}
      ]
    }
  }
  guid = "miraListarComentariosGerente01"
}
