// Categorias elegíveis para abertura manual administrativa.
query "administracao/categorias" verb=GET {
  api_group = "MIRA Auth"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $auth.id, administrador: true}
    } as $administrador
    db.query categorias_servico {
      where = $db.categorias_servico.permite_abertura_manual == true && $db.categorias_servico.sla_horas != null
      sort = {categorias_servico.id: "asc"}
      return = {type: "list"}
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
  guid = "admin-categorias-manuais-6ae425c2"
}
