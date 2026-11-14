// Consulta executiva somente leitura com dados persistidos.
function "indicadores/consultar_causas_recorrencia" {
  input {
    int usuarios_id { table = "usuarios" }
    timestamp t0
    timestamp t1
    text? visao?
    int? lojas_id?
    int? ativos_referencia_id?
    int? categorias_servico_id?
  }
  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {"causas diretoria vazia":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas gerente negado":{"id":4,"role":"gerente","deve_trocar_senha":false},"causas tecnico autorizado":{"id":4,"role":"tecnico","deve_trocar_senha":false},"causas administrador autorizado":{"id":4,"role":"administrador","deve_trocar_senha":false},"causas troca pendente":{"id":4,"role":"diretoria","deve_trocar_senha":true},"causas periodo invertido":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas futuro":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas visao invalida":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas hoje incompleto":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas loja invalida":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas totem invalido":{"id":4,"role":"diretoria","deve_trocar_senha":false},"causas categoria invalida":{"id":4,"role":"diretoria","deve_trocar_senha":false}}
    } as $diretoria
    precondition (($diretoria.role == "tecnico" || $diretoria.role == "diretoria" || $diretoria.role == "administrador") && $diretoria.deve_trocar_senha == false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    var $agora {
      value = now
      mock = {"causas diretoria vazia":1791999000000,"causas gerente negado":1791999000000,"causas tecnico autorizado":1791999000000,"causas administrador autorizado":1791999000000,"causas troca pendente":1791999000000,"causas periodo invertido":1791999000000,"causas futuro":1791999000000,"causas visao invalida":1791999000000,"causas hoje incompleto":1791999000000,"causas loja invalida":1791999000000,"causas totem invalido":1791999000000,"causas categoria invalida":1791999000000}
    }
    var $visao_hoje { value = $input.visao == "hoje" }
    precondition ($input.visao == null || $visao_hoje) {
      error_type = "inputerror"
      error = "Visão inválida."
    }
    precondition ($input.t0 < $input.t1) {
      error_type = "inputerror"
      error = "Período inválido."
    }
    conditional {
      if ($visao_hoje) {
        var $hoje_local { value = $agora|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
        var $amanha_local { value = ($agora|transform_timestamp:"+1 day":"America/Sao_Paulo")|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
        var $inicio_local { value = $input.t0|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo" }
        var $fim_local { value = $input.t1|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo" }
        precondition ($inicio_local == ($hoje_local ~ " 00:00:00") && $fim_local == ($amanha_local ~ " 00:00:00") && $input.t1 - $input.t0 == 86400000 && $input.t0 < $agora) {
          error_type = "inputerror"
          error = "Período inválido para Hoje."
        }
      }
      else {
        precondition ($input.t1 <= $agora) {
          error_type = "inputerror"
          error = "Período inválido."
        }
      }
    }
    var $observado_ate { value = $visao_hoje ? $agora : $input.t1 }

    conditional {
      if ($input.lojas_id != null) {
        precondition ($input.lojas_id > 0) {
          error_type = "inputerror"
          error = "Loja inválida."
        }
        db.get lojas {
          field_name = "id"
          field_value = $input.lojas_id
          mock = {"causas loja invalida": null}
        } as $filtro_validado
        precondition ($filtro_validado != null) {
          error_type = "inputerror"
          error = "Loja inválida."
        }
      }
    }
    conditional {
      if ($input.ativos_referencia_id != null) {
        precondition ($input.ativos_referencia_id > 0) {
          error_type = "inputerror"
          error = "Totem inválido."
        }
        db.get ativos_referencia {
          field_name = "id"
          field_value = $input.ativos_referencia_id
          mock = {"causas totem invalido": null}
        } as $filtro_validado
        precondition ($filtro_validado != null) {
          error_type = "inputerror"
          error = "Totem inválido."
        }
      }
    }
    conditional {
      if ($input.categorias_servico_id != null) {
        precondition ($input.categorias_servico_id > 0) {
          error_type = "inputerror"
          error = "Categoria inválida."
        }
        db.get categorias_servico {
          field_name = "id"
          field_value = $input.categorias_servico_id
          mock = {"causas categoria invalida": null}
        } as $filtro_validado
        precondition ($filtro_validado != null) {
          error_type = "inputerror"
          error = "Categoria inválida."
        }
      }
    }
    db.query chamados {
      where = ($db.chamados.criado_em == null || ($db.chamados.criado_em >= ($input.t0 - 2592000000) && $db.chamados.criado_em < $observado_ate)) && $db.chamados.ativos_referencia_id ==? $input.ativos_referencia_id && $db.chamados.categorias_servico_id ==? $input.categorias_servico_id
      sort = {chamados.criado_em: "asc"}
      return = {type: "list"}
      mock = {
        "causas diretoria vazia": [],
        "causas administrador autorizado": [],
        "causas tecnico autorizado": []
      }
    } as $chamados
    db.query categorias_servico {
      sort = {categorias_servico.id: "asc"}
      return = {type: "list"}
      mock = {
        "causas diretoria vazia": [],
        "causas administrador autorizado": [],
        "causas tecnico autorizado": []
      }
    } as $categorias
    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "causas diretoria vazia": [],
        "causas administrador autorizado": [],
        "causas tecnico autorizado": []
      }
    } as $totens
    db.query lojas {
      sort = {lojas.id: "asc"}
      return = {type: "list"}
      mock = {
        "causas diretoria vazia": [],
        "causas administrador autorizado": [],
        "causas tecnico autorizado": []
      }
    } as $lojas
    db.query historico_vinculos_totem_loja {
      sort = {historico_vinculos_totem_loja.efetivado_em: "asc"}
      return = {type: "list"}
      mock = {
        "causas diretoria vazia": [],
        "causas administrador autorizado": [],
        "causas tecnico autorizado": []
      }
    } as $vinculos
    var $totens_identificados { value = [] }
    foreach ($totens) {
      each as $totem {
        array.push $totens_identificados { value = {id: $totem.id, nome: $totem.nome_ativo|first_notempty:("Totem " ~ ($totem.id|to_text))} }
      }
    }
    function.run "indicadores/resumir_causas_recorrencia" {
      input = {t0: $input.t0, observado_ate: $observado_ate, lojas_id: $input.lojas_id, ativos_referencia_id: $input.ativos_referencia_id, categorias_servico_id: $input.categorias_servico_id, chamados: $chamados, categorias: $categorias, totens: $totens_identificados, lojas: $lojas, vinculos: $vinculos}
    } as $resumo
  }
  response = {
    periodo: {t0: $input.t0, t1: $input.t1, observado_ate: $observado_ate, fuso: "America/Sao_Paulo"},
    filtros: {lojas_id: $input.lojas_id, ativos_referencia_id: $input.ativos_referencia_id, categorias_servico_id: $input.categorias_servico_id},
    base: $resumo.base,
    top_lojas: $resumo.top_lojas,
    pareto: $resumo.pareto,
    recorrencia: $resumo.recorrencia
  }

  test "causas diretoria vazia" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1792033200000,"visao":"hoje"}
    expect.to_equal ($response.base.elegiveis) { value = 0 }
    expect.to_be_null ($response.recorrencia.percentual)
    expect.to_equal ($response.periodo.observado_ate) { value = 1791999000000 }
  }

  test "causas gerente negado" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "causas tecnico autorizado" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000}
    expect.to_equal ($response.base.elegiveis) { value = 0 }
  }


  test "causas administrador autorizado" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000}
    expect.to_equal ($response.base.elegiveis) { value = 0 }
  }


  test "causas troca pendente" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "causas periodo invertido" {
    input = {"usuarios_id":4,"t0":1791999000000,"t1":1791999000000}
    expect.to_throw { exception = "Período inválido." }
  }

  test "causas futuro" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1792033200000}
    expect.to_throw { exception = "Período inválido." }
  }

  test "causas visao invalida" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000,"visao":"semana"}
    expect.to_throw { exception = "Visão inválida." }
  }

  test "causas hoje incompleto" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000,"visao":"hoje"}
    expect.to_throw { exception = "Período inválido para Hoje." }
  }

  test "causas loja invalida" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000,"lojas_id":999999999}
    expect.to_throw { exception = "Loja inválida." }
  }

  test "causas totem invalido" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000,"ativos_referencia_id":999999999}
    expect.to_throw { exception = "Totem inválido." }
  }

  test "causas categoria invalida" {
    input = {"usuarios_id":4,"t0":1791946800000,"t1":1791999000000,"categorias_servico_id":999999999}
    expect.to_throw { exception = "Categoria inválida." }
  }
  guid = "vq4ZM7QY7MOMrs_Gor-vb0XzP-w"
}
