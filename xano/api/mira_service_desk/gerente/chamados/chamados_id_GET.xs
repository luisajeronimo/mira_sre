// Detalhe funcional de chamado autorizado pela Loja.
query "gerente/chamados/{chamados_id}" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/obter_chamado_gerente" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id}
    } as $resultado
  }

  response = $resultado
  guid = "tj-_a_Dei5XeN0nhiprvgWJ1YC4"
}
