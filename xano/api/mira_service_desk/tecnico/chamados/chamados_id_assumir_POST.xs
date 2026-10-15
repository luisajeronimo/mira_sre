// Comando de assumir, atribuir, reatribuir ou liberar o responsável.
query "tecnico/chamados/{chamados_id}/assumir" verb=POST {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    int chamados_id filters=min:1
    text acao? filters=trim
    int? tecnico_id?
  }

  stack {
    function.run "service_desk/assumir_chamado_tecnico" {
      input = {usuarios_id: $auth.id, chamados_id: $input.chamados_id, acao: $input.acao, tecnico_id: $input.tecnico_id}
    } as $resultado
  }

  response = $resultado
  guid = "miraAssumirTecnicoApi01"
}
