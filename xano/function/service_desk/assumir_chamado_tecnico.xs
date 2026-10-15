// Executa alterações de responsável no Service Desk pelo Xano.
// A mutação e seu evento são persistidos na mesma transação.
function "service_desk/assumir_chamado_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
    text acao? filters=trim
    int? tecnico_id?
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "assume padrão": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "assume ação vazia": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "assume idempotente": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "assume outro técnico": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "atribui em Resolvido": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "reatribui": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "rejeita alvo não Técnico": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "libera própria": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "Técnico não libera outro": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "Diretoria libera": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "Administrador libera": ```
          {id: 14, nome: "Administrador", email: "admin@example.test", role: "administrador", lojas_id: null}
          ```
        "Encerrado terminal": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "Cancelado terminal": ```
          {id: 14, nome: "Administrador", email: "admin@example.test", role: "administrador", lojas_id: null}
          ```
        "status desconhecido": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "Diretoria não assume": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "atribui mesmo Técnico": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "libera sem responsável": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    var $acao {
      value = $input.acao
    }
    conditional {
      if ($acao == null || $acao == "") {
        var.update $acao {
          value = "assumir"
        }
      }
    }

    precondition ($acao == "assumir" || $acao == "atribuir" || $acao == "liberar") {
      error_type = "inputerror"
      error = "Ação de responsável inválida."
    }

    conditional {
      if ($acao == "assumir" && $usuario.role != "tecnico") {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "accessdenied"
          error = "Somente Técnico pode assumir chamado."
        }
      }
      elseif ($acao == "atribuir" && ($input.tecnico_id == null || $input.tecnico_id < 1)) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Informe um Técnico para atribuição."
        }
      }
      elseif (($acao == "assumir" || $acao == "liberar") && $input.tecnico_id != null) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "A ação não aceita Técnico alvo."
        }
      }
    }

    db.get chamados {
      field_name = "id"
      field_value = $input.chamados_id
      mock = {
        "assume padrão": {id: 101, status: "Novo", tecnico_id: null}
        "assume ação vazia": {id: 101, status: "Novo", tecnico_id: null}
        "assume idempotente": {id: 101, status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
        "assume outro técnico": {id: 101, status: "Novo", tecnico_id: 13, atribuido_em: 1780000001000}
        "atribui em Resolvido": {id: 101, status: "Resolvido", tecnico_id: null}
        "reatribui": {id: 101, status: "Em Atendimento", tecnico_id: 12, atribuido_em: 1780000001000}
        "rejeita alvo não Técnico": {id: 101, status: "Novo", tecnico_id: null}
        "libera própria": {id: 101, status: "Aguardando Solicitante", tecnico_id: 12, atribuido_em: 1780000001000}
        "Técnico não libera outro": {id: 101, status: "Novo", tecnico_id: 10, atribuido_em: 1780000001000}
        "Diretoria libera": {id: 101, status: "Em Atendimento", tecnico_id: 10, atribuido_em: 1780000001000}
        "Administrador libera": {id: 101, status: "Resolvido", tecnico_id: 10, atribuido_em: 1780000001000}
        "Encerrado terminal": {id: 101, status: "Encerrado", tecnico_id: 10, atribuido_em: 1780000001000}
        "Cancelado terminal": {id: 101, status: "Cancelado", tecnico_id: null}
        "status desconhecido": {id: 101, status: "Desconhecido", tecnico_id: null}
        "Diretoria não assume": {id: 101, status: "Novo", tecnico_id: null}
        "atribui mesmo Técnico": {id: 101, status: "Novo", tecnico_id: 10, atribuido_em: 1780000001000}
        "libera sem responsável": {id: 101, status: "Novo", tecnico_id: null}
      }
    } as $atual

    precondition ($atual != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    var $status_reconhecido {
      value = $atual.status == "Novo" || $atual.status == "Em Atendimento" || $atual.status == "Aguardando Solicitante" || $atual.status == "Aguardando Mudança" || $atual.status == "Resolvido" || $atual.status == "Solução Rejeitada" || $atual.status == "Encerrado" || $atual.status == "Cancelado"
    }

    conditional {
      if (!$status_reconhecido) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Status do chamado não reconhecido para atribuição."
        }
      }
      elseif ($atual.status == "Encerrado" || $atual.status == "Cancelado") {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Chamado terminal não permite alteração de responsável."
        }
      }
      elseif ($acao == "assumir" && $atual.tecnico_id != null && $atual.tecnico_id != 0 && $atual.tecnico_id != $usuario.id) {
        util.set_header {
          value = "HTTP/1.1 409 Conflict"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Chamado já foi assumido por outro Técnico."
        }
      }
    }

    var $alterou_responsavel {
      value = false
    }

    var $conflito_assumir {
      value = false
    }

    var $tecnico_anterior_id {
      value = null
    }

    var $tecnico_novo_id {
      value = null
    }

    var $tipo_evento {
      value = null
    }

    db.transaction {
      stack {
        db.get chamados {
          field_name = "id"
          field_value = $input.chamados_id
          mock = {
            "assume padrão": {id: 101, status: "Novo", tecnico_id: null}
            "assume ação vazia": {id: 101, status: "Novo", tecnico_id: null}
            "assume idempotente": {id: 101, status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
            "atribui em Resolvido": {id: 101, status: "Resolvido", tecnico_id: null}
            "reatribui": {id: 101, status: "Em Atendimento", tecnico_id: 12, atribuido_em: 1780000001000}
            "rejeita alvo não Técnico": {id: 101, status: "Novo", tecnico_id: null}
            "libera própria": {id: 101, status: "Aguardando Solicitante", tecnico_id: 12, atribuido_em: 1780000001000}
            "Técnico não libera outro": {id: 101, status: "Novo", tecnico_id: 10, atribuido_em: 1780000001000}
            "Diretoria libera": {id: 101, status: "Em Atendimento", tecnico_id: 10, atribuido_em: 1780000001000}
            "Administrador libera": {id: 101, status: "Resolvido", tecnico_id: 10, atribuido_em: 1780000001000}
            "atribui mesmo Técnico": {id: 101, status: "Novo", tecnico_id: 10, atribuido_em: 1780000001000}
            "libera sem responsável": {id: 101, status: "Novo", tecnico_id: null}
          }
        } as $verificacao

        precondition ($verificacao != null) {
          error_type = "notfound"
          error = "Recurso não encontrado."
        }

        var $status_atual_reconhecido {
          value = $verificacao.status == "Novo" || $verificacao.status == "Em Atendimento" || $verificacao.status == "Aguardando Solicitante" || $verificacao.status == "Aguardando Mudança" || $verificacao.status == "Resolvido" || $verificacao.status == "Solução Rejeitada" || $verificacao.status == "Encerrado" || $verificacao.status == "Cancelado"
        }

        conditional {
          if (!$status_atual_reconhecido) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "Status do chamado não reconhecido para atribuição."
            }
          }
          elseif ($verificacao.status == "Encerrado" || $verificacao.status == "Cancelado") {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "Chamado terminal não permite alteração de responsável."
            }
          }
        }

        var $responsavel_atual_id {
          value = ($verificacao.tecnico_id == null || $verificacao.tecnico_id == 0) ? null : $verificacao.tecnico_id
        }

        var $responsavel_destino_id {
          value = $responsavel_atual_id
        }

        conditional {
          if ($acao == "atribuir") {
            db.get usuarios {
              field_name = "id"
              field_value = $input.tecnico_id
              mock = {
                "atribui em Resolvido": {id: 10, nome: "Técnico alvo", role: "tecnico"}
                "reatribui": {id: 10, nome: "Outro Técnico", role: "tecnico"}
                "rejeita alvo não Técnico": {id: 20, nome: "Gerente", role: "gerente"}
                "atribui mesmo Técnico": {id: 10, nome: "Técnico alvo", role: "tecnico"}
              }
            } as $tecnico_alvo

            conditional {
              if ($tecnico_alvo == null || $tecnico_alvo.role != "tecnico") {
                util.set_header {
                  value = "HTTP/1.1 422 Unprocessable Entity"
                  duplicates = "replace"
                }

                precondition (false) {
                  error_type = "inputerror"
                  error = "O responsável informado deve possuir perfil Técnico."
                }
              }
            }

            var.update $responsavel_destino_id {
              value = $tecnico_alvo.id
            }
          }
        }

        conditional {
          if ($acao == "liberar" && $responsavel_atual_id != null && $usuario.role == "tecnico" && $responsavel_atual_id != $usuario.id) {
            util.set_header {
              value = "HTTP/1.1 403 Forbidden"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "accessdenied"
              error = "Técnico só pode liberar a própria atribuição."
            }
          }
        }

        conditional {
          if ($acao == "assumir") {
            conditional {
              if ($responsavel_atual_id == $usuario.id) {
                // Repetição pelo responsável atual é idempotente.
              }
              elseif ($responsavel_atual_id != null) {
                var.update $conflito_assumir {
                  value = true
                }
              }
              else {
                var.update $responsavel_destino_id {
                  value = $usuario.id
                }

                var.update $tipo_evento {
                  value = "atribuicao"
                }

                var.update $alterou_responsavel {
                  value = true
                }
              }
            }
          }
          elseif ($acao == "atribuir") {
            conditional {
              if ($responsavel_atual_id == $responsavel_destino_id) {
                // Atribuição ao Técnico já responsável não renova dados nem evento.
              }
              else {
                var.update $tipo_evento {
                  value = ($responsavel_atual_id == null) ? "atribuicao" : "reatribuicao"
                }

                var.update $alterou_responsavel {
                  value = true
                }
              }
            }
          }
          else {
            conditional {
              if ($responsavel_atual_id == null) {
                // Liberar chamado sem responsável é uma operação sem efeito.
              }
              else {
                var.update $responsavel_destino_id {
                  value = null
                }

                var.update $tipo_evento {
                  value = "liberacao"
                }

                var.update $alterou_responsavel {
                  value = true
                }
              }
            }
          }
        }

        conditional {
          if ($alterou_responsavel) {
            var.update $tecnico_anterior_id {
              value = $responsavel_atual_id
            }

            var.update $tecnico_novo_id {
              value = $responsavel_destino_id
            }

            var $instante {
              value = now
              mock = {
                "assume padrão": 1780000002000
                "assume ação vazia": 1780000002000
                "atribui em Resolvido": 1780000002000
                "reatribui": 1780000002000
                "libera própria": 1780000002000
                "Diretoria libera": 1780000002000
                "Administrador libera": 1780000002000
              }
            }

            db.edit chamados {
              field_name = "id"
              field_value = $verificacao.id
              data = {
                tecnico_id: $responsavel_destino_id,
                atribuido_em: ($tipo_evento == "liberacao") ? null : $instante,
                ultima_atualizacao_em: $instante
              }
              mock = {
                "assume padrão": {id: 101, tecnico_id: 12, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000}
                "assume ação vazia": {id: 101, tecnico_id: 12, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000}
                "atribui em Resolvido": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000}
                "reatribui": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000}
                "libera própria": {id: 101, tecnico_id: null, atribuido_em: null, ultima_atualizacao_em: 1780000002000}
                "Diretoria libera": {id: 101, tecnico_id: null, atribuido_em: null, ultima_atualizacao_em: 1780000002000}
                "Administrador libera": {id: 101, tecnico_id: null, atribuido_em: null, ultima_atualizacao_em: 1780000002000}
              }
            } as $chamado_atualizado

            db.add interacoes_chamado {
              data = {
                tipo_evento: $tipo_evento,
                chamados_id: $verificacao.id,
                usuarios_id: $usuario.id,
                criado_em: $instante,
                visibilidade: "interna",
                tecnico_anterior_id: $tecnico_anterior_id,
                tecnico_novo_id: $tecnico_novo_id
              }
              mock = {
                "assume padrão": {id: 21, tipo_evento: "atribuicao", chamados_id: 101, usuarios_id: 12, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: null, tecnico_novo_id: 12}
                "assume ação vazia": {id: 21, tipo_evento: "atribuicao", chamados_id: 101, usuarios_id: 12, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: null, tecnico_novo_id: 12}
                "atribui em Resolvido": {id: 21, tipo_evento: "atribuicao", chamados_id: 101, usuarios_id: 4, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: null, tecnico_novo_id: 10}
                "reatribui": {id: 21, tipo_evento: "reatribuicao", chamados_id: 101, usuarios_id: 12, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: 12, tecnico_novo_id: 10}
                "libera própria": {id: 21, tipo_evento: "liberacao", chamados_id: 101, usuarios_id: 12, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: 12, tecnico_novo_id: null}
                "Diretoria libera": {id: 21, tipo_evento: "liberacao", chamados_id: 101, usuarios_id: 4, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: 10, tecnico_novo_id: null}
                "Administrador libera": {id: 21, tipo_evento: "liberacao", chamados_id: 101, usuarios_id: 14, criado_em: 1780000002000, visibilidade: "interna", tecnico_anterior_id: 10, tecnico_novo_id: null}
              }
            } as $evento_criado
          }
        }
      }
    }

    conditional {
      if ($acao == "assumir") {
        db.get chamados {
          field_name = "id"
          field_value = $input.chamados_id
          mock = {
            "assume padrão": {id: 101, status: "Novo", tecnico_id: 12, atribuido_em: 1780000002000}
            "assume ação vazia": {id: 101, status: "Novo", tecnico_id: 12, atribuido_em: 1780000002000}
            "assume idempotente": {id: 101, status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
          }
        } as $pos_edicao

        precondition ($pos_edicao != null) {
          error_type = "notfound"
          error = "Recurso não encontrado."
        }

        conditional {
          if ($conflito_assumir || $pos_edicao.tecnico_id != $usuario.id) {
            util.set_header {
              value = "HTTP/1.1 409 Conflict"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "Chamado já foi assumido por outro Técnico."
            }
          }
        }
      }
    }

    function.run "service_desk/obter_chamado_tecnico" {
      input = {usuarios_id: $usuario.id, chamados_id: $input.chamados_id}
      mock = {
        "assume padrão": {chamado: {id: 101, status: "Novo", tecnico: {id: 12, nome: "Técnico"}, atribuido_em: 1780000002000}}
        "assume ação vazia": {chamado: {id: 101, status: "Novo", tecnico: {id: 12, nome: "Técnico"}, atribuido_em: 1780000002000}}
        "assume idempotente": {chamado: {id: 101, status: "Novo", tecnico: {id: 12, nome: "Técnico"}, atribuido_em: 1780000001000}}
        "atribui em Resolvido": {chamado: {id: 101, status: "Resolvido", tecnico: {id: 10, nome: "Técnico alvo"}, atribuido_em: 1780000002000}}
        "reatribui": {chamado: {id: 101, status: "Em Atendimento", tecnico: {id: 10, nome: "Outro Técnico"}, atribuido_em: 1780000002000}}
        "libera própria": {chamado: {id: 101, status: "Aguardando Solicitante", tecnico: null, atribuido_em: null}}
        "Diretoria libera": {chamado: {id: 101, status: "Em Atendimento", tecnico: null, atribuido_em: null}}
        "Administrador libera": {chamado: {id: 101, status: "Resolvido", tecnico: null, atribuido_em: null}}
        "atribui mesmo Técnico": {chamado: {id: 101, status: "Novo", tecnico: {id: 10, nome: "Técnico alvo"}, atribuido_em: 1780000001000}}
        "libera sem responsável": {chamado: {id: 101, status: "Novo", tecnico: null, atribuido_em: null}}
      }
    } as $detalhe
  }

  response = {chamado: $detalhe.chamado}

  test "assume padrão" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.chamado.status) { value = "Novo" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 12 }
    expect.to_equal ($response.chamado.atribuido_em) { value = 1780000002000 }
  }

  test "assume ação vazia" {
    input = {usuarios_id: 12, chamados_id: 101, acao: ""}
    expect.to_equal ($response.chamado.status) { value = "Novo" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 12 }
    expect.to_equal ($response.chamado.atribuido_em) { value = 1780000002000 }
  }

  test "assume idempotente" {
    input = {usuarios_id: 12, chamados_id: 101, acao: "assumir"}
    expect.to_equal ($response.chamado.tecnico.id) { value = 12 }
    expect.to_equal ($response.chamado.atribuido_em) { value = 1780000001000 }
  }

  test "assume outro técnico" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_throw { exception = "" }
  }

  test "atribui em Resolvido" {
    input = {usuarios_id: 4, chamados_id: 101, acao: "atribuir", tecnico_id: 10}
    expect.to_equal ($response.chamado.status) { value = "Resolvido" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 10 }
  }

  test "reatribui" {
    input = {usuarios_id: 12, chamados_id: 101, acao: "atribuir", tecnico_id: 10}
    expect.to_equal ($response.chamado.status) { value = "Em Atendimento" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 10 }
  }

  test "rejeita alvo não Técnico" {
    input = {usuarios_id: 4, chamados_id: 101, acao: "atribuir", tecnico_id: 20}
    expect.to_throw { exception = "" }
  }

  test "libera própria" {
    input = {usuarios_id: 12, chamados_id: 101, acao: "liberar"}
    expect.to_equal ($response.chamado.status) { value = "Aguardando Solicitante" }
    expect.to_equal ($response.chamado.tecnico) { value = null }
  }

  test "Técnico não libera outro" {
    input = {usuarios_id: 12, chamados_id: 101, acao: "liberar"}
    expect.to_throw { exception = "" }
  }

  test "Diretoria libera" {
    input = {usuarios_id: 4, chamados_id: 101, acao: "liberar"}
    expect.to_equal ($response.chamado.status) { value = "Em Atendimento" }
    expect.to_equal ($response.chamado.tecnico) { value = null }
  }

  test "Administrador libera" {
    input = {usuarios_id: 14, chamados_id: 101, acao: "liberar"}
    expect.to_equal ($response.chamado.status) { value = "Resolvido" }
    expect.to_equal ($response.chamado.tecnico) { value = null }
  }

  test "Encerrado terminal" {
    input = {usuarios_id: 4, chamados_id: 101, acao: "liberar"}
    expect.to_throw { exception = "" }
  }

  test "Cancelado terminal" {
    input = {usuarios_id: 14, chamados_id: 101, acao: "atribuir", tecnico_id: 10}
    expect.to_throw { exception = "" }
  }

  test "status desconhecido" {
    input = {usuarios_id: 4, chamados_id: 101, acao: "atribuir", tecnico_id: 10}
    expect.to_throw { exception = "" }
  }

  test "Diretoria não assume" {
    input = {usuarios_id: 4, chamados_id: 101}
    expect.to_throw { exception = "" }
  }

  test "atribui mesmo Técnico" {
    input = {usuarios_id: 4, chamados_id: 101, acao: "atribuir", tecnico_id: 10}
    expect.to_equal ($response.chamado.tecnico.id) { value = 10 }
    expect.to_equal ($response.chamado.atribuido_em) { value = 1780000001000 }
  }

  test "libera sem responsável" {
    input = {usuarios_id: 12, chamados_id: 101, acao: "liberar"}
    expect.to_equal ($response.chamado.tecnico) { value = null }
  }

  guid = "miraAssumirTecnico01"
}
