// Criação funcional de comentário público pelo Gerente.
query "gerente/chamados/{chamados_id}/comentarios" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
    text conteudo? filters=trim
  }

  stack {
    function.run "service_desk/criar_comentario_publico_gerente" {
      input = {
        usuarios_id: $auth.id
        chamados_id: $input.chamados_id
        conteudo: $input.conteudo
      }
    } as $resultado

    util.set_header {
      value = "HTTP/1.1 201 Created"
      duplicates = "replace"
    }
  }

  response = $resultado
  guid = "miraComentariosGerentePost01"
}
