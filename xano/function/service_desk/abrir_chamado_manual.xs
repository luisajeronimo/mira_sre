// Valida e cria um chamado manual sob autoridade exclusiva do Xano.
function "service_desk/abrir_chamado_manual" {
  input {
    int usuarios_id {
      table = "usuarios"
    }

    int ativos_referencia_id?
    int categorias_servico_id?
    text prioridade? filters=trim
    text titulo? filters=trim
    text descricao? filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true, administrador: true}
      mock = {
        "cria chamado manual": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "administrador abre em outra loja": {id: 12, nome: "Administrador de Teste", email: "admin@example.test", role: "administrador", lojas_id: null}
        "rejeita titulo ausente": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita titulo somente espacos": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita descricao vazia": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita descricao somente espacos": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita prioridade invalida": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita ativo inexistente": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita ativo de outra loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita categoria inexistente": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita categoria bloqueada": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita categoria sem sla": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
      }
    } as $usuario

    precondition ($usuario.role == "administrador" || $usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    var $entrada_basica_valida {
      value = $input.ativos_referencia_id != null && $input.ativos_referencia_id > 0 && $input.categorias_servico_id != null && $input.categorias_servico_id > 0 && $input.titulo != null && $input.titulo != "" && $input.descricao != null && $input.descricao != ""
    }

    conditional {
      if (!$entrada_basica_valida) {
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

    var $prioridade_valida {
      value = $input.prioridade == "Baixa" || $input.prioridade == "Média" || $input.prioridade == "Alta" || $input.prioridade == "Urgente"
    }

    conditional {
      if (!$prioridade_valida) {
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

    db.get ativos_referencia {
      field_name = "id"
      field_value = $input.ativos_referencia_id
      mock = {
        "cria chamado manual": ```
          {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 1}
          ```
        "administrador abre em outra loja": {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 2}
        "rejeita ativo inexistente": null
        "rejeita ativo de outra loja": ```
          {id: 8, nome_ativo: "Totem 08", tipo: "Totem", status_atual: "online", lojas_id: 2}
          ```
        "rejeita categoria inexistente": ```
          {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 1}
          ```
        "rejeita categoria bloqueada": ```
          {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 1}
          ```
        "rejeita categoria sem sla": ```
          {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 1}
          ```
      }
    } as $ativo

    precondition ($ativo != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    precondition ($ativo.lojas_id != null && ($usuario.role == "administrador" || $ativo.lojas_id == $usuario.lojas_id)) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.get categorias_servico {
      field_name = "id"
      field_value = $input.categorias_servico_id
      mock = {
        "cria chamado manual": ```
          {id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, desc: "Falha percebida", permite_abertura_manual: true}
          ```
        "administrador abre em outra loja": {id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, permite_abertura_manual: true}
        "rejeita categoria inexistente": null
        "rejeita categoria bloqueada": ```
          {id: 8, nome: "Alta Temperatura", tipo_itil: "Incidente", sla_horas: 2, desc: "Telemetria", permite_abertura_manual: false}
          ```
        "rejeita categoria sem sla": ```
          {id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: null, desc: "Falha percebida", permite_abertura_manual: true}
          ```
      }
    } as $categoria

    precondition ($categoria != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    var $categoria_valida {
      value = $categoria.permite_abertura_manual == true && $categoria.sla_horas != null
    }

    conditional {
      if (!$categoria_valida) {
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

    db.transaction {
      stack {
        db.get ativos_referencia {
          field_name = "id"
          field_value = $ativo.id
          lock = true
          mock = {
            "cria chamado manual": ```
              {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 1}
              ```
            "administrador abre em outra loja": {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", lojas_id: 2}
          }
        } as $ativo_atual
        precondition ($ativo_atual != null && $ativo_atual.lojas_id != null && ($usuario.role == "administrador" || $ativo_atual.lojas_id == $usuario.lojas_id)) {
          error_type = "accessdenied"
          error = "Acesso não autorizado."
        }
        var $criado_em {
          value = now
          mock = {"cria chamado manual": 1780000000000}
        }
        db.query historico_vinculos_totem_loja {
          where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $ativo_atual.id
          sort = {historico_vinculos_totem_loja.efetivado_em: "desc"}
          return = {type: "single"}
          mock = {
            "cria chamado manual": {id: 1, loja_destino_id: 1, tipo: "criacao", efetivado_em: 1779999999999}
            "administrador abre em outra loja": {id: 2, loja_destino_id: 2, tipo: "criacao", efetivado_em: 1779999999999}
          }
        } as $ultimo_vinculo
        conditional {
          if ($ultimo_vinculo == null) {
            // O vínculo atual só comprova o instante deste novo chamado.
            db.add historico_vinculos_totem_loja {
              data = {
                ativos_referencia_id: $ativo_atual.id
                loja_origem_id: null
                loja_destino_id: $ativo_atual.lojas_id
                tipo: "marco"
                efetivado_em: $criado_em
              }
            } as $marco
          }
        }
        db.add chamados {
          data = {
            titulo               : $input.titulo
            descricao            : $input.descricao
            status               : "Novo"
            prioridade           : $input.prioridade
            origem               : "manual"
            criado_em            : $criado_em
            ultima_atualizacao_em: $criado_em
            sla_horas_aplicado   : $categoria.sla_horas
            solicitante_id       : $usuario.id
            tecnico_id           : null
            categorias_servico_id: $categoria.id
            ativos_referencia_id : $ativo_atual.id
          }
          mock = {
            "cria chamado manual": ```
              {id: 101, titulo: "Falha observada", descricao: "Totem não conecta", status: "Novo", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 2, solicitante_id: 8, tecnico_id: null, categorias_servico_id: 2, ativos_referencia_id: 1}
              ```
            "administrador abre em outra loja": {id: 102, titulo: "Falha observada", descricao: "Totem não conecta", status: "Novo", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 2, solicitante_id: 12, tecnico_id: null, categorias_servico_id: 2, ativos_referencia_id: 1}
          }
        } as $novo_chamado
        precondition ($novo_chamado.ativos_referencia_id == $ativo_atual.id && $novo_chamado.categorias_servico_id == $categoria.id) {
          error_type = "inputerror"
          error = "Chamado não concluído."
        }
      }
    }

    var $chamado {
      value = {
        id: $novo_chamado.id,
        titulo: $novo_chamado.titulo,
        descricao: $novo_chamado.descricao,
        status: $novo_chamado.status,
        prioridade: $novo_chamado.prioridade,
        origem: $novo_chamado.origem,
        criador_sistema: $novo_chamado.criador_sistema,
        criado_em: $novo_chamado.criado_em,
        ultima_atualizacao_em: $novo_chamado.ultima_atualizacao_em,
        sla_horas_aplicado: $novo_chamado.sla_horas_aplicado,
        ativo: {id: $ativo_atual.id, nome_ativo: $ativo_atual.nome_ativo},
        categoria: {id: $categoria.id, nome: $categoria.nome},
        solicitante: {id: $usuario.id, nome: $usuario.nome},
        tecnico: null
      }
    }
  }

  response = {chamado: $chamado}

  test "cria chamado manual" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", titulo: "Falha observada", descricao: "Totem não conecta"}
    expect.to_equal ($response.chamado.status) { value = "Novo" }
    expect.to_equal ($response.chamado.origem) { value = "manual" }
    expect.to_equal ($response.chamado.solicitante.id) { value = 8 }
    expect.to_be_null ($response.chamado.criador_sistema)
    expect.to_equal ($response.chamado.sla_horas_aplicado) { value = 2 }
    expect.to_equal ($response.chamado.ultima_atualizacao_em) { value = 1780000000000 }
    expect.to_be_null ($response.chamado.tecnico)
    expect.to_not_be_defined ($response.chamado.created_at)
  }

  test "administrador abre em outra loja" {
    input = {usuarios_id: 12, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", titulo: "Falha observada", descricao: "Totem não conecta"}
    expect.to_equal ($response.chamado.solicitante.id) { value = 12 }
    expect.to_equal ($response.chamado.ativo.id) { value = 1 }
    expect.to_equal ($response.chamado.origem) { value = "manual" }
  }

  test "rejeita titulo ausente" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita titulo somente espacos" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", titulo: "   ", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita descricao vazia" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", titulo: "Título", descricao: ""}
    expect.to_throw { exception = "" }
  }

  test "rejeita descricao somente espacos" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", titulo: "Título", descricao: "   "}
    expect.to_throw { exception = "" }
  }

  test "rejeita prioridade invalida" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Crítica", titulo: "Título", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita ativo inexistente" {
    input = {usuarios_id: 8, ativos_referencia_id: 999, categorias_servico_id: 2, prioridade: "Alta", titulo: "Título", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita ativo de outra loja" {
    input = {usuarios_id: 8, ativos_referencia_id: 8, categorias_servico_id: 2, prioridade: "Alta", titulo: "Título", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita categoria inexistente" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 999, prioridade: "Alta", titulo: "Título", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita categoria bloqueada" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 8, prioridade: "Alta", titulo: "Título", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }

  test "rejeita categoria sem sla" {
    input = {usuarios_id: 8, ativos_referencia_id: 1, categorias_servico_id: 2, prioridade: "Alta", titulo: "Título", descricao: "Descrição"}
    expect.to_throw { exception = "" }
  }
  guid = "uIIQIaF1GWw4rvly1S-uzf1sK50"
}
