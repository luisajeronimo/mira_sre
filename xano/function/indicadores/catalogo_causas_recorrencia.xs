// Opções históricas de Loja, Totem e Categoria para a Diretoria.
function "indicadores/catalogo_causas_recorrencia" {
  input { int usuarios_id { table = "usuarios" } }
  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {"catalogo causas totem sem nome":{"id":4,"role":"diretoria","deve_trocar_senha":false},"catalogo causas diretoria vazia":{"id":4,"role":"diretoria","deve_trocar_senha":false},"catalogo causas gerente negado":{"id":4,"role":"gerente","deve_trocar_senha":false},"catalogo causas tecnico autorizado":{"id":4,"role":"tecnico","deve_trocar_senha":false},"catalogo causas administrador autorizado":{"id":4,"role":"administrador","deve_trocar_senha":false},"catalogo causas troca pendente":{"id":4,"role":"diretoria","deve_trocar_senha":true}}
    } as $diretoria
    precondition (($diretoria.role == "tecnico" || $diretoria.role == "diretoria" || $diretoria.role == "administrador") && $diretoria.deve_trocar_senha == false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    db.query lojas {
      sort = {lojas.id: "asc"}
      return = {type: "list"}
      mock = {
        "catalogo causas diretoria vazia": [],
        "catalogo causas totem sem nome": [],
        "catalogo causas tecnico autorizado": [],
        "catalogo causas administrador autorizado": []
      }
    } as $lojas
    var $lojas_opcoes { value = [] }
    foreach ($lojas) {
      each as $item {
        array.push $lojas_opcoes { value = {id: $item.id, nome: $item.nome} }
      }
    }
    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "catalogo causas diretoria vazia": [],
        "catalogo causas totem sem nome": [{id: 7, nome_ativo: null}],
        "catalogo causas tecnico autorizado": [],
        "catalogo causas administrador autorizado": []
      }
    } as $totens
    var $totens_opcoes { value = [] }
    foreach ($totens) {
      each as $item {
        array.push $totens_opcoes { value = {id: $item.id, nome: $item.nome_ativo|first_notempty:("Totem " ~ ($item.id|to_text))} }
      }
    }
    db.query categorias_servico {
      sort = {categorias_servico.id: "asc"}
      return = {type: "list"}
      mock = {
        "catalogo causas diretoria vazia": [],
        "catalogo causas totem sem nome": [],
        "catalogo causas tecnico autorizado": [],
        "catalogo causas administrador autorizado": []
      }
    } as $categorias
    var $categorias_opcoes { value = [] }
    foreach ($categorias) {
      each as $item {
        array.push $categorias_opcoes { value = {id: $item.id, nome: $item.nome} }
      }
    }
  }
  response = {lojas: $lojas_opcoes, totens: $totens_opcoes, categorias: $categorias_opcoes}

  test "catalogo causas diretoria vazia" {
    input = {"usuarios_id":4}
    expect.to_equal ($response.lojas) { value = [] }
    expect.to_equal ($response.totens) { value = [] }
    expect.to_equal ($response.categorias) { value = [] }
  }

  test "catalogo causas gerente negado" {
    input = {"usuarios_id":4}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "catalogo causas tecnico autorizado" {
    input = {"usuarios_id":4}
    expect.to_equal ($response.lojas) { value = [] }
  }


  test "catalogo causas administrador autorizado" {
    input = {"usuarios_id":4}
    expect.to_equal ($response.lojas) { value = [] }
  }


  test "catalogo causas troca pendente" {
    input = {"usuarios_id":4}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  test "catalogo causas totem sem nome" {
    input = {usuarios_id: 4}
    expect.to_equal ($response.totens) { value = [{id: 7, nome: "Totem 7"}] }
  }
  guid = "TcSPZKFfeGSWUX01fPm1Xwqvyzc"
}
