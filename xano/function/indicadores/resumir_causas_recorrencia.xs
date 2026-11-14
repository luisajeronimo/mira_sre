// Resume fatos persistidos sem gravar agregados ou reconstruir histórico.
function "indicadores/resumir_causas_recorrencia" {
  input {
    timestamp t0
    timestamp observado_ate
    int? lojas_id?
    int? ativos_referencia_id?
    int? categorias_servico_id?
    json[] chamados
    json[] categorias
    json[] totens
    json[] lojas
    json[] vinculos
  }

  stack {
    var $elegiveis { value = 0 }
    var $recorrentes { value = 0 }
    var $cancelados { value = 0 }
    var $requisicoes { value = 0 }
    var $inconsistentes { value = 0 }
    var $sem_data { value = 0 }
    var $sem_loja { value = 0 }
    var $grupos_loja { value = {} }
    var $grupos_totem { value = {} }
    var $grupos_categoria { value = {} }
    var $ultimos { value = {} }
    var $ordenados { value = $input.chamados|sort:"criado_em":"number":true }
    var $vinculos_ordenados { value = $input.vinculos|sort:"id":"number":true|sort:"efetivado_em":"number":true }
    foreach ($ordenados) {
      each as $chamado {
        conditional {
          if (($input.ativos_referencia_id != null && $chamado.ativos_referencia_id != $input.ativos_referencia_id) || ($input.categorias_servico_id != null && $chamado.categorias_servico_id != $input.categorias_servico_id)) {
            continue
          }
        }
        conditional {
          if ($chamado.criado_em == null || $chamado.criado_em <= 0) {
            conditional {
              if ($input.lojas_id == null) {
                var.update $sem_data { value = $sem_data + 1 }
              }
            }
            continue
          }
          elseif ($chamado.criado_em < $input.t0 - 2592000000 || $chamado.criado_em >= $input.observado_ate) {
            continue
          }
        }
        var $no_periodo { value = $chamado.criado_em >= $input.t0 }
        var $categoria { value = $input.categorias|find:$$.id == $chamado.categorias_servico_id }
        var $totem { value = $input.totens|find:$$.id == $chamado.ativos_referencia_id }
        var $vinculos_totem { value = $vinculos_ordenados|filter:$$.ativos_referencia_id == $chamado.ativos_referencia_id }
        function.run "indicadores/loja_no_instante" {
          input = {instante: $chamado.criado_em, vinculos: $vinculos_totem}
        } as $vinculo
        var $loja { value = $input.lojas|find:$$.id == $vinculo.lojas_id }
        var $no_recorte { value = $no_periodo && ($input.lojas_id == null || ($loja != null && $loja.id == $input.lojas_id)) }
        conditional {
          if ($chamado.status == "Cancelado") {
            conditional {
              if ($no_recorte) {
                var.update $cancelados {
                value = $cancelados + 1 }
              }
            }
            continue
          }
          elseif ($categoria == null || $totem == null || ($categoria.tipo_itil != "Incidente" && $categoria.tipo_itil != "Requisição")) {
            conditional {
              if ($no_recorte) {
                var.update $inconsistentes {
                value = $inconsistentes + 1 }
              }
            }
            continue
          }
          elseif ($categoria.tipo_itil == "Requisição") {
            conditional {
              if ($no_recorte) {
                var.update $requisicoes {
                value = $requisicoes + 1 }
              }
            }
            continue
          }
        }

        // Guardar dois instantes distintos evita usar chamados simultâneos como predecessores.
        var $chave { value = ($totem.id|to_text) ~ ":" ~ ($categoria.id|to_text) }
        var $ultimo { value = $ultimos|get:$chave:null }
        var $predecessor { value = null }
        conditional {
          if ($ultimo != null) {
            var.update $predecessor { value = $ultimo.atual < $chamado.criado_em ? $ultimo.atual : $ultimo.anterior }
          }
        }
        var $recorrente { value = $predecessor != null && $chamado.criado_em - $predecessor <= 2592000000 }
        var.update $ultimos { value = $ultimos|set:$chave:{atual: $chamado.criado_em, anterior: $predecessor} }
        conditional {
          if (!$no_recorte) {
            continue
          }
        }

        var.update $elegiveis { value = $elegiveis + 1 }
        conditional {
          if ($recorrente) {
                var.update $recorrentes {
            value = $recorrentes + 1 }
          }
        }
        var $chave_categoria { value = "categoria_" ~ ($categoria.id|to_text) }
        var $grupo_categoria { value = $grupos_categoria|get:$chave_categoria:{id: $categoria.id, nome: $categoria.nome, quantidade: 0} }
        var.update $grupos_categoria { value = $grupos_categoria|set:$chave_categoria:($grupo_categoria|set:"quantidade":($grupo_categoria.quantidade + 1)) }
        var $chave_totem { value = "totem_" ~ ($totem.id|to_text) }
        var $grupo_totem { value = $grupos_totem|get:$chave_totem:{id: $totem.id, nome: $totem.nome, elegiveis: 0, recorrentes: 0} }
        var.update $grupos_totem { value = $grupos_totem|set:$chave_totem:($grupo_totem|set:"elegiveis":($grupo_totem.elegiveis + 1)|set:"recorrentes":($grupo_totem.recorrentes + ($recorrente ? 1 : 0))) }
        conditional {
          if ($loja == null) {
            var.update $sem_loja { value = $sem_loja + 1 }
          }
          else {
            var $chave_loja { value = "loja_" ~ ($loja.id|to_text) }
            var $grupo_loja { value = $grupos_loja|get:$chave_loja:{id: $loja.id, nome: $loja.nome, elegiveis: 0, recorrentes: 0} }
            var.update $grupos_loja { value = $grupos_loja|set:$chave_loja:($grupo_loja|set:"elegiveis":($grupo_loja.elegiveis + 1)|set:"recorrentes":($grupo_loja.recorrentes + ($recorrente ? 1 : 0))) }
          }
        }
      }
    }

    var $por_loja { value = [] }
    var $por_totem { value = [] }
    var $ranking { value = [] }
    // Ordenação explícita: o sort do runtime não garante estabilidade nos empates.
    var $lojas_restantes { value = $grupos_loja|values }
    var $lojas_ordenadas { value = [] }
    while (($lojas_restantes|count) > 0) {
      each {
        var $melhor { value = null }
        foreach ($lojas_restantes) {
          each as $candidato {
            conditional {
              if ($melhor == null || $candidato.elegiveis > $melhor.elegiveis || ($candidato.elegiveis == $melhor.elegiveis && $candidato.id < $melhor.id)) {
                var.update $melhor { value = $candidato }
              }
            }
          }
        }
        array.push $lojas_ordenadas { value = $melhor }
        var.update $lojas_restantes { value = $lojas_restantes|filter:$$.id != $melhor.id }
      }
    }
    foreach ($lojas_ordenadas) {
      each as $grupo {
        array.push $por_loja { value = $grupo|set:"percentual":((100.0 * $grupo.recorrentes / $grupo.elegiveis)|round:2) }
        conditional {
          if (($ranking|count) < 5) {
            array.push $ranking { value = {id: $grupo.id, nome: $grupo.nome, quantidade: $grupo.elegiveis} }
          }
        }
      }
    }
    var $totens_ordenados { value = $grupos_totem|values|sort:"id":"number":true }
    foreach ($totens_ordenados) {
      each as $grupo {
        array.push $por_totem { value = $grupo|set:"percentual":((100.0 * $grupo.recorrentes / $grupo.elegiveis)|round:2) }
      }
    }
    var $pareto { value = [] }
    var $acumulado { value = 0 }
    var $categorias_80 { value = 0 }
    // Ordenação explícita: o sort do runtime não garante estabilidade nos empates.
    var $categorias_restantes { value = $grupos_categoria|values }
    var $categorias_ordenadas { value = [] }
    while (($categorias_restantes|count) > 0) {
      each {
        var $melhor { value = null }
        foreach ($categorias_restantes) {
          each as $candidato {
            conditional {
              if ($melhor == null || $candidato.quantidade > $melhor.quantidade || ($candidato.quantidade == $melhor.quantidade && $candidato.id < $melhor.id)) {
                var.update $melhor { value = $candidato }
              }
            }
          }
        }
        array.push $categorias_ordenadas { value = $melhor }
        var.update $categorias_restantes { value = $categorias_restantes|filter:$$.id != $melhor.id }
      }
    }
    foreach ($categorias_ordenadas) {
      each as $grupo {
        // Comparar contagens inteiras evita que arredondamento altere o corte de 80%.
        var $destaque { value = $acumulado * 100 < $elegiveis * 80 }
        conditional {
          if ($destaque) {
                var.update $categorias_80 {
            value = $categorias_80 + 1 }
          }
        }
        var.update $acumulado { value = $acumulado + $grupo.quantidade }
        array.push $pareto { value = {id: $grupo.id, nome: $grupo.nome, quantidade: $grupo.quantidade, percentual: ((100.0 * $grupo.quantidade / $elegiveis)|round:2), acumulado_percentual: ((100.0 * $acumulado / $elegiveis)|round:2), destaque_80: $destaque} }
      }
    }
    var $percentual { value = null }
    conditional {
      if ($elegiveis > 0) {
                var.update $percentual {
        value = (100.0 * $recorrentes / $elegiveis)|round:2 }
      }
    }
  }

  response = {
    base: {elegiveis: $elegiveis, cancelados: $cancelados, requisicoes: $requisicoes, inconsistentes: $inconsistentes, sem_data: $sem_data, sem_loja: $sem_loja},
    top_lojas: $ranking,
    pareto: {categorias: $pareto, categorias_80: $categorias_80},
    recorrencia: {janela_dias: 30, elegiveis: $elegiveis, recorrentes: $recorrentes, percentual: $percentual, por_loja: $por_loja, por_totem: $por_totem}
  }

  test "causas resumo vazio" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.base.elegiveis) { value = 0 }
    expect.to_equal ($response.top_lojas) { value = [] }
    expect.to_equal ($response.pareto.categorias) { value = [] }
    expect.to_be_null ($response.recorrencia.percentual)
  }

  test "causas recorrencia dois de tres" {
    input = {"t0":1791946800000,"observado_ate":1792206000000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1792033200000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":3,"criado_em":1792119600000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.base.elegiveis) { value = 3 }
    expect.to_equal ($response.recorrencia.recorrentes) { value = 2 }
    expect.to_equal ($response.recorrencia.percentual) { value = 66.67 }
  }

  test "causas predecessor exatamente 30 dias" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1789354800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.recorrencia.recorrentes) { value = 1 }
    expect.to_equal ($response.base.elegiveis) { value = 1 }
  }

  test "causas predecessor fora da janela" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1789354799999,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.recorrencia.recorrentes) { value = 0 }
    expect.to_equal ($response.recorrencia.percentual) { value = 0 }
  }

  test "causas simultaneos sem predecessor" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.recorrencia.recorrentes) { value = 0 }
    expect.to_equal ($response.base.elegiveis) { value = 2 }
  }

  test "causas simultaneos com predecessor" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791860400000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.recorrencia.recorrentes) { value = 2 }
    expect.to_equal ($response.base.elegiveis) { value = 2 }
  }

  test "causas totem e categoria distintos" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791860400000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":2,"ativos_referencia_id":1,"status":"Novo"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":2,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.recorrencia.recorrentes) { value = 0 }
    expect.to_equal ($response.base.elegiveis) { value = 2 }
  }

  test "causas cancelado nao e predecessor" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791860400000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Cancelado"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.recorrencia.recorrentes) { value = 0 }
    expect.to_equal ($response.base.elegiveis) { value = 1 }
  }

  test "causas exclusoes e inativa" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Cancelado"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":5,"ativos_referencia_id":1,"status":"Novo"},{"id":4,"criado_em":1791946800000,"categorias_servico_id":null,"ativos_referencia_id":1,"status":"Novo"},{"id":5,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":null,"status":"Novo"},{"id":6,"criado_em":null,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.base.elegiveis) { value = 1 }
    expect.to_equal ($response.base.cancelados) { value = 1 }
    expect.to_equal ($response.base.requisicoes) { value = 1 }
    expect.to_equal ($response.base.inconsistentes) { value = 2 }
    expect.to_equal ($response.base.sem_data) { value = 1 }
  }

  test "causas transferencia preserva predecessor" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791860400000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000},{"id":7,"ativos_referencia_id":1,"loja_destino_id":2,"efetivado_em":1791946800000}],"lojas_id":2}
    expect.to_equal ($response.base.elegiveis) { value = 1 }
    expect.to_equal ($response.recorrencia.recorrentes) { value = 1 }
    expect.to_equal ($response.top_lojas) { value = [{"id":2,"nome":"Loja 2","quantidade":1}] }
  }

  test "causas transferencia exclui loja antiga" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791860400000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000},{"id":7,"ativos_referencia_id":1,"loja_destino_id":2,"efetivado_em":1791946800000}],"lojas_id":1}
    expect.to_equal ($response.base.elegiveis) { value = 0 }
  }

  test "causas sem loja global" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[]}
    expect.to_equal ($response.base.elegiveis) { value = 1 }
    expect.to_equal ($response.base.sem_loja) { value = 1 }
    expect.to_equal ($response.top_lojas) { value = [] }
  }

  test "causas sem loja filtrada" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[],"lojas_id":1}
    expect.to_equal ($response.base.elegiveis) { value = 0 }
    expect.to_equal ($response.base.sem_loja) { value = 0 }
  }

  test "causas top cinco empate" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":6,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":6,"status":"Novo"},{"id":5,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":5,"status":"Novo"},{"id":4,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":4,"status":"Novo"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":3,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":2,"status":"Novo"},{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.top_lojas) { value = [{"id":1,"nome":"Loja 1","quantidade":1},{"id":2,"nome":"Loja 2","quantidade":1},{"id":3,"nome":"Loja 3","quantidade":1},{"id":4,"nome":"Loja 4","quantidade":1},{"id":5,"nome":"Loja 5","quantidade":1}] }
  }

  test "causas pareto oitenta exato" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":4,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":5,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":6,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":7,"criado_em":1791946800000,"categorias_servico_id":2,"ativos_referencia_id":1,"status":"Novo"},{"id":8,"criado_em":1791946800000,"categorias_servico_id":2,"ativos_referencia_id":1,"status":"Novo"},{"id":9,"criado_em":1791946800000,"categorias_servico_id":3,"ativos_referencia_id":1,"status":"Novo"},{"id":10,"criado_em":1791946800000,"categorias_servico_id":4,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.pareto.categorias_80) { value = 2 }
    expect.to_equal ($response.pareto.categorias) { value = [{"id":1,"nome":"Categoria 1","quantidade":6,"percentual":60,"acumulado_percentual":60,"destaque_80":true},{"id":2,"nome":"Categoria 2","quantidade":2,"percentual":20,"acumulado_percentual":80,"destaque_80":true},{"id":3,"nome":"Categoria 3","quantidade":1,"percentual":10,"acumulado_percentual":90,"destaque_80":false},{"id":4,"nome":"Categoria 4","quantidade":1,"percentual":10,"acumulado_percentual":100,"destaque_80":false}] }
  }

  test "causas pareto cruza oitenta" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":4,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":5,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":6,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":7,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":8,"criado_em":1791946800000,"categorias_servico_id":2,"ativos_referencia_id":1,"status":"Novo"},{"id":9,"criado_em":1791946800000,"categorias_servico_id":2,"ativos_referencia_id":1,"status":"Novo"},{"id":10,"criado_em":1791946800000,"categorias_servico_id":3,"ativos_referencia_id":1,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}]}
    expect.to_equal ($response.pareto.categorias_80) { value = 2 }
  }

  test "causas filtros e corte exclusivo" {
    input = {"t0":1791946800000,"observado_ate":1792033200000,"chamados":[{"id":1,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":2,"criado_em":1792033200000,"categorias_servico_id":1,"ativos_referencia_id":1,"status":"Novo"},{"id":3,"criado_em":1791946800000,"categorias_servico_id":2,"ativos_referencia_id":1,"status":"Novo"},{"id":4,"criado_em":1791946800000,"categorias_servico_id":1,"ativos_referencia_id":2,"status":"Novo"}],"categorias":[{"id":1,"nome":"Categoria 1","tipo_itil":"Incidente","ativo":false},{"id":2,"nome":"Categoria 2","tipo_itil":"Incidente","ativo":false},{"id":3,"nome":"Categoria 3","tipo_itil":"Incidente","ativo":false},{"id":4,"nome":"Categoria 4","tipo_itil":"Incidente","ativo":false},{"id":5,"nome":"Pedido","tipo_itil":"Requisição"}],"totens":[{"id":1,"nome":"Totem 1"},{"id":2,"nome":"Totem 2"},{"id":3,"nome":"Totem 3"},{"id":4,"nome":"Totem 4"},{"id":5,"nome":"Totem 5"},{"id":6,"nome":"Totem 6"}],"lojas":[{"id":1,"nome":"Loja 1"},{"id":2,"nome":"Loja 2"},{"id":3,"nome":"Loja 3"},{"id":4,"nome":"Loja 4"},{"id":5,"nome":"Loja 5"},{"id":6,"nome":"Loja 6"}],"vinculos":[{"id":1,"ativos_referencia_id":1,"loja_destino_id":1,"efetivado_em":1788490800000},{"id":2,"ativos_referencia_id":2,"loja_destino_id":2,"efetivado_em":1788490800000},{"id":3,"ativos_referencia_id":3,"loja_destino_id":3,"efetivado_em":1788490800000},{"id":4,"ativos_referencia_id":4,"loja_destino_id":4,"efetivado_em":1788490800000},{"id":5,"ativos_referencia_id":5,"loja_destino_id":5,"efetivado_em":1788490800000},{"id":6,"ativos_referencia_id":6,"loja_destino_id":6,"efetivado_em":1788490800000}],"categorias_servico_id":1,"ativos_referencia_id":1}
    expect.to_equal ($response.base.elegiveis) { value = 1 }
  }
  guid = "yE7_vXM5Qj5LnWIAK_mNd9ciKqU"
}
