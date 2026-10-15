// Retorna o detalhe global e sua timeline para os perfis autorizados.
function "service_desk/obter_chamado_tecnico" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
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
        "retorna timeline cronológica com legado": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "retorna detalhe Diretoria": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "retorna detalhe Administrador": ```
          {id: 13, nome: "Administradora", email: "admin@example.test", role: "administrador", lojas_id: null}
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
        "retorna timeline cronológica com legado": ```
          {id: 101, titulo: "Falha", descricao: "Descrição", status: "Em Atendimento", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: 1780000002000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: 12, tecnico_nome: "Técnico"}
          ```
        "retorna detalhe Diretoria": ```
          {id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
          ```
        "retorna detalhe Administrador": ```
          {id: 101, titulo: "Falha", descricao: "Descrição", status: "Novo", prioridade: "Alta", origem: "manual", criador_sistema: null, criado_em: 1780000000000, ultima_atualizacao_em: 1780000000000, sla_horas_aplicado: 2, atribuido_em: null, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede", solicitante_usuario_id: 8, solicitante_nome: "Gerente", tecnico_usuario_id: null, tecnico_nome: null}
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

    db.query interacoes_chamado {
      join = {
        autor: {
          table: "usuarios"
          type: "left"
          where: $db.interacoes_chamado.usuarios_id == $db.autor.id
        }
        tecnico_anterior: {
          table: "usuarios"
          type: "left"
          where: $db.interacoes_chamado.tecnico_anterior_id == $db.tecnico_anterior.id
        }
        tecnico_novo: {
          table: "usuarios"
          type: "left"
          where: $db.interacoes_chamado.tecnico_novo_id == $db.tecnico_novo.id
        }
      }
      eval = {
        autor_id: $db.autor.id
        autor_nome: $db.autor.nome
        tecnico_anterior_nome: $db.tecnico_anterior.nome
        tecnico_novo_nome: $db.tecnico_novo.nome
      }
      where = $db.interacoes_chamado.chamados_id == $registro.id
      sort = {interacoes_chamado.id: "asc"}
      return = {type: "list"}
      mock = {
        "retorna detalhe": []
        "retorna detalhe legado": []
        "retorna detalhe automático": []
        "retorna timeline cronológica com legado": ```
          [
            {id: 11, mensagem: "Comentário legado", criado_em: null, created_at: 1780000001000, tipo_evento: null, visibilidade: "publica", chamados_id: 101, usuarios_id: 8, autor_id: 8, autor_nome: "Gerente", tecnico_anterior_id: null, tecnico_anterior_nome: null, tecnico_novo_id: null, tecnico_novo_nome: null},
            {id: 12, mensagem: "Comentário recente", criado_em: 1780000004000, created_at: 1780000004001, tipo_evento: "comentario", visibilidade: "interna", chamados_id: 101, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", tecnico_anterior_id: null, tecnico_anterior_nome: null, tecnico_novo_id: null, tecnico_novo_nome: null},
            {id: 13, mensagem: null, criado_em: 1780000002000, created_at: 1780000002001, tipo_evento: "atribuicao", visibilidade: "interna", chamados_id: 101, usuarios_id: 12, autor_id: 12, autor_nome: "Técnico", tecnico_anterior_id: null, tecnico_anterior_nome: null, tecnico_novo_id: 12, tecnico_novo_nome: "Técnico"},
            {id: 14, mensagem: null, criado_em: 1780000002000, created_at: 1780000002002, tipo_evento: "reatribuicao", visibilidade: "interna", chamados_id: 101, usuarios_id: 4, autor_id: 4, autor_nome: "Diretoria", tecnico_anterior_id: 12, tecnico_anterior_nome: "Técnico", tecnico_novo_id: 10, tecnico_novo_nome: "Outro Técnico"}
          ]
          ```
        "retorna detalhe Diretoria": []
        "retorna detalhe Administrador": []
      }
    } as $interacoes

    var $eventos {
      value = $interacoes|map:{
        id: $$.id,
        tipo: ($$.tipo_evento == null || $$.tipo_evento == "") ? "comentario" : $$.tipo_evento,
        conteudo: $$.mensagem,
        visibilidade: $$.visibilidade,
        criado_em: ($$.criado_em ?? $$.created_at),
        ordenacao: (($$.criado_em ?? $$.created_at)|to_text) ~ "-" ~ ($$.id|to_text),
        autor: ($$.autor_id != null && $$.autor_id != 0) ? {id: $$.autor_id, nome: $$.autor_nome} : null,
        tecnico_anterior: ($$.tecnico_anterior_id != null && $$.tecnico_anterior_id != 0) ? {id: $$.tecnico_anterior_id, nome: $$.tecnico_anterior_nome} : null,
        tecnico_novo: ($$.tecnico_novo_id != null && $$.tecnico_novo_id != 0) ? {id: $$.tecnico_novo_id, nome: $$.tecnico_novo_nome} : null
      }
    }

    // A chave natural combina o instante efetivo e o id, garantindo o desempate.
    var $eventos_ordenados {
      value = $eventos|sort:"ordenacao":"natural":true
    }

    var $timeline {
      value = $eventos_ordenados|map:{
        id: $$.id,
        tipo: $$.tipo,
        conteudo: $$.conteudo,
        visibilidade: $$.visibilidade,
        criado_em: $$.criado_em,
        autor: $$.autor,
        tecnico_anterior: $$.tecnico_anterior,
        tecnico_novo: $$.tecnico_novo
      }
    }

    db.query usuarios {
      where = $db.usuarios.role == "tecnico"
      sort = {usuarios.nome: "asc", usuarios.id: "asc"}
      return = {type: "list"}
      mock = {
        "retorna detalhe": [{id: 10, nome: "Outro Técnico"}, {id: 12, nome: "Técnico"}]
        "retorna detalhe legado": []
        "retorna detalhe automático": []
        "retorna timeline cronológica com legado": [{id: 10, nome: "Outro Técnico"}, {id: 12, nome: "Técnico"}]
        "retorna detalhe Diretoria": [{id: 12, nome: "Técnico"}]
        "retorna detalhe Administrador": [{id: 12, nome: "Técnico"}]
      }
    } as $tecnicos_registros

    var $tecnicos {
      value = $tecnicos_registros|map:{id: $$.id, nome: $$.nome}
    }
  }

  response = {chamado: $chamado, timeline: $timeline, tecnicos: $tecnicos}

  test "retorna detalhe" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.chamado.id) { value = 101 }
    expect.to_be_null ($response.chamado.criador_sistema)
    expect.to_be_null ($response.chamado.tecnico)
    expect.to_be_null ($response.chamado.atribuido_em)
    expect.to_be_empty ($response.timeline)
    expect.to_equal ($response.tecnicos) { value = [{id: 10, nome: "Outro Técnico"}, {id: 12, nome: "Técnico"}] }
  }

  test "retorna detalhe legado" {
    input = {usuarios_id: 12, chamados_id: 16}
    expect.to_be_null ($response.chamado.descricao)
    expect.to_be_null ($response.chamado.origem)
    expect.to_be_null ($response.chamado.criador_sistema)
    expect.to_be_null ($response.chamado.atribuido_em)
    expect.to_be_empty ($response.timeline)
  }

  test "retorna detalhe automático" {
    input = {usuarios_id: 12, chamados_id: 17}
    expect.to_equal ($response.chamado.origem) { value = "automatico" }
    expect.to_be_null ($response.chamado.solicitante)
    expect.to_equal ($response.chamado.criador_sistema) { value = "bot_fiscalizacao" }
  }

  test "retorna timeline cronológica com legado" {
    input = {usuarios_id: 12, chamados_id: 101}
    expect.to_equal ($response.timeline) {
      value = [
        {id: 11, tipo: "comentario", conteudo: "Comentário legado", visibilidade: "publica", criado_em: 1780000001000, autor: {id: 8, nome: "Gerente"}, tecnico_anterior: null, tecnico_novo: null},
        {id: 13, tipo: "atribuicao", conteudo: null, visibilidade: "interna", criado_em: 1780000002000, autor: {id: 12, nome: "Técnico"}, tecnico_anterior: null, tecnico_novo: {id: 12, nome: "Técnico"}},
        {id: 14, tipo: "reatribuicao", conteudo: null, visibilidade: "interna", criado_em: 1780000002000, autor: {id: 4, nome: "Diretoria"}, tecnico_anterior: {id: 12, nome: "Técnico"}, tecnico_novo: {id: 10, nome: "Outro Técnico"}},
        {id: 12, tipo: "comentario", conteudo: "Comentário recente", visibilidade: "interna", criado_em: 1780000004000, autor: {id: 12, nome: "Técnico"}, tecnico_anterior: null, tecnico_novo: null}
      ]
    }
  }

  test "retorna detalhe Diretoria" {
    input = {usuarios_id: 4, chamados_id: 101}
    expect.to_equal ($response.chamado.id) { value = 101 }
  }

  test "retorna detalhe Administrador" {
    input = {usuarios_id: 13, chamados_id: 101}
    expect.to_equal ($response.chamado.id) { value = 101 }
  }

  test "rejeita inexistente" {
    input = {usuarios_id: 12, chamados_id: 999}
    expect.to_throw { exception = "" }
  }

  guid = "miraDetalheTecnico01"
}
