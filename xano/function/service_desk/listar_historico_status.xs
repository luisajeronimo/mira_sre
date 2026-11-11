// Projeta, somente para leitura, as transições de status registradas pelo Save
// em `alteracao_chamado` (H-1). O chamador autoriza o chamado antes da chamada.
function "service_desk/listar_historico_status" {
  input {
    int chamados_id
  }

  stack {
    // Seleção pelo tipo do evento e pelo chamado; visibilidade não participa.
    db.query interacoes_chamado {
      join = {
        usuarios: {
          table: "usuarios"
          type: "left"
          where: $db.interacoes_chamado.usuarios_id == $db.usuarios.id
        }
      }
      eval = {
        autor_id: $db.usuarios.id
        autor_nome: $db.usuarios.nome
        autor_role: $db.usuarios.role
      }
      where = $db.interacoes_chamado.chamados_id == $input.chamados_id && $db.interacoes_chamado.tipo_evento == "alteracao_chamado"
      sort = {interacoes_chamado.criado_em: "desc", interacoes_chamado.id: "desc"}
      return = {type: "list"}
      mock = {
        "projeta somente transicoes validas": [
          {id: 30, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Em Atendimento", resultante: "Resolvido"}, prioridade: {anterior: "Média", resultante: "Alta"}, responsavel: {anterior: 12, resultante: 10}, comentario_interacao_id: 29}, criado_em: 1780000005000, visibilidade: "interna", usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"},
          {id: 29, tipo_evento: "alteracao_chamado", alteracoes: {status: "Resolvido"}, criado_em: 1780000004500, visibilidade: null, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"},
          {id: 28, tipo_evento: "alteracao_chamado", alteracoes: {prioridade: {anterior: "Baixa", resultante: "Média"}}, criado_em: 1780000004000, visibilidade: null, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"},
          {id: 27, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Novo", resultante: "Novo"}}, criado_em: 1780000003000, visibilidade: null, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"},
          {id: 26, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: null, visibilidade: null, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"},
          {id: 25, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780000002000, visibilidade: "publica", usuarios_id: 4, autor_id: 4, autor_nome: "Diretoria", autor_role: "diretoria"},
          {id: 24, tipo_evento: "alteracao_chamado", alteracoes: null, criado_em: 1780000001500, visibilidade: null, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"},
          {id: 23, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Novo"}}, criado_em: 1780000001000, visibilidade: null, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", autor_role: "tecnico"}
        ]
        "identifica autores": [
          {id: 43, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Resolvido", resultante: "Encerrado"}}, criado_em: 1780000009000, visibilidade: null, usuarios_id: null, autor_id: null, autor_nome: null, autor_role: null},
          {id: 42, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Em Atendimento", resultante: "Resolvido"}}, criado_em: 1780000008000, visibilidade: null, usuarios_id: 99, autor_id: null, autor_nome: null, autor_role: null},
          {id: 41, tipo_evento: "alteracao_chamado", alteracoes: {status: {anterior: "Novo", resultante: "Em Atendimento"}}, criado_em: 1780000007000, visibilidade: null, usuarios_id: 50, autor_id: 50, autor_nome: "Perfil legado", autor_role: "tecnico_n1"}
        ]
        "retorna lista vazia sem transicoes": []
      }
    } as $eventos

    var $items {
      value = []
    }

    foreach ($eventos) {
      each as $evento {
        var $par {
          value = null
        }

        var $anterior {
          value = null
        }

        var $resultante {
          value = null
        }

        // Leitura em etapas com `get` e padrão nulo: não depende de curto-circuito
        // nem do acesso por ponto a chave ausente em campo `json`.
        conditional {
          if ($evento.alteracoes|is_object) {
            var.update $par {
              value = $evento.alteracoes|get:"status":null
            }
          }
        }

        conditional {
          if ($par|is_object) {
            var.update $anterior {
              value = $par|get:"anterior":null
            }

            var.update $resultante {
              value = $par|get:"resultante":null
            }
          }
        }

        conditional {
          if (($anterior|is_text) && ($resultante|is_text) && $anterior != "" && $resultante != "" && $anterior != $resultante && $evento.criado_em != null) {
            var $autor {
              value = null
            }

            conditional {
              if ($evento.usuarios_id == null || $evento.usuarios_id == 0) {
                var.update $autor {
                  value = {nome: "Sistema", perfil: null}
                }
              }

              elseif ($evento.autor_id != null && $evento.autor_id != 0) {
                var $perfil {
                  value = null
                }

                conditional {
                  if ($evento.autor_role == "gerente") {
                    var.update $perfil {
                      value = "Gerente"
                    }
                  }

                  elseif ($evento.autor_role == "tecnico") {
                    var.update $perfil {
                      value = "Técnico"
                    }
                  }

                  elseif ($evento.autor_role == "diretoria") {
                    var.update $perfil {
                      value = "Diretoria"
                    }
                  }

                  elseif ($evento.autor_role == "administrador") {
                    var.update $perfil {
                      value = "Administrador"
                    }
                  }
                }

                var.update $autor {
                  value = {nome: $evento.autor_nome, perfil: $perfil}
                }
              }
            }

            array.push $items {
              value = {
                id                : $evento.id
                status_anterior   : $anterior
                status_resultante : $resultante
                criado_em         : $evento.criado_em
                autor             : $autor
              }
            }
          }
        }
      }
    }
  }

  response = {items: $items}

  test "projeta somente transicoes validas" {
    input = {chamados_id: 101}

    expect.to_equal ($response.items) {
      value = [
        {id: 30, status_anterior: "Em Atendimento", status_resultante: "Resolvido", criado_em: 1780000005000, autor: {nome: "Técnico", perfil: "Técnico"}},
        {id: 25, status_anterior: "Novo", status_resultante: "Em Atendimento", criado_em: 1780000002000, autor: {nome: "Diretoria", perfil: "Diretoria"}}
      ]
    }
  }

  test "identifica autores" {
    input = {chamados_id: 101}

    expect.to_equal ($response.items) {
      value = [
        {id: 43, status_anterior: "Resolvido", status_resultante: "Encerrado", criado_em: 1780000009000, autor: {nome: "Sistema", perfil: null}},
        {id: 42, status_anterior: "Em Atendimento", status_resultante: "Resolvido", criado_em: 1780000008000, autor: null},
        {id: 41, status_anterior: "Novo", status_resultante: "Em Atendimento", criado_em: 1780000007000, autor: {nome: "Perfil legado", perfil: null}}
      ]
    }
  }

  test "retorna lista vazia sem transicoes" {
    input = {chamados_id: 101}

    expect.to_be_empty ($response.items)
  }

  guid = "miraListarHistoricoStatus01"
}
