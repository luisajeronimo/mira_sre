// Fila global em tabela com filtros simples de atribuição.
query "tecnico/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    text situacao_atribuicao? filters=trim
    text numero? filters=trim
  }

  stack {
    function.run "service_desk/listar_chamados_tecnico" {
      input = {usuarios_id: $auth.id, situacao_atribuicao: $input.situacao_atribuicao, numero: $input.numero}
    } as $resultado
  }

  response = $resultado
  guid = "miraFilaTecnicoApi01"
}
