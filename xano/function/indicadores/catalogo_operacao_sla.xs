// Catálogo gerencial de Loja e Categoria, inclusive categorias históricas inativas.
function "indicadores/catalogo_operacao_sla" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {"catalogo operacao diretoria consulta": {id: 4, role: "diretoria", deve_trocar_senha: false}, "catalogo operacao gerente negado": {id: 8, role: "gerente", deve_trocar_senha: false}, "catalogo operacao tecnico autorizado": {id: 3, role: "tecnico", deve_trocar_senha: false}, "catalogo operacao administrador autorizado": {id: 2, role: "administrador", deve_trocar_senha: false}, "catalogo operacao troca pendente negada": {id: 4, role: "diretoria", deve_trocar_senha: true}}
    } as $diretoria
    precondition (($diretoria.role == "tecnico" || $diretoria.role == "diretoria" || $diretoria.role == "administrador") && $diretoria.deve_trocar_senha == false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query lojas {
      sort = {lojas.nome: "asc"}
      return = {type: "list"}
      mock = {
        "catalogo operacao diretoria consulta": [{id: 1, nome: "Loja A"}],
        "catalogo operacao administrador autorizado": [],
        "catalogo operacao tecnico autorizado": []
      }
    } as $lojas
    db.query categorias_servico {
      sort = {categorias_servico.nome: "asc"}
      return = {type: "list"}
      mock = {
        "catalogo operacao diretoria consulta": [{id: 2, nome: "Falha de Rede"}],
        "catalogo operacao administrador autorizado": [],
        "catalogo operacao tecnico autorizado": []
      }
    } as $categorias
    var $lojas_opcoes { value = [] }
    foreach ($lojas) {
      each as $loja {
        array.push $lojas_opcoes { value = {id: $loja.id, nome: $loja.nome} }
      }
    }
    var $categorias_opcoes { value = [] }
    foreach ($categorias) {
      each as $categoria {
        array.push $categorias_opcoes { value = {id: $categoria.id, nome: $categoria.nome} }
      }
    }
  }

  response = {lojas: $lojas_opcoes, categorias: $categorias_opcoes}

  test "catalogo operacao diretoria consulta" {
    input = {usuarios_id: 4}
    expect.to_equal ($response.lojas) { value = [{id: 1, nome: "Loja A"}] }
    expect.to_equal ($response.categorias) { value = [{id: 2, nome: "Falha de Rede"}] }
  }

  test "catalogo operacao gerente negado" {
    input = {usuarios_id: 8}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  test "catalogo operacao tecnico autorizado" {
    input = {usuarios_id: 3}
    expect.to_equal ($response.lojas) { value = [] }
  }

  test "catalogo operacao administrador autorizado" {
    input = {usuarios_id: 2}
    expect.to_equal ($response.lojas) { value = [] }
  }

  test "catalogo operacao troca pendente negada" {
    input = {usuarios_id: 4}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  guid = "2Fdg_O9UDWnKIVUKRtulvfAc5Yw"
}
