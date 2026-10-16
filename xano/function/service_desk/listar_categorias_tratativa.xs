// Lista categorias ativas disponíveis para a tratativa operacional.
function "service_desk/listar_categorias_tratativa" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "lista categorias ativas para tecnico": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
        "lista categorias ativas para diretoria": ```
          {id: 4, nome: "Diretoria", email: "diretoria@example.test", role: "diretoria", lojas_id: null}
          ```
        "lista categorias ativas para administrador": ```
          {id: 13, nome: "Administradora", email: "admin@example.test", role: "administrador", lojas_id: null}
          ```
        "inclui categoria legada sem ativo materializado": ```
          {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null}
          ```
      }
    } as $usuario

    // A seleção para tratativa exclui somente a Categoria explicitamente
    // inativa. Isso preserva como ativas as categorias legadas que ainda não
    // tenham o valor materializado após a introdução aditiva do campo.
    // A regra de abertura manual e seus filtros de tipo ou SLA não se aplicam.
    db.query categorias_servico {
      where = $db.categorias_servico.ativo == true || $db.categorias_servico.ativo == null
      sort = {categorias_servico.nome: "asc", categorias_servico.id: "asc"}
      return = {type: "list"}
      mock = {
        "lista categorias ativas para tecnico": ```
          [
            {id: 8, nome: "Alta Temperatura", tipo_itil: "Incidente", sla_horas: 2, desc: "Telemetria", permite_abertura_manual: false, ativo: true},
            {id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, desc: "Falha percebida", permite_abertura_manual: true, ativo: null}
          ]
          ```
        "lista categorias ativas para diretoria": ```
          [{id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, desc: "Falha percebida", permite_abertura_manual: true, ativo: true}]
          ```
        "lista categorias ativas para administrador": ```
          [{id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, desc: "Falha percebida", permite_abertura_manual: true, ativo: true}]
          ```
        "inclui categoria legada sem ativo materializado": ```
          [
            {id: 8, nome: "Alta Temperatura", tipo_itil: "Incidente", sla_horas: 2, desc: "Telemetria", permite_abertura_manual: false, ativo: true},
            {id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, desc: "Falha percebida", permite_abertura_manual: true, ativo: null}
          ]
          ```
      }
    } as $categorias

    var $items {
      value = $categorias|map:{
        id: $$.id,
        nome: $$.nome,
        tipo_itil: $$.tipo_itil,
        descricao: $$.desc,
        sla_horas: $$.sla_horas
      }
    }
  }

  response = {items: $items}

  test "lista categorias ativas para tecnico" {
    input = {usuarios_id: 12}
    expect.to_equal ($response.items) {
      value = [
        {id: 8, nome: "Alta Temperatura", tipo_itil: "Incidente", descricao: "Telemetria", sla_horas: 2},
        {id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", descricao: "Falha percebida", sla_horas: 2}
      ]
    }
  }

  test "lista categorias ativas para diretoria" {
    input = {usuarios_id: 4}
    expect.to_equal ($response.items) {
      value = [{id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", descricao: "Falha percebida", sla_horas: 2}]
    }
  }

  test "lista categorias ativas para administrador" {
    input = {usuarios_id: 13}
    expect.to_equal ($response.items) {
      value = [{id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", descricao: "Falha percebida", sla_horas: 2}]
    }
  }
  guid = "miraCategoriasTratativa01"
}
