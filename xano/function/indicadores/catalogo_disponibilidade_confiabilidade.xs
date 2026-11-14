// Catálogo global de filtros do dashboard executivo.
function "indicadores/catalogo_disponibilidade_confiabilidade" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "diretoria consulta catalogo": {id: 4, role: "diretoria", deve_trocar_senha: false}
        "gerente negado": {id: 8, role: "gerente", deve_trocar_senha: false}
        "tecnico autorizado": {id: 3, role: "tecnico", deve_trocar_senha: false}
        "administrador autorizado": {id: 2, role: "administrador", deve_trocar_senha: false}
        "troca pendente negada": {id: 4, role: "diretoria", deve_trocar_senha: true}
      }
    } as $diretoria
    precondition (($diretoria.role == "tecnico" || $diretoria.role == "diretoria" || $diretoria.role == "administrador") && $diretoria.deve_trocar_senha == false) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }

    db.query lojas {
      sort = {lojas.nome: "asc"}
      return = {type: "list"}
      mock = {
        "diretoria consulta catalogo": [{id: 1, nome: "Loja A"}, {id: 2, nome: "Loja B"}],
        "administrador autorizado": [],
        "tecnico autorizado": []
      }
    } as $lojas

    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {
        "diretoria consulta catalogo": [{id: 17, nome_ativo: "Totem transferido", lojas_id: 2}],
        "administrador autorizado": [],
        "tecnico autorizado": []
      }
    } as $ativos

    var $lojas_opcoes { value = [] }
    foreach ($lojas) {
      each as $loja {
        array.push $lojas_opcoes { value = {id: $loja.id, nome: $loja.nome} }
      }
    }

    var $totens_opcoes { value = [] }
    foreach ($ativos) {
      each as $ativo {
        array.push $totens_opcoes { value = {id: $ativo.id, nome: $ativo.nome_ativo|first_notempty:("Totem " ~ ($ativo.id|to_text))} }
      }
    }
  }

  response = {lojas: $lojas_opcoes, totens: $totens_opcoes}

  test "diretoria consulta catalogo" {
    input = {usuarios_id: 4}
    expect.to_equal ($response.lojas) { value = [{id: 1, nome: "Loja A"}, {id: 2, nome: "Loja B"}] }
    expect.to_equal ($response.totens) { value = [{id: 17, nome: "Totem transferido"}] }
  }

  test "gerente negado" {
    input = {usuarios_id: 8}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "tecnico autorizado" {
    input = {usuarios_id: 3}
    expect.to_equal ($response.lojas) { value = [] }
  }


  test "administrador autorizado" {
    input = {usuarios_id: 2}
    expect.to_equal ($response.lojas) { value = [] }
  }


  test "troca pendente negada" {
    input = {usuarios_id: 4}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  guid = "RJhIP9XWCTr0Yp6uaZ4WLpx-3Fc"
}
