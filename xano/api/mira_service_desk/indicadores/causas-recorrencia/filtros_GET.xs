query "indicadores/causas-recorrencia/filtros" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"
  input {

  }
  stack {
    function.run "indicadores/catalogo_causas_recorrencia" {
      input = {usuarios_id: $auth.id}
    } as $dados
  }
  response = $dados
  guid = "FO90fFYqkpBGkYpKDSiP8KRUgpQ"
}
