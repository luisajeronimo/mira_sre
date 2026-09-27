// Abertura manual autorizada de chamado.
query "gerente/chamados" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int ativos_referencia_id?
    int categorias_servico_id?
    text prioridade? filters=trim
    text titulo? filters=trim
    text descricao? filters=trim
  }

  stack {
    function.run "service_desk/abrir_chamado_manual" {
      input = {
        usuarios_id: $auth.id
        ativos_referencia_id: $input.ativos_referencia_id
        categorias_servico_id: $input.categorias_servico_id
        prioridade: $input.prioridade
        titulo: $input.titulo
        descricao: $input.descricao
      }
    } as $resultado

    util.set_header {
      value = "HTTP/1.1 201 Created"
      duplicates = "replace"
    }
  }

  response = $resultado
  guid = "6ypM3o20jzlNXGaxlvecI0nVM54"
}
