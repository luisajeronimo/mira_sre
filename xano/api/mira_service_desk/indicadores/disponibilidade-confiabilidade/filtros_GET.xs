// Catálogos de Loja e Totem para a Diretoria.
query "indicadores/disponibilidade-confiabilidade/filtros" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {}

  stack {
    function.run "indicadores/catalogo_disponibilidade_confiabilidade" {
      input = {usuarios_id: $auth.id}
    } as $catalogo
  }

  response = $catalogo
  guid = "2CqH7dTLLTGuzGvvULOSLhPKcdA"
}
