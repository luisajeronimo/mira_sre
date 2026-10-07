// Autoatribui um chamado elegível ao Técnico autenticado.
// Usa somente operações normais disponíveis no plano Free do Xano.
function "service_desk/assumir_chamado_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true}
      mock = {
        "assume válido": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "idempotente": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "outro técnico": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "status inelegível": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "inexistente": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    db.get chamados {
      field_name = "id"
      field_value = $input.chamados_id
      mock = {
        "assume válido": ```
          {id: 101, titulo: "Falha", status: "Novo", tecnico_id: null}
          ```
        "idempotente": ```
          {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
          ```
        "outro técnico": ```
          {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 13, atribuido_em: 1780000001000}
          ```
        "status inelegível": ```
          {id: 101, titulo: "Falha", status: "Em Atendimento", tecnico_id: null}
          ```
        "inexistente": null
      }
    } as $atual

    precondition ($atual != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    var $status_elegivel {
      value = $atual.status == "Novo"
    }

    conditional {
      if (!$status_elegivel) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Chamado inelegível para assunção."
        }
      }
    }

    var $resultado {
      value = null
    }

    conditional {
      if ($atual.tecnico_id == $usuario.id) {
        function.run "service_desk/obter_chamado_tecnico" {
          input = {usuarios_id: $usuario.id, chamados_id: $input.chamados_id}
        } as $detalhe

        var.update $resultado {
          value = $detalhe.chamado
        }
      }
      elseif ($atual.tecnico_id != null && $atual.tecnico_id != 0) {
        util.set_header {
          value = "HTTP/1.1 409 Conflict"
          duplicates = "replace"
        }

        precondition (false) {
          error_type = "inputerror"
          error = "Chamado já foi assumido por outro Técnico."
        }
      }
      else {
        var $conflito {
          value = false
        }

        db.transaction {
          stack {
            db.get chamados {
              field_name = "id"
              field_value = $input.chamados_id
              mock = {
                "assume válido": ```
                  {id: 101, titulo: "Falha", status: "Novo", tecnico_id: null}
                  ```
                "idempotente": ```
                  {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
                  ```
                "outro técnico": ```
                  {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 13, atribuido_em: 1780000001000}
                  ```
              }
            } as $verificacao

            precondition ($verificacao != null) {
              error_type = "notfound"
              error = "Recurso não encontrado."
            }

            conditional {
              if ($verificacao.status != "Novo") {
                util.set_header {
                  value = "HTTP/1.1 422 Unprocessable Entity"
                  duplicates = "replace"
                }

                precondition (false) {
                  error_type = "inputerror"
                  error = "Chamado inelegível para assunção."
                }
              }
              elseif ($verificacao.tecnico_id != null && $verificacao.tecnico_id != 0) {
                var.update $conflito {
                  value = true
                }
              }
              else {
                var $atribuido_em {
                  value = now
                  mock = {"assume válido": 1780000001000}
                }

                db.edit chamados {
                  field_name = "id"
                  field_value = $input.chamados_id
                  data = {
                    tecnico_id: $usuario.id,
                    atribuido_em: $atribuido_em,
                    ultima_atualizacao_em: $atribuido_em
                  }
                  mock = {
                    "assume válido": {id: 101, tecnico_id: 12, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000001000},
                    "idempotente": {id: 101, tecnico_id: 12, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000001000}
                  }
                } as $editado

              }
            }
          }
        }

        db.get chamados {
          field_name = "id"
          field_value = $input.chamados_id
          mock = {
            "assume válido": ```
              {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
              ```
            "idempotente": ```
              {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 12, atribuido_em: 1780000001000}
              ```
            "outro técnico": ```
              {id: 101, titulo: "Falha", status: "Novo", tecnico_id: 13, atribuido_em: 1780000001000}
              ```
          }
        } as $pos_edicao

        precondition ($pos_edicao != null) {
          error_type = "notfound"
          error = "Recurso não encontrado."
        }

        conditional {
          if ($pos_edicao.status != "Novo") {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "Chamado inelegível para assunção."
            }
          }
          elseif ($pos_edicao.tecnico_id == $usuario.id) {
            function.run "service_desk/obter_chamado_tecnico" {
              input = {usuarios_id: $usuario.id, chamados_id: $input.chamados_id}
            } as $detalhe

            var.update $resultado {
              value = $detalhe.chamado
            }
          }
          elseif ($pos_edicao.tecnico_id != null && $pos_edicao.tecnico_id != 0) {
            util.set_header {
              value = "HTTP/1.1 409 Conflict"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "Chamado já foi assumido por outro Técnico."
            }
          }
          elseif ($conflito) {
            util.set_header {
              value = "HTTP/1.1 409 Conflict"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "Chamado já foi assumido por outro Técnico."
            }
          }
          else {
            util.set_header {
              value = "HTTP/1.1 409 Conflict"
              duplicates = "replace"
            }

            precondition (false) {
              error_type = "inputerror"
              error = "A assunção não pôde ser confirmada após a edição."
            }
          }
        }
      }
    }
  }

  response = {chamado: $resultado}

  test "assume válido" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.chamado.status) { value = "Novo" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 12 }
  }

  test "idempotente" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.chamado.tecnico.id) { value = 12 }
    expect.to_equal ($response.chamado.atribuido_em) { value = 1780000001000 }
  }

  test "outro técnico" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_throw { exception = "" }
  }

  test "status inelegível" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_throw { exception = "" }
  }

  test "inexistente" {
    input = {usuarios_id: 12, chamados_id: 999}
    expect.to_throw { exception = "" }
  }

  guid = "miraAssumirTecnico01"
}
