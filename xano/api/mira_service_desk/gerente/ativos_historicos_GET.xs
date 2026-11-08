// Opções de Totem para filtro histórico da fila do Gerente.
query "gerente/ativos-historicos" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
  }

  stack {
    function.run "service_desk/listar_ativos_historicos_gerente" {
      input = {usuarios_id: $auth.id}
    } as $resultado
  }

  response = $resultado
  guid = "miraGerenteAtivosHistoricosGet01"
}