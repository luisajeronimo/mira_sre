// Inventário administrativo sem campos internos.
query "administracao/totens" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador
    db.query ativos_referencia {
      sort = {ativos_referencia.id: "asc"}
      return = {type: "list"}
    } as $totens
    var $items {
      value = $totens|map:{
        id: $$.id,
        identificacao: $$.identificacao,
        nome: $$.nome_ativo,
        lojas_id: $$.lojas_id,
        status_atual: $$.status_atual
      }
    }
  }

  response = {items: $items}
  guid = "admin-totens-listar-7d5b9c3f"
}
