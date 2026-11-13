// Disponibilidade, MTTD e MTTR da Diretoria com recortes históricos.
query "indicadores/disponibilidade-confiabilidade" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    timestamp t0
    timestamp t1
    text? visao?
    int? lojas_id?
    int? ativos_referencia_id?
  }

  stack {
    function.run "indicadores/consultar_disponibilidade_confiabilidade" {
      input = {
        usuarios_id: $auth.id,
        t0: $input.t0,
        t1: $input.t1,
        visao: $input.visao,
        lojas_id: $input.lojas_id,
        ativos_referencia_id: $input.ativos_referencia_id
      }
    } as $indicadores
  }

  response = $indicadores
  guid = "R5lUOyZNk6n_rWus2EGzv9iwvyM"
}
