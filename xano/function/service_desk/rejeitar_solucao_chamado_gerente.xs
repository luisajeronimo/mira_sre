// Rejeição específica de solução de chamado Resolvido pelo Gerente da Loja (DR2-1).
function "service_desk/rejeitar_solucao_chamado_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
    text justificativa?
    timestamp? ultima_atualizacao_em?
  }

  stack {
    function.run "service_desk/obter_chamado_gerente_autorizado" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $input.chamados_id}
      mock = {
        "rejeita solucao com sucesso": {id: 101, status: "Resolvido", autor_nome: "Gerente"}
        "rejeita com justificativa vazia": {id: 101, status: "Resolvido", autor_nome: "Gerente"}
        "rejeita fora de resolvido": {id: 101, status: "Novo", autor_nome: "Gerente"}
        "rejeita chamado encerrado": {id: 101, status: "Encerrado", autor_nome: "Gerente"}
        "rejeita chamado cancelado": {id: 101, status: "Cancelado", autor_nome: "Gerente"}
        "rejeita detalhe desatualizado": {id: 101, status: "Resolvido", autor_nome: "Gerente"}
        "rejeita alteracao durante transacao": {id: 101, status: "Resolvido", autor_nome: "Gerente"}
      }
    } as $chamado

    db.get chamados {
      field_name = "id"
      field_value = $chamado.id
      mock = {
        "rejeita solucao com sucesso": {id: 101, status: "Resolvido", ultima_atualizacao_em: 1780000000000}
        "rejeita com justificativa vazia": {id: 101, status: "Resolvido", ultima_atualizacao_em: 1780000000000}
        "rejeita fora de resolvido": {id: 101, status: "Novo", ultima_atualizacao_em: 1780000000000}
        "rejeita chamado encerrado": {id: 101, status: "Encerrado", ultima_atualizacao_em: 1780000000000}
        "rejeita chamado cancelado": {id: 101, status: "Cancelado", ultima_atualizacao_em: 1780000000000}
        "rejeita detalhe desatualizado": {id: 101, status: "Resolvido", ultima_atualizacao_em: 1780000000000}
        "rejeita alteracao durante transacao": {id: 101, status: "Resolvido", ultima_atualizacao_em: 1780000000000}
      }
    } as $registro

    conditional {
      if ($registro == null) {
        util.set_header {
          value = "HTTP/1.1 409 Conflict"
          duplicates = "replace"
        }
        return {
          value = {sucesso: false, erro: "Conflito de concorrência. Chamado indisponível."}
        }
      }
    }

    var $justificativa {
      value = $input.justificativa
    }

    conditional {
      if ($justificativa != null) {
        var.update $justificativa {
          value = $justificativa|trim
        }
      }
    }

    conditional {
      if ($justificativa == null || $justificativa == "") {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        return {
          value = {sucesso: false, erro: "Entrada inválida. Justificativa obrigatória."}
        }
      }
    }

    conditional {
      if ($registro.status != "Resolvido") {
        util.set_header {
          value = "HTTP/1.1 409 Conflict"
          duplicates = "replace"
        }

        return {
          value = {sucesso: false, erro: "Conflito de estado. Somente chamados Resolvidos podem ser rejeitados."}
        }
      }
    }

    conditional {
      if ($input.ultima_atualizacao_em == null || $registro.ultima_atualizacao_em != $input.ultima_atualizacao_em) {
        util.set_header {
          value = "HTTP/1.1 409 Conflict"
          duplicates = "replace"
        }

        return {
          value = {sucesso: false, erro: "Conflito de concorrência. Detalhe desatualizado."}
        }
      }
    }

    var $instante {
      value = now
      mock = {
        "rejeita solucao com sucesso": 1780000002000
      }
    }

    var $comentario_id {
      value = null
    }

    var $versao_validada {
      value = $input.ultima_atualizacao_em
    }

    db.transaction {
      stack {
        db.get chamados {
          field_name = "id"
          field_value = $chamado.id
          mock = {
            "rejeita solucao com sucesso": {id: 101, status: "Resolvido", ultima_atualizacao_em: 1780000000000}
            "rejeita alteracao durante transacao": {id: 101, status: "Solução Rejeitada", ultima_atualizacao_em: 1780000002000}
          }
        } as $revalidado

        conditional {
          if ($revalidado.status != "Resolvido" || $revalidado.ultima_atualizacao_em != $versao_validada) {
            util.set_header {
              value = "HTTP/1.1 409 Conflict"
              duplicates = "replace"
            }

            return {
              value = {sucesso: false, erro: "Conflito de concorrência na transação."}
            }
          }
        }

        db.add interacoes_chamado {
          data = {
            mensagem: $justificativa
            criado_em: $instante
            visibilidade: "publica"
            tipo_evento: "comentario"
            chamados_id: $chamado.id
            usuarios_id: $input.usuarios_id
          }
          mock = {
            "rejeita solucao com sucesso": {id: 201, mensagem: "Solução insatisfatória", criado_em: 1780000002000, visibilidade: "publica", tipo_evento: "comentario", chamados_id: 101, usuarios_id: 8}
          }
        } as $novo_comentario

        var.update $comentario_id {
          value = $novo_comentario.id
        }

        db.patch chamados {
          field_name = "id"
          field_value = $chamado.id
          data = {
            status: "Solução Rejeitada"
            ultima_atualizacao_em: $instante
          }
          mock = {
            "rejeita solucao com sucesso": {id: 101, status: "Solução Rejeitada", ultima_atualizacao_em: 1780000002000}
          }
        } as $chamado_atualizado

        db.add interacoes_chamado {
          data = {
            tipo_evento: "alteracao_chamado"
            alteracoes: {
              status: {
                anterior: "Resolvido"
                resultante: "Solução Rejeitada"
              }
              comentario_interacao_id: $novo_comentario.id
            }
            criado_em: $instante
            chamados_id: $chamado.id
            usuarios_id: $input.usuarios_id
          }
          mock = {
            "rejeita solucao com sucesso": {id: 202, tipo_evento: "alteracao_chamado", criado_em: 1780000002000, chamados_id: 101, usuarios_id: 8}
          }
        } as $novo_evento
      }
    }

    function.run "service_desk/obter_chamado_gerente" {
      input = {usuarios_id: $input.usuarios_id, chamados_id: $chamado.id}
      mock = {
        "rejeita solucao com sucesso": {
          chamado: {
            id: 101
            status: "Solução Rejeitada"
            ultima_atualizacao_em: 1780000002000
          }
        }
      }
    } as $detalhe_atualizado
  }

  response = {
    sucesso: true
    chamado: $detalhe_atualizado.chamado
  }

  test "rejeita solucao com sucesso" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "Solução insatisfatória"
      ultima_atualizacao_em: 1780000000000
    }
    expect.to_equal ($response.sucesso) { value = true }
    expect.to_equal ($response.chamado.status) { value = "Solução Rejeitada" }
  }

  test "rejeita com justificativa vazia" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "   "
      ultima_atualizacao_em: 1780000000000
    }
    expect.to_equal ($response.sucesso) { value = false }
    expect.to_equal ($response.erro) { value = "Entrada inválida. Justificativa obrigatória." }
  }

  test "rejeita fora de resolvido" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "Não está resolvido"
      ultima_atualizacao_em: 1780000000000
    }
    expect.to_equal ($response.sucesso) { value = false }
  }

  test "rejeita chamado encerrado" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "Encerrado"
      ultima_atualizacao_em: 1780000000000
    }
    expect.to_equal ($response.sucesso) { value = false }
  }

  test "rejeita chamado cancelado" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "Cancelado"
      ultima_atualizacao_em: 1780000000000
    }
    expect.to_equal ($response.sucesso) { value = false }
  }

  test "rejeita detalhe desatualizado" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "Desatualizado"
      ultima_atualizacao_em: 1779999999000
    }
    expect.to_equal ($response.sucesso) { value = false }
  }

  test "rejeita alteracao durante transacao" {
    input = {
      usuarios_id: 8
      chamados_id: 101
      justificativa: "Conflito concorrente"
      ultima_atualizacao_em: 1780000000000
    }
    expect.to_equal ($response.sucesso) { value = false }
    expect.to_equal ($response.erro) { value = "Conflito de concorrência na transação." }
  }

  guid = "miraRejeitarSolucaoGerente01"
}
