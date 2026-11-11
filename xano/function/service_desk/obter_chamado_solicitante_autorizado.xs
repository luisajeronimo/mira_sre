// Localiza chamado pelo vínculo de solicitante da identidade autenticada.
// O vínculo integra o filtro: inexistente, de outra pessoa ou sem solicitante
// recebem a mesma resposta de recurso não encontrado. A Loja não é consultada.
function "service_desk/obter_chamado_solicitante_autorizado" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id  : $input.usuarios_id
        gerente      : true
        tecnico      : true
        diretoria    : true
        administrador: true
      }
      mock = {
        "autoriza solicitante associado": {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 2, deve_trocar_senha: false}
        "autoriza tecnico solicitante"  : {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null, deve_trocar_senha: false}
        "nega chamado sem vinculo"      : {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1, deve_trocar_senha: false}
      }
    } as $usuario

    db.query chamados {
      where = $db.chamados.id == $input.chamados_id && $db.chamados.solicitante_id == $usuario.id
      return = {type: "single"}
      mock = {
        "autoriza solicitante associado": {id: 101, status: "Resolvido", solicitante_id: 8}
        "autoriza tecnico solicitante"  : {id: 102, status: "Novo", solicitante_id: 12}
        "nega chamado sem vinculo"      : null
      }
    } as $registro

    precondition ($registro != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    // Defesa em profundidade sobre o mesmo vínculo usado no filtro.
    precondition ($registro.solicitante_id != null && $registro.solicitante_id == $usuario.id) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }
  }

  response = {id: $registro.id, status: $registro.status}

  test "autoriza solicitante associado" {
    input = {usuarios_id: 8, chamados_id: 101}

    expect.to_equal ($response.id) {
      value = 101
    }
  }

  test "autoriza tecnico solicitante" {
    input = {usuarios_id: 12, chamados_id: 102}

    expect.to_equal ($response.id) {
      value = 102
    }
  }

  test "nega chamado sem vinculo" {
    input = {usuarios_id: 8, chamados_id: 103}

    expect.to_throw {
      exception = ""
    }
  }

  guid = "miraChamadoSolicitanteAutorizado01"
}
