// Retorna o detalhe global, somente leitura, para um Técnico autenticado.
function "service_desk/obter_chamado_tecnico" {
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
        "retorna detalhe": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "retorna detalhe legado": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "retorna detalhe automático": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "rejeita inexistente": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    db.query chamados {
      join = {
        ativo: {
          table: "ativos_referencia"
          type: "left"
          where: $db.chamados.ativos_referencia_id == $db.ativo.id
        }
        categoria: {
          table: "categorias_servico"
          type: "left"
          where: $db.chamados.categorias_servico_id == $db.categoria.id
        }
        solicitante: {
          table: "usuarios"
          type: "left"
          where: $db.chamados.solicitante_id == $db.solicitante.id
        }
        tecnico: {
          table: "usuarios"
          type: "left"
          where: $db.chamados.tecnico_id == $db.tecnico.id
        }
      }
      eval = {
        ativo_id: $db.ativo.id
        ativo_nome: $db.ativo.nome_ativo
        categoria_id: $db.categoria.id
        categoria_nome: $db.categoria.nome
        solicitante_usuario_id: $db.solicitante.id
        solicitante_nome: $db.solicitante.nome
        tecnico_usuario_id: $db.tecnico.id
        tecnico_nome: $db.tecnico.nome
      }
      where = $db.chamados.id == $input.chamados_id
      return = {type: "single"}
      mock = {
        "retorna detalhe": ```
          {id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
          ```
        "retorna detalhe legado": ```
          {id: 16, titulo: "Legado", descricao: null, status: "Novo", prioridade: "Urgente", origem: null, criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: null, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 1, categoria_nome: "Totem Offline / Sem Heartbeat", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: null, tecnico_nome: null}
          ```
        "retorna detalhe automático": ```
          {id: 17, titulo: "Totem sem heartbeat", descricao: null, status: "Novo", prioridade: "Urgente", origem: "automatico", criador_sistema: "bot_fiscalizacao", criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 1, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 1, categoria_nome: "Totem Offline / Sem Heartbeat", solicitante_usuario_id: null, solicitante_nome: null, tecnico_usuario_id: null, tecnico_nome: null}
          ```
        "rejeita inexistente": null
      }
    } as $registro

    precondition ($registro != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    function.run "service_desk/construir_dto_chamado_tecnico" {
      input = {registro: $registro}
    } as $chamado
  }

  response = {chamado: $chamado}

  test "retorna detalhe" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.chamado.id) { value = 101 }
    expect.to_be_null ($response.chamado.criador_sistema)
    expect.to_be_null ($response.chamado.tecnico)
    expect.to_be_null ($response.chamado.atribuido_em)
  }

  test "retorna detalhe legado" {
    input = {usuarios_id: 12, chamados_id: 16}
    expect.to_be_null ($response.chamado.descricao)
    expect.to_be_null ($response.chamado.origem)
    expect.to_be_null ($response.chamado.criador_sistema)
    expect.to_be_null ($response.chamado.atribuido_em)
  }

  test "retorna detalhe automático" {
    input = {usuarios_id: 12, chamados_id: 17}
    expect.to_equal ($response.chamado.origem) { value = "automatico" }
    expect.to_be_null ($response.chamado.solicitante)
    expect.to_equal ($response.chamado.criador_sistema) { value = "bot_fiscalizacao" }
  }

  test "rejeita inexistente" {
    input = {usuarios_id: 12, chamados_id: 999}
    expect.to_throw { exception = "" }
  }

  guid = "miraDetalheTecnico01"
}
