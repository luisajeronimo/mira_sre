// Resumo global persistido dos Totens para a jornada autorizada de monitoramento.
function "service_desk/listar_ativos_monitoramento" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "resumo completo": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null, deve_trocar_senha: false}
          ```
        "timestamps ausentes": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null, deve_trocar_senha: false}
          ```
        "diretoria consulta monitoramento": ```
          {id: 13, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null, deve_trocar_senha: false}
          ```
        "administrador consulta monitoramento": ```
          {id: 14, nome: "Administrador", email: "administrador@example.test", role: "administrador", lojas_id: null, deve_trocar_senha: false}
          ```
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
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "resumo completo": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", loja_id: 3, loja_nome: "Loja Centro"}]
          ```
        "timestamps ausentes": ```
          [{id: 2, nome_ativo: "Totem 02", tipo: "Totem", status_atual: "offline", loja_id: null, loja_nome: null}]
          ```
        "diretoria consulta monitoramento": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", loja_id: 3, loja_nome: "Loja Centro"}]
          ```
        "administrador consulta monitoramento": ```
          [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", status_atual: "online", loja_id: 3, loja_nome: "Loja Centro"}]
          ```
      }
    } as $ativos

    var $items {
      value = []
    }

    foreach ($ativos) {
      each as $ativo {
        db.query telemetria_equipamentos {
          where = $db.telemetria_equipamentos.ativos_referencia_id == $ativo.id
          sort = {telemetria_equipamentos.evento_timestamp: "desc"}
          return = {type: "single"}
          mock = {
            "resumo completo": {id: 91, evento_timestamp: 1780000010000}
            "timestamps ausentes": null
            "diretoria consulta monitoramento": {id: 91, evento_timestamp: 1780000010000}
            "administrador consulta monitoramento": {id: 91, evento_timestamp: 1780000010000}
          }
        } as $ultima_telemetria

        db.query historico_disponibilidade_totens {
          where = $db.historico_disponibilidade_totens.ativos_referencia_id == $ativo.id
          sort = {historico_disponibilidade_totens.detectado_em: "desc"}
          return = {type: "single"}
          mock = {
            "resumo completo": {id: 31, detectado_em: 1780000020000}
            "timestamps ausentes": null
            "diretoria consulta monitoramento": {id: 31, detectado_em: 1780000020000}
            "administrador consulta monitoramento": {id: 31, detectado_em: 1780000020000}
          }
        } as $ultima_transicao

        array.push $items {
          value = {
            id: $ativo.id,
            nome_ativo: $ativo.nome_ativo,
            tipo: $ativo.tipo,
            loja: ($ativo.loja_id != null && $ativo.loja_id != 0) ? {id: $ativo.loja_id, nome: $ativo.loja_nome} : null,
            status_atual: $ativo.status_atual,
            ultima_telemetria_em: $ultima_telemetria != null ? $ultima_telemetria.evento_timestamp : null,
            ultima_transicao_disponibilidade_em: $ultima_transicao != null ? $ultima_transicao.detectado_em : null
          }
        }
      }
    }
  }

  response = {items: $items}

  test "resumo completo" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", loja: {id: 3, nome: "Loja Centro"}, status_atual: "online", ultima_telemetria_em: 1780000010000, ultima_transicao_disponibilidade_em: 1780000020000}]
    }
  }

  test "timestamps ausentes" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [{id: 2, nome_ativo: "Totem 02", tipo: "Totem", loja: null, status_atual: "offline", ultima_telemetria_em: null, ultima_transicao_disponibilidade_em: null}]
    }
  }

  test "diretoria consulta monitoramento" {
    input = {usuarios_id: 13}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", loja: {id: 3, nome: "Loja Centro"}, status_atual: "online", ultima_telemetria_em: 1780000010000, ultima_transicao_disponibilidade_em: 1780000020000}]
    }
  }

  test "administrador consulta monitoramento" {
    input = {usuarios_id: 14}
    expect.to_equal ($response.items) {
      value = [{id: 1, nome_ativo: "Totem 01", tipo: "Totem", loja: {id: 3, nome: "Loja Centro"}, status_atual: "online", ultima_telemetria_em: 1780000010000, ultima_transicao_disponibilidade_em: 1780000020000}]
    }
  }

  guid = "Yd84hQh-Bb7WP_h_93GqsR6mrYo"
}
