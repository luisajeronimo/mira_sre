// Consulta funcional de comentários públicos de chamado da Loja do Gerente.
query "gerente/chamados/{chamados_id}/comentarios" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
  }

  stack {
    function.run "service_desk/listar_comentarios_publicos_gerente" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id}
    } as $resultado
  }

  response = $resultado
  guid = "miraComentariosGerenteGet01"
}
