// Lista funcional de chamados da Loja do Gerente.
query "gerente/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_chamados_gerente" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "6h4T1Nwn7Coht05btWyScvCe-K8"
}
