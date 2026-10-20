// Consulta somente leitura dos fatos operacionais recentes de um Totem.
function "service_desk/obter_detalhe_ativo_monitoramento" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int ativos_referencia_id {
      table = "ativos_referencia"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "detalhe completo": {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
        "colecoes vazias": {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
        "totem inexistente": {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
      }
    } as $usuario

    db.query ativos_referencia {
      join = {
        loja: {
          table: "lojas"
          type: "left"
          where: $db.ativos_referencia.lojas_id == $db.loja.id
        }
      }
      eval = {
        loja_id: $db.loja.id
        loja_nome: $db.loja.nome
      }
      where = $db.ativos_referencia.id == $input.ativos_referencia_id
      return = {type: "single"}
      mock = {
        "detalhe completo": {id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", loja_id: 3, loja_nome: "Loja Centro"}
        "colecoes vazias": {id: 2, nome_ativo: "Totem 02", tipo: "Totem", status_atual: "offline", loja_id: null, loja_nome: null}
        "totem inexistente": null
      }
    } as $ativo

    precondition ($ativo != null) {
      error_type = "notfound"
      error = "Recurso não encontrado."
    }

    db.query telemetria_equipamentos {
      where = $db.telemetria_equipamentos.ativos_referencia_id == $ativo.id
      sort = {telemetria_equipamentos.evento_timestamp: "desc"}
      return = {type: "single"}
      mock = {
        "detalhe completo": {id: 91, evento_timestamp: 1780000030000, uso_cpu: 12.5, uso_memoria: 42.25, temperatura: 31.75, status_rede: "online"}
        "colecoes vazias": null
      }
    } as $ultima_telemetria

    db.query telemetria_equipamentos {
      where = $db.telemetria_equipamentos.ativos_referencia_id == $ativo.id
      sort = {telemetria_equipamentos.evento_timestamp: "desc"}
      return = {type: "list", paging: {page: 1, per_page: 10}}
      mock = {
        "detalhe completo": {items: [{id: 91, evento_timestamp: 1780000030000, uso_cpu: 12.5, uso_memoria: 42.25, temperatura: 31.75, status_rede: "online"}, {id: 90, evento_timestamp: 1780000020000, uso_cpu: 10, uso_memoria: 40, temperatura: 30, status_rede: "online"}]}
        "colecoes vazias": {items: []}
      }
    } as $telemetrias_resultado

    db.query historico_disponibilidade_totens {
      where = $db.historico_disponibilidade_totens.ativos_referencia_id == $ativo.id
      sort = {historico_disponibilidade_totens.detectado_em: "desc"}
      return = {type: "list", paging: {page: 1, per_page: 10}}
      mock = {
        "detalhe completo": {items: [{id: 31, status: "online", detectado_em: 1780000040000, heartbeat_limite_minutos: 15}, {id: 30, status: "offline", detectado_em: 1780000010000, heartbeat_limite_minutos: 15}]}
        "colecoes vazias": {items: []}
      }
    } as $transicoes_resultado

    db.query chamados {
      join = {
        categoria: {
          table: "categorias_servico"
          type: "inner"
          where: $db.chamados.categorias_servico_id == $db.categoria.id
        }
      }
      eval = {
        categoria_id: $db.categoria.id
        categoria_nome: $db.categoria.nome
      }
      where = $db.chamados.ativos_referencia_id == $ativo.id && $db.chamados.origem == "automatico" && $db.chamados.criador_sistema == "bot_fiscalizacao" && $db.categoria.nome == "Totem Offline / Sem Heartbeat"
      sort = {chamados.criado_em: "desc"}
      return = {type: "list", paging: {page: 1, per_page: 10}}
      mock = {
        "detalhe completo": {items: [{id: 70, titulo: "Totem sem heartbeat", status: "Novo", prioridade: "Urgente", criado_em: 1780000015000, ultima_atualizacao_em: 1780000015000, categoria_id: 5, categoria_nome: "Totem Offline / Sem Heartbeat"}]}
        "colecoes vazias": {items: []}
      }
    } as $incidentes_resultado

    var $totem {
      value = {
        id: $ativo.id,
        nome_ativo: $ativo.nome_ativo,
        tipo: $ativo.tipo,
        loja: ($ativo.loja_id != null && $ativo.loja_id != 0) ? {id: $ativo.loja_id, nome: $ativo.loja_nome} : null,
        status_atual: $ativo.status_atual
      }
    }

    var $ultima_telemetria_dto {
      value = $ultima_telemetria != null ? {id: $ultima_telemetria.id, evento_timestamp: $ultima_telemetria.evento_timestamp, uso_cpu: $ultima_telemetria.uso_cpu, uso_memoria: $ultima_telemetria.uso_memoria, temperatura: $ultima_telemetria.temperatura, status_rede: $ultima_telemetria.status_rede} : null
    }

    var $telemetrias {
      value = $telemetrias_resultado.items|map:{id: $$.id, evento_timestamp: $$.evento_timestamp, uso_cpu: $$.uso_cpu, uso_memoria: $$.uso_memoria, temperatura: $$.temperatura, status_rede: $$.status_rede}
    }

    var $transicoes_disponibilidade {
      value = $transicoes_resultado.items|map:{id: $$.id, status: $$.status, detectado_em: $$.detectado_em, heartbeat_limite_minutos: $$.heartbeat_limite_minutos}
    }

    var $incidentes_automaticos {
      value = $incidentes_resultado.items|map:{id: $$.id, titulo: $$.titulo, status: $$.status, prioridade: $$.prioridade, criado_em: $$.criado_em, ultima_atualizacao_em: $$.ultima_atualizacao_em, categoria: {id: $$.categoria_id, nome: $$.categoria_nome}}
    }
  }

  response = {totem: $totem, ultima_telemetria: $ultima_telemetria_dto, telemetrias: $telemetrias, transicoes_disponibilidade: $transicoes_disponibilidade, incidentes_automaticos: $incidentes_automaticos}

  test "detalhe completo" {
    input = {usuarios_id: 12, ativos_referencia_id: 1}
    expect.to_equal ($response.totem) { value = {id: 1, nome_ativo: "Totem 01", tipo: "Totem", loja: {id: 3, nome: "Loja Centro"}, status_atual: "online"} }
    expect.to_equal ($response.ultima_telemetria.id) { value = 91 }
    expect.to_equal ($response.telemetrias) { value = [{id: 91, evento_timestamp: 1780000030000, uso_cpu: 12.5, uso_memoria: 42.25, temperatura: 31.75, status_rede: "online"}, {id: 90, evento_timestamp: 1780000020000, uso_cpu: 10, uso_memoria: 40, temperatura: 30, status_rede: "online"}] }
    expect.to_equal ($response.transicoes_disponibilidade) { value = [{id: 31, status: "online", detectado_em: 1780000040000, heartbeat_limite_minutos: 15}, {id: 30, status: "offline", detectado_em: 1780000010000, heartbeat_limite_minutos: 15}] }
    expect.to_equal ($response.incidentes_automaticos) { value = [{id: 70, titulo: "Totem sem heartbeat", status: "Novo", prioridade: "Urgente", criado_em: 1780000015000, ultima_atualizacao_em: 1780000015000, categoria: {id: 5, nome: "Totem Offline / Sem Heartbeat"}}] }
  }

  test "colecoes vazias" {
    input = {usuarios_id: 12, ativos_referencia_id: 2}
    expect.to_be_null ($response.ultima_telemetria)
    expect.to_be_empty ($response.telemetrias)
    expect.to_be_empty ($response.transicoes_disponibilidade)
    expect.to_be_empty ($response.incidentes_automaticos)
  }

  test "totem inexistente" {
    input = {usuarios_id: 12, ativos_referencia_id: 999}
    expect.to_throw {
      exception = ""
    }
  }
  guid = "b6R1z1JzsRfpeP-5ZA5ecZ_fRfU"
}
