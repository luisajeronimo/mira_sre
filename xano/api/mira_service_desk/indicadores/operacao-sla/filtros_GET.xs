// Catálogo de Loja e Categoria para os indicadores de chamados.
query "indicadores/operacao-sla/filtros" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "indicadores/catalogo_operacao_sla" {
      input = {usuarios_id: $auth.id}
    } as $catalogo
  }

  response = $catalogo
  guid = "V_pJUqYliA-hNA-dGsgqJcruMV8"
}
