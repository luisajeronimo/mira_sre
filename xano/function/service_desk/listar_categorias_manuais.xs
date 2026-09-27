// Lista categorias explicitamente liberadas para abertura manual.
function "service_desk/listar_categorias_manuais" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, gerente: true}
      mock = {
        "lista somente categoria manual": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 1}
          ```
        "rejeita gerente sem loja": ```
          {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: null}
          ```
      }
    } as $usuario

    precondition ($usuario.lojas_id != null) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query categorias_servico {
      where = $db.categorias_servico.permite_abertura_manual == true && $db.categorias_servico.sla_horas != null
      sort = {categorias_servico.id: "asc"}
      return = {type: "list"}
      mock = {
        "lista somente categoria manual": ```
          [{id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", sla_horas: 2, desc: "Falha percebida", permite_abertura_manual: true}]
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

  test "lista somente categoria manual" {
    input = {usuarios_id: 8}
    expect.to_equal ($response.items) {
      value = [{id: 2, nome: "Falha de Rede", tipo_itil: "Incidente", descricao: "Falha percebida", sla_horas: 2}]
    }
  }

  test "rejeita gerente sem loja" {
    input = {usuarios_id: 8}
    expect.to_throw { exception = "" }
  }
  guid = "bEWXfmmnwrToL7-U-MjfOz4mLdc"
}
