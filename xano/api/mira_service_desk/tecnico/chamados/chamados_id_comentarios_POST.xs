// Comentário operacional independente do Save de tratativa.
query "tecnico/chamados/{chamados_id}/comentarios" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
    text? conteudo? filters=trim
    text visibilidade filters=trim
  }

  stack {
    function.run "service_desk/criar_comentario_operacional" {
      input = {
        usuarios_id: $auth.id
        chamados_id: $input.chamados_id
        conteudo: $input.conteudo
        visibilidade: $input.visibilidade
      }
    } as $resultado
  }

  response = $resultado
  guid = "miraComentarioOperacionalPost01"
}
