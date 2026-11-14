// Catálogo operacional de abertura; não expõe a Gestão.
function "service_desk/catalogo_abertura_global" {
  input { int usuarios_id { table = "usuarios" } }
  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {"tecnico consulta abertura": {"id": 12, "role": "tecnico", "deve_trocar_senha": false}, "diretoria consulta abertura": {"id": 12, "role": "diretoria", "deve_trocar_senha": false}, "administrador consulta abertura": {"id": 12, "role": "administrador", "deve_trocar_senha": false}, "gerente nao consulta abertura global": {"id": 8, "role": "gerente", "deve_trocar_senha": false}, "troca pendente nao consulta abertura": {"id": 4, "role": "diretoria", "deve_trocar_senha": true}}
    } as $usuario
    precondition (($usuario.role == "tecnico" || $usuario.role == "diretoria" || $usuario.role == "administrador") && $usuario.deve_trocar_senha != true) {
      error_type = "accessdenied"
      error = "Acesso não autorizado."
    }
    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
      mock = {"tecnico consulta abertura": [{"id": 17, "nome_ativo": "Totem global"}], "diretoria consulta abertura": [{"id": 17, "nome_ativo": "Totem global"}], "administrador consulta abertura": [{"id": 17, "nome_ativo": "Totem global"}], "gerente nao consulta abertura global": [{"id": 17, "nome_ativo": "Totem global"}], "troca pendente nao consulta abertura": [{"id": 17, "nome_ativo": "Totem global"}]}
    } as $ativos
    db.query categorias_servico {
      where = $db.categorias_servico.permite_abertura_manual == true && $db.categorias_servico.sla_horas != null
      sort = {categorias_servico.id: "asc"}
      return = {type: "list"}
      mock = {"tecnico consulta abertura": [{"id": 2, "nome": "Rede"}], "diretoria consulta abertura": [{"id": 2, "nome": "Rede"}], "administrador consulta abertura": [{"id": 2, "nome": "Rede"}], "gerente nao consulta abertura global": [{"id": 2, "nome": "Rede"}], "troca pendente nao consulta abertura": [{"id": 2, "nome": "Rede"}]}
    } as $categorias
    var $ativos_opcoes { value = [] }
    foreach ($ativos) {
      each as $ativo {
        array.push $ativos_opcoes { value = {id: $ativo.id, nome: $ativo.nome_ativo|first_notempty:("Totem " ~ ($ativo.id|to_text))} }
      }
    }
    var $categorias_opcoes { value = $categorias|map:{id: $$.id, nome: $$.nome} }
  }
  response = {ativos: $ativos_opcoes, categorias: $categorias_opcoes}

  test "tecnico consulta abertura" {
    input = {"usuarios_id": 12}
    expect.to_equal ($response.ativos) { value = [{id: 17, nome: "Totem global"}] }
  }

  test "diretoria consulta abertura" {
    input = {"usuarios_id": 12}
    expect.to_equal ($response.ativos) { value = [{id: 17, nome: "Totem global"}] }
  }

  test "administrador consulta abertura" {
    input = {"usuarios_id": 12}
    expect.to_equal ($response.ativos) { value = [{id: 17, nome: "Totem global"}] }
  }

  test "gerente nao consulta abertura global" {
    input = {"usuarios_id": 8}
    expect.to_throw { exception = "Acesso não autorizado." }
  }

  test "troca pendente nao consulta abertura" {
    input = {"usuarios_id": 4}
    expect.to_throw { exception = "Acesso não autorizado." }
  }
  guid = "-4c7EXD6MKHwrzir_9bwyhhPCAQ"
}
