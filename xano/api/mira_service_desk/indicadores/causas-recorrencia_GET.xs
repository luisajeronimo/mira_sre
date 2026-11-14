query "indicadores/causas-recorrencia" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {
    timestamp t0
    timestamp t1
    text? visao?
    int? lojas_id?
    int? ativos_referencia_id?
    int? categorias_servico_id?
  }
  stack {
    function.run "indicadores/consultar_causas_recorrencia" {
      input = {usuarios_id: $auth.id, t0: $input.t0, t1: $input.t1, visao: $input.visao, lojas_id: $input.lojas_id, ativos_referencia_id: $input.ativos_referencia_id, categorias_servico_id: $input.categorias_servico_id}
    } as $dados
  }
  response = $dados
  guid = "hTTa65sBnfAWmjVx83oARe1cDqk"
}
