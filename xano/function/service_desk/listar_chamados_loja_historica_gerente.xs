// Registros de chamados que o Gerente autenticado pode ler pelo contrato
// genérico `GET /chamados` (correção C-1). O escopo é a Loja comprovada na
// abertura de cada chamado (`resolver_loja_totem_no_instante`); a Loja atual
// do Totem não é lida nem usada como fallback. Sem vínculo demonstrável, o
// chamado não é disponibilizado ao Gerente.
function "service_desk/listar_chamados_loja_historica_gerente" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "inclui chamado da loja historica com totem transferido": {id: 8, role: "gerente", lojas_id: 1}
        "exclui chamado de outra loja historica"                : {id: 8, role: "gerente", lojas_id: 1}
        "exclui chamado sem vinculo historico"                  : {id: 8, role: "gerente", lojas_id: 1}
        "exclui chamado sem totem"                              : {id: 8, role: "gerente", lojas_id: 1}
        "exclui chamado sem criado em"                          : {id: 8, role: "gerente", lojas_id: 1}
        "lista vazia"                                           : {id: 8, role: "gerente", lojas_id: 1}
        "rejeita gerente sem loja"                              : {id: 8, role: "gerente", lojas_id: null}
      }
    } as $usuario

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    // Sem join com ativos_referencia: a Loja atual do Totem não participa.
    db.query chamados {
      sort = {chamados.id: "asc"}
      return = {type: "list"}
      mock = {
        "inclui chamado da loja historica com totem transferido": [{id: 101, titulo: "Aberto na Loja 1", status: "Novo", ativos_referencia_id: 1, criado_em: 1780000000000}]
        "exclui chamado de outra loja historica"                : [{id: 102, titulo: "Aberto na Loja 2", status: "Novo", ativos_referencia_id: 2, criado_em: 1780000000000}]
        "exclui chamado sem vinculo historico"                  : [{id: 103, titulo: "Legado", status: "Novo", ativos_referencia_id: 3, criado_em: 1780000000000}]
        "exclui chamado sem totem"                              : [{id: 104, titulo: "Sem Totem", status: "Novo", ativos_referencia_id: null, criado_em: 1780000000000}]
        "exclui chamado sem criado em"                          : [{id: 105, titulo: "Sem data", status: "Novo", ativos_referencia_id: 1, criado_em: null}]
        "lista vazia"                                           : []
      }
    } as $chamados

    var $autorizados {
      value = []
    }

    foreach ($chamados) {
      each as $chamado {
        var $loja_historica_id {
          value = null
        }

        conditional {
          if ($chamado.ativos_referencia_id != null && $chamado.ativos_referencia_id != 0 && $chamado.criado_em != null) {
            function.run "administracao/resolver_loja_totem_no_instante" {
              input = {
                ativos_referencia_id: $chamado.ativos_referencia_id
                instante            : $chamado.criado_em
              }

              mock = {
                "inclui chamado da loja historica com totem transferido": {lojas_id: 1}
                "exclui chamado de outra loja historica"                : {lojas_id: 2}
                "exclui chamado sem vinculo historico"                  : {lojas_id: null}
              }
            } as $historico

            var.update $loja_historica_id {
              value = $historico.lojas_id
            }
          }
        }

        conditional {
          if ($loja_historica_id != null && $loja_historica_id == $usuario.lojas_id) {
            array.push $autorizados {
              value = $chamado
            }
          }
        }
      }
    }
  }

  response = $autorizados

  // Totem hoje em outra Loja: o chamado aberto na Loja 1 continua da Loja 1.
  test "inclui chamado da loja historica com totem transferido" {
    input = {usuarios_id: 8}

    expect.to_equal ($response) {
      value = [{id: 101, titulo: "Aberto na Loja 1", status: "Novo", ativos_referencia_id: 1, criado_em: 1780000000000}]
    }
  }

  // Regressão C-1: o Totem pode estar hoje na Loja 1, mas o chamado foi aberto na Loja 2.
  test "exclui chamado de outra loja historica" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response)
  }

  test "exclui chamado sem vinculo historico" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response)
  }

  test "exclui chamado sem totem" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response)
  }

  test "exclui chamado sem criado em" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response)
  }

  test "lista vazia" {
    input = {usuarios_id: 8}

    expect.to_be_empty ($response)
  }

  test "rejeita gerente sem loja" {
    input = {usuarios_id: 8}

    expect.to_throw {
      exception = "Acesso não autorizado."
    }
  }

  guid = "miraChamadosGenericosLojaHistoricaGerente01"
}
