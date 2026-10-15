// Fila global em tabela com filtros simples de atribuição.
query "tecnico/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    text numero? filters=trim
    text status? filters=trim
    text ativo_id? filters=trim
    timestamp data_inicio?
    timestamp data_fim?
  }

  stack {
    function.run "service_desk/listar_chamados_tecnico" {
      input = {usuarios_id: $auth.id, numero: $input.numero, status: $input.status, ativo_id: $input.ativo_id, data_inicio: $input.data_inicio, data_fim: $input.data_fim}
    } as $resultado
  }

  response = $resultado
  guid = "miraFilaTecnicoApi01"
}
