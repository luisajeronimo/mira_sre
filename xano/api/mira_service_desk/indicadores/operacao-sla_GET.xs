// Volumetria e SLA executivos da Diretoria.
query "indicadores/operacao-sla" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    timestamp t0
    timestamp t1
    text? visao?
    int? lojas_id?
    int? categorias_servico_id?
  }

  stack {
    function.run "indicadores/consultar_operacao_sla" {
      input = {usuarios_id: $auth.id, t0: $input.t0, t1: $input.t1, visao: $input.visao, lojas_id: $input.lojas_id, categorias_servico_id: $input.categorias_servico_id}
    } as $indicadores
  }

  response = $indicadores
  guid = "4svNTYM-Hsgox43eLMtTMeoilA0"
}
